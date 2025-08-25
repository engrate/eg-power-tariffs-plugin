package io.engrate.powertariffs.api.controller

import io.engrate.powertariffs.api.dto.PowerTariffDto
import io.engrate.powertariffs.api.dto.toDto
import io.engrate.powertariffs.service.PowerTariffsService
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/v1/power-tariffs")
@Suppress("unused")
class PowerTariffsController(private val powerTariffsService: PowerTariffsService) {

    @GetMapping("/postal-code")
    fun getByAddress(@RequestParam code: Int): PowerTariffDto {
        return powerTariffsService.getTariffByPostalCode(postalCode = code).toDto()
    }
}
