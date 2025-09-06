package io.engrate.powertariffs.service

import io.engrate.powertariffs.client.elomraden.ElomradenApiClient
import io.engrate.powertariffs.persistence.repository.PowerTariffsRepository
import io.engrate.powertariffs.persistence.schema.PowerTariff
import org.springframework.stereotype.Service

@Service
class PowerTariffsService(
    private val elomraden: ElomradenApiClient,
    private val tariffsRepo: PowerTariffsRepository,
) {
    fun getByMeteringGridArea(countryCode: String, mgaCode: String): List<PowerTariff> {
        return tariffsRepo.findPowerTariffsByMga(countryCode, mgaCode)
    }

    fun getByCoordinates(countryCode: String, lat: Double, long: Double): List<PowerTariff> {
        val mgaCode = elomraden.getByCoordinates(lat = lat, long = long).natomradeBeteckning
        return tariffsRepo.findPowerTariffsByMga(countryCode = countryCode, mgaCode = mgaCode)
    }

    fun getByAddress(countryCode: String, address: String, city: String): List<PowerTariff> {
        val mgaCode = elomraden.getByAddress(street = address, city = city).natomradeBeteckning
        return tariffsRepo.findPowerTariffsByMga(countryCode = countryCode, mgaCode = mgaCode)
    }

    fun getByPostalCode(countryCode: String, postalCode: Int): List<PowerTariff> {
        val mgaCode = elomraden.getByPostalCode(code = postalCode).natomradeBeteckning
        return tariffsRepo.findPowerTariffsByMga(countryCode = countryCode, mgaCode = mgaCode)
    }
}
