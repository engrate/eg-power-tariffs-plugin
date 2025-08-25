package io.engrate.powertariffs.api.dto

import io.engrate.powertariffs.persistence.schema.GridProvider
import io.engrate.powertariffs.persistence.schema.PowerTariff
import java.time.ZonedDateTime
import java.util.UUID

data class PowerTariffDto(
    val uid: UUID,
    val provider: GridProviderDto,
    val countryCode: String,
    val timeZone: String,
    val lastUpdated: ZonedDateTime,
    val validFrom: ZonedDateTime,
    val validTo: ZonedDateTime,
)

data class GridProviderDto(
    val uid: String,
    val name: String,
    val ediel: Int,
    val orgNumber: String,
)

fun PowerTariff.toDto(): PowerTariffDto {
    return PowerTariffDto(
        uid = uid,
        provider = provider.toDto(),
        countryCode = countryCode,
        timeZone = timeZone,
        lastUpdated = lastUpdated,
        validFrom = validFrom,
        validTo = validTo,
    )
}

fun GridProvider.toDto(): GridProviderDto {
    return GridProviderDto(uid = uid.toString(), name = name, ediel = ediel, orgNumber = orgNumber)
}
