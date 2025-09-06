package io.engrate.powertariffs.api.controller

import io.engrate.powertariffs.api.PowerTariffDto
import io.engrate.powertariffs.api.toDto
import io.engrate.powertariffs.service.PowerTariffsService
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/power-tariffs")
@Suppress("unused")
@Transactional
class PowerTariffsController(private val tariffsService: PowerTariffsService) {
    @GetMapping("/{countryCode}/mga/{mgaCode}")
    fun getByMeteringGridArea(
        @PathVariable countryCode: String,
        @PathVariable mgaCode: String,
    ): List<PowerTariffDto> {
        return tariffsService.getByMeteringGridArea(countryCode, mgaCode).map { it.toDto() }
    }

    @GetMapping("/{countryCode}/lat/{lat}/long/{long}")
    fun getByCoordinates(
        @PathVariable countryCode: String,
        @PathVariable lat: Double,
        @PathVariable long: Double,
    ): List<PowerTariffDto> {
        return tariffsService.getByCoordinates(countryCode, lat, long).map { it.toDto() }
    }

    @GetMapping("/{countryCode}/address/{address}/city/{city}")
    fun getByAddress(
        @PathVariable countryCode: String,
        @PathVariable address: String,
        @PathVariable city: String,
    ): List<PowerTariffDto> {
        return tariffsService.getByAddress(countryCode, address, city).map { it.toDto() }
    }

    @GetMapping("/{countryCode}/postal-code/{postalCode}")
    fun getByPostalCode(
        @PathVariable countryCode: String,
        @PathVariable postalCode: Int,
    ): List<PowerTariffDto> {
        return tariffsService.getByPostalCode(countryCode, postalCode).map { it.toDto() }
    }
}
