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

    fun getPostalCodeInfo(postalCode: Int): PostalNumber {
        val url = "/postnr/postnummer/$postalCode/output/json/user/$user/key/$apikey"
        val response =
            restTemplate.getForObject(url, PostalNumberResponse::class.java)?.natomradePostnummer
                ?: error("Error parsing Elomraden API response")

        throwIfError(response.success, response.error, postalCode.toString())
        return response.item.firstOrNull()
            ?: throw HttpException(
                HttpStatus.NOT_FOUND,
                "No data found for postal code $postalCode",
            )
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
