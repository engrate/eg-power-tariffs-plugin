package io.engrate.powertariffs.importers

import io.engrate.powertariffs.persistence.repository.GridOperatorsRepository
import io.engrate.powertariffs.persistence.schema.GridOperator
import jakarta.transaction.Transactional
import org.slf4j.LoggerFactory
import org.springframework.boot.ApplicationRunner
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.core.annotation.Order
import org.springframework.core.io.ClassPathResource
import org.springframework.stereotype.Component

@Order(1)
@Component
@Transactional
@EnableConfigurationProperties(ImportersProperties::class)
class OperatorsImporter(
    private val repository: GridOperatorsRepository,
    private val props: ImportersProperties,
) : ApplicationRunner {
    private val logger = LoggerFactory.getLogger(OperatorsImporter::class.java)

    override fun run(args: org.springframework.boot.ApplicationArguments?) {
        if (!props.loadGridOperators) {
            logger.info("Skipping operator definitions import")
            return
        }
        val csvPath = "data/operators/operators.csv"
        val resource = ClassPathResource(csvPath)
        if (!resource.exists()) {
            logger.error("Operators CSV file not found at: $csvPath")
            return
        }

        resource.inputStream.bufferedReader(Charsets.UTF_8).use { reader ->
            val lines = reader.readLines()
            if (lines.isEmpty()) {
                logger.warn("Operator CSV is empty: $csvPath")
                return@use
            }

            val rows = lines.drop(1) // Skip header
            for (line in rows) {
                val row = line.split(";")
                if (row.size < 2) {
                    logger.warn("Skipping malformed row: $row")
                    continue
                }
                val name = row[0].trim()
                val edielIdStr = row[1].trim()
                val edielId = edielIdStr.toIntOrNull()
                if (edielId == null) {
                    logger.warn("Skipping row with invalid Ediel ID: $row")
                    continue
                }

                val existingOperator = repository.findByEdiel(edielId)
                if (existingOperator != null) {
                    logger.warn("Operator $name already exists, skipping")
                    continue
                }

                val gridOperator =
                    GridOperator(name = name, ediel = edielId, meteringGridAreas = emptySet())

                repository.save(gridOperator)
                logger.info("Created grid operator: $name (Ediel: $edielId)")
            }
        }
    }
}
