package io.engrate.powertariffs.importers

import org.springframework.boot.context.properties.ConfigurationProperties

@ConfigurationProperties(prefix = "data-importer")
data class ImportersProperties(
    val loadTariffsDefinitions: Boolean,
    val loadMeteringGridAreas: Boolean,
    val loadGridOperators: Boolean,
) {}
