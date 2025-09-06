package io.engrate.powertariffs.importers

import io.engrate.powertariffs.persistence.repository.GridOperatorsRepository
import io.engrate.powertariffs.persistence.repository.MeteringGridAreasRepository
import io.engrate.powertariffs.persistence.schema.MeteringGridArea
import jakarta.transaction.Transactional
import org.slf4j.LoggerFactory
import org.springframework.boot.ApplicationRunner
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.core.annotation.Order
import org.springframework.core.io.ClassPathResource
import org.springframework.stereotype.Component

@Order(2)
@Component
@Transactional
@EnableConfigurationProperties(ImportersProperties::class)
class MeteringGridAreasImporter(
    private val meteringGridAreaRepository: MeteringGridAreasRepository,
    private val gridOperatorsRepository: GridOperatorsRepository,
    private val props: ImportersProperties,
) : ApplicationRunner {
    private val logger = LoggerFactory.getLogger(MeteringGridAreasImporter::class.java)

    override fun run(args: org.springframework.boot.ApplicationArguments?) {
        if (!props.loadMeteringGridAreas) {
            logger.info("Skipping metering grid areas import")
            return
        }
        val csvPath = "data/metering_grid_areas/mgas.csv"
        val resource = ClassPathResource(csvPath)
        if (!resource.exists()) {
            logger.error("Metering grid areas CSV file not found at: $csvPath")
            return
        }

        resource.inputStream.bufferedReader(Charsets.UTF_8).use { reader ->
            val lines = reader.readLines()
            if (lines.isEmpty()) {
                logger.warn("Metering grid areas CSV is empty: $csvPath")
                return@use
            }

            val rows = lines.drop(1) // No header check, skip first line
            for (rowLine in rows) {
                val row = rowLine.split(";")
                if (row.size < 6) {
                    logger.warn("Skipping malformed row: $row")
                    continue
                }

                val operatorName = row[0].trim()
                val mgaName = row[1].trim()
                val mgaCode = row[2].trim()
                val mgaType = row[3].trim()
                val mbaCode = row[4].trim()
                val country = row[5].trim()

                if (!mgaType.contains("DISTRIBUTION", ignoreCase = true)) {
                    logger.warn("Skipping $mgaName - only DISTRIBUTION types are supported")
                    continue
                }

                val operator = gridOperatorsRepository.findByName(operatorName)
                if (operator == null) {
                    logger.warn("Operator $operatorName does not exist, skipping")
                    continue
                }

                val existingMga = meteringGridAreaRepository.findByCode(mgaCode)
                if (existingMga != null) {
                    logger.warn("Metering grid area $mgaCode already exists, skipping")
                    continue
                }

                val mga =
                    MeteringGridArea(
                        code = mgaCode,
                        name = mgaName,
                        countryCode = country,
                        meteringBusinessArea = mbaCode,
                        gridOperator = operator,
                        tariffAssociations = emptySet(),
                    )

                meteringGridAreaRepository.save(mga)
                logger.info("Metering grid area saved: $mgaName (Code: $mgaCode)")
            }
        }
    }
}
