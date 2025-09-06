package io.engrate.powertariffs.client.elomraden

import io.engrate.powertariffs.HttpException
import io.engrate.powertariffs.config.ElomradenProperties
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Service
import org.springframework.web.client.RestTemplate

@Service
class ElomradenApiClient(elomradenRestTemplate: RestTemplate, properties: ElomradenProperties) {

    private val restTemplate = elomradenRestTemplate
    private val user = properties.user
    private val apikey = properties.apikey

    fun getByCoordinates(lat: Double, long: Double): ElnatData {
        val url = "/koord/latitud/$lat/longitud/$long/output/json/user/{user}/key/{apikey}"
        val response =
            restTemplate
                .getForObject(url, ByCoordinatesResponse::class.java, user, apikey)
                ?.elomradeAdress ?: error("Error parsing Elomraden API response")

        throwIfError(response.success, response.error, "$lat, $long")
        return response.elnat
            ?: throw HttpException(
                HttpStatus.NOT_FOUND,
                "No data found for coordinates $lat, $long",
            )
    }

    fun getByAddress(street: String, city: String): ElnatData {
        val url = "/adress/adress/$street/ort/$city/output/json/user/{user}/key/{apikey}"
        val response =
            restTemplate
                .getForObject(url, ByAddressResponse::class.java, user, apikey)
                ?.elomradeAdress ?: error("Error parsing Elomraden API response")

        throwIfError(response.success, response.error, "$street, $city")
        return response.elnat
            ?: throw HttpException(HttpStatus.NOT_FOUND, "No data found for address $street, $city")
    }

    fun getByPostalCode(code: Int): ElnatData {
        val url = "/postnr/postnummer/$code/output/json/user/{user}/key/{apikey}"
        val response =
            restTemplate
                .getForObject(url, ByPostalCodeResponse::class.java, user, apikey)
                ?.natomradePostnummer ?: error("Error parsing Elomraden API response")

        throwIfError(response.success, response.error, code.toString())
        return response.item.firstOrNull()?.elnat
            ?: throw HttpException(HttpStatus.NOT_FOUND, "No data found for postal code $code")
    }

    private fun throwIfError(success: Int, error: Error?, arg: String) {
        if (success == 1) return
        val error = error ?: Error(0, "Unknown error")

        when (error.errorCode) {
            1 -> throw WrongArgumentException(error)
            2 -> throw MissingAreaException(arg, error)
            90 -> throw NotEnabledException(error)
            99 -> throw UnknownException(error)
            else -> throw UnknownException(error)
        }
    }
}
