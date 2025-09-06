package io.engrate.powertariffs.importers

import io.engrate.powertariffs.persistence.repository.GridOperatorsRepository
import io.engrate.powertariffs.persistence.repository.MeteringGridAreasPowerTariffsRepository
import io.engrate.powertariffs.persistence.repository.PowerTariffsRepository
import io.engrate.powertariffs.persistence.schema.DaysEnum
import io.engrate.powertariffs.persistence.schema.GridOperator
import io.engrate.powertariffs.persistence.schema.MeteringGridAreaPowerTariff
import io.engrate.powertariffs.persistence.schema.MonthEnum
import io.engrate.powertariffs.persistence.schema.PowerTariff
import io.engrate.powertariffs.persistence.schema.TariffComposition
import io.engrate.powertariffs.persistence.schema.TimeInterval
import jakarta.transaction.Transactional
import java.time.ZonedDateTime
import java.util.Locale
import org.slf4j.LoggerFactory
import org.springframework.boot.ApplicationRunner
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.core.annotation.Order
import org.springframework.core.io.ClassPathResource
import org.springframework.stereotype.Component

@Order(3)
@Component
@Transactional
@EnableConfigurationProperties(ImportersProperties::class)
class PowerTariffsImporter(
    private val gridOperatorsRepository: GridOperatorsRepository,
    private val meteringGridAreasPowerTariffsRepository: MeteringGridAreasPowerTariffsRepository,
    private val powerTariffRepository: PowerTariffsRepository,
    private val props: ImportersProperties,
) : ApplicationRunner {

    private val logger = LoggerFactory.getLogger(PowerTariffsImporter::class.java)

    override fun run(args: org.springframework.boot.ApplicationArguments?) {
        if (!props.loadTariffsDefinitions) {
            logger.info("Skipping tariff definitions import")
            return
        }
        val operatorsByEdiel = parseTariffsHeaders()
        val compositionsByTariffId = parseTariffsCompositions()

        // Map compositions into matching PowerTariff
        for ((tariffId, compositions) in compositionsByTariffId) {
            val pt = findTariffById(operatorsByEdiel, tariffId)
            if (pt == null) {
                logger.error("Operator not found for tariff ID: $tariffId")
                continue
            }
            pt.compositions.addAll(compositions)
        }

        // For each operator, save tariffs if not already present
        for ((ediel, operatorTariffs) in operatorsByEdiel) {
            val op = gridOperatorsRepository.findByEdiel(ediel)
            if (op == null) {
                logger.warn("Skipping power tariff: Operator $ediel not found")
                continue
            }
            if (op.meteringGridAreas.isEmpty()) {
                logger.warn("Skipping power tariff: No MGAs for $ediel")
                continue
            }
            val alreadyHasTariffs =
                op.meteringGridAreas.any { mga -> mga.tariffAssociations.isNotEmpty() }
            if (alreadyHasTariffs) {
                logger.warn("Operator $ediel already has tariffs, skipping.")
                continue
            }
            operatorTariffs.powerTariffs.forEach { pt -> saveOperatorTariff(op, pt) }
        }
    }

    data class PTariff(
        val tariffId: String,
        val name: String,
        val model: String,
        val description: String,
        val samplesPerMonth: Int,
        val timeUnit: String,
        val buildingType: String,
        val compositions: MutableList<TariffComposition> = mutableListOf(),
    )

    data class POperator(val ediel: Int, val powerTariffs: MutableList<PTariff>)

    private fun parseTariffsHeaders(): MutableMap<Int, POperator> {
        val result = mutableMapOf<Int, POperator>()
        val resource = ClassPathResource("data/power_tariffs/tariffs_headers.csv")
        if (!resource.exists()) {
            logger.error("Tariffs headers CSV not found")
            return result
        }
        resource.inputStream.bufferedReader(Charsets.UTF_8).use { reader ->
            val rows = reader.readLines()
            if (rows.isEmpty()) return result
            val headers = rows.first().split(",")
            val idx = { name: String -> headers.indexOf(name) }
            for (line in rows.drop(1)) {
                val row = line.split(",")
                if (row.size < headers.size) continue
                val ediel = row[idx("Provider Ediel")].toInt()
                val operator = result.getOrPut(ediel) { POperator(ediel, mutableListOf()) }
                val tariff =
                    PTariff(
                        tariffId = row[idx("Tariff ID")],
                        name = row[idx("Name")],
                        model = row[idx("Model Name")],
                        description = row[idx("Description")],
                        samplesPerMonth = row[idx("Number of samples")].toInt(),
                        timeUnit = row[idx("Time unit")],
                        buildingType = parseBuildingType(row[idx("Building types")]),
                    )
                operator.powerTariffs.add(tariff)
            }
        }
        return result
    }

    private fun parseTariffsCompositions(): Map<String, List<TariffComposition>> {
        val result = mutableMapOf<String, MutableList<TariffComposition>>()
        val resource = ClassPathResource("data/power_tariffs/tariffs_compositions.csv")
        if (!resource.exists()) {
            logger.error("Tariffs compositions CSV not found")
            return result
        }
        resource.inputStream.bufferedReader(Charsets.UTF_8).use { reader ->
            val rows = reader.readLines()
            if (rows.isEmpty()) return result
            val headers = rows.first().split(",")
            val idx = { name: String -> headers.indexOf(name) }
            for (line in rows.drop(1)) {
                val row = line.split(Regex(""",(?=(?:[^"]*"[^"]*")*[^"]*$)"""))
                if (row.size < headers.size) continue
                try {
                    val tariffId = row[idx("Fee ID")]
                    val comp =
                        TariffComposition(
                            months = parseMonths(row[idx("Months Number")]),
                            days = parseDays(row[idx("Days")]),
                            fuseFrom = parseFuse(row[idx("Fuse From")]),
                            fuseTo = parseFuse(row[idx("Fuse To")]),
                            unit = row[idx("Unit")],
                            priceExcVat = parsePrice(row[idx("Price Ex Vat")]),
                            priceIncVat = parsePrice(row[idx("Price Inc Vat")]),
                            intervals = parseIntervals(row, idx),
                        )
                    val list = result.getOrPut(tariffId) { mutableListOf() }
                    list.add(comp)
                } catch (ex: Exception) {
                    logger.error("Error parsing fee ${row.getOrNull(idx("Fee ID"))}: $ex")
                }
            }
        }
        return result
    }

    private fun parseIntervals(row: List<String>, idx: (String) -> Int): List<TimeInterval> {
        val from1 = row[idx("From")]
        val to1 = if (row[idx("To")] == "0:00") "24:00" else row[idx("To")]
        val multiplier1 = row[idx("Multiplier")].toDouble()
        val intervals = mutableListOf(TimeInterval(from1, to1, multiplier1))
        val from2 = row[idx("From2")]
        if (from2.isNotBlank()) {
            val to2 = if (row[idx("To2")] == "0:00") "24:00" else row[idx("To2")]
            val multiplier2 = row[idx("Multiplier2")].toDouble()
            intervals.add(TimeInterval(from2, to2, multiplier2))
        }
        return intervals
    }

    private fun parseBuildingType(value: String?): String {
        val s = value?.lowercase(Locale.getDefault()) ?: return "ALL"
        val hasHouse = "_house" in s
        val hasApartments = "apartments" in s
        return when {
            hasHouse && hasApartments -> "ALL"
            hasHouse -> "HOUSE"
            hasApartments -> "APARTMENT"
            else -> "ALL"
        }
    }

    private fun parseMonths(value: String?): List<MonthEnum> {
        val value = if (value == null || value.isEmpty()) "1,2,3,4,5,6,7,8,9,10,11,12" else value
        val months = value.split(",").map { it.trim() }
        return months.mapNotNull { num ->
            when (num) {
                "1" -> MonthEnum.JANUARY
                "2" -> MonthEnum.FEBRUARY
                "3" -> MonthEnum.MARCH
                "4" -> MonthEnum.APRIL
                "5" -> MonthEnum.MAY
                "6" -> MonthEnum.JUNE
                "7" -> MonthEnum.JULY
                "8" -> MonthEnum.AUGUST
                "9" -> MonthEnum.SEPTEMBER
                "10" -> MonthEnum.OCTOBER
                "11" -> MonthEnum.NOVEMBER
                "12" -> MonthEnum.DECEMBER
                else -> null
            }
        }
    }

    private fun parseDays(value: String?): List<DaysEnum> {
        val value = if (value == null || value.isEmpty()) "M,T,W,T,F,S,S" else value
        val s = value.replace("\\s+".toRegex(), "")
        val days = mutableListOf<DaysEnum>()
        if (s.contains("M,T,W,T,F")) {
            days +=
                listOf(
                    DaysEnum.MONDAY,
                    DaysEnum.TUESDAY,
                    DaysEnum.WEDNESDAY,
                    DaysEnum.THURSDAY,
                    DaysEnum.FRIDAY,
                )
        }
        if (s.contains("S,S")) {
            days += listOf(DaysEnum.SATURDAY, DaysEnum.SUNDAY)
        }
        return days.ifEmpty { DaysEnum.values().toList() }
    }

    private fun parseFuse(value: String?): String {
        return value?.takeIf { Regex("\\d+A").matches(it) }
            ?: throw IllegalArgumentException("Invalid fuse format $value")
    }

    private fun parsePrice(value: String?): Double {
        return value?.toDoubleOrNull()
            ?: throw IllegalArgumentException("Invalid price format $value")
    }

    private fun findTariffById(ops: Map<Int, POperator>, tariffId: String): PTariff? {
        for (op in ops.values) {
            val tariff = op.powerTariffs.find { it.tariffId == tariffId }
            if (tariff != null) return tariff
        }
        return null
    }

    private fun saveOperatorTariff(operator: GridOperator, tariff: PTariff) {
        if (tariff.compositions.isEmpty()) {
            logger.warn("No tariffs composition for ${tariff.name} EDIEL ${operator.ediel}")
        }
        val now = ZonedDateTime.now()
        val entity =
            PowerTariff(
                name = tariff.name,
                model = tariff.model,
                description = tariff.description,
                samplesPerMonth = tariff.samplesPerMonth,
                timeUnit = tariff.timeUnit,
                buildingType = tariff.buildingType,
                lastUpdated = now,
                validFrom = null,
                validTo = null,
                voltage = "LV",
                compositions = tariff.compositions,
                areaAssociations = mutableSetOf(),
            )

        val savedTariff = powerTariffRepository.saveAndFlush(entity)
        meteringGridAreasPowerTariffsRepository.saveAll(
            operator.meteringGridAreas.map { mga ->
                MeteringGridAreaPowerTariff(meteringGridArea = mga, powerTariff = savedTariff)
            }
        )

        logger.info("Saved power tariff: ${tariff.name} for operator ${operator.name}")
    }
}
