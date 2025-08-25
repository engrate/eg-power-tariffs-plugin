package io.engrate.powertariffs.service

import io.engrate.powertariffs.HttpException
import io.engrate.powertariffs.client.elomraden.ElomradenApiClient
import io.engrate.powertariffs.persistence.repository.GridProviderRepository
import io.engrate.powertariffs.persistence.schema.PowerTariff
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Service

@Service
class PowerTariffsService(
    private val elomraden: ElomradenApiClient,
    private val gridProviderRepository: GridProviderRepository,
) {

    fun getTariffByPostalCode(postalCode: Int): PowerTariff {
        val eidelStr =
            elomraden.getPostalCodeInfo(postalCode = postalCode).elnat?.edielId
                ?: throw HttpException(
                    HttpStatus.NOT_FOUND,
                    "EidelId couldn't be resolved for postal code $postalCode",
                )
        val eidel =
            eidelStr.toIntOrNull()
                ?: throw HttpException(HttpStatus.BAD_REQUEST, "Invalid EidelId format: $eidelStr")
        return gridProviderRepository.findByEdiel(eidel)?.powerTariff
            ?: throw HttpException(
                HttpStatus.NOT_FOUND,
                "Grid provider not found for EidelId $eidel",
            )
    }
}
