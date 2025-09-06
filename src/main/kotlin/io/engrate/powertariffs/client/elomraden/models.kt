package io.engrate.powertariffs.client.elomraden

import com.fasterxml.jackson.annotation.JsonProperty

data class Error(val errorCode: Int, val errorString: String)

data class ByCoordinatesResponse(val elomradeAdress: ElomradeAddress)

data class ByAddressResponse(val elomradeAdress: ElomradeAddress)

data class ByPostalCodeResponse(val natomradePostnummer: NatomradePostnummer)

data class ElomradeAddress(val success: Int, val error: Error?, val elnat: ElnatData?)

data class NatomradePostnummer(
    val success: Int,
    val error: Error?,
    val item: List<NatomradePostNummerItem> = emptyList(),
)

data class NatomradePostNummerItem(val elnat: ElnatData)

data class ElnatData(
    val natomradeBeteckning: String,
    @field:JsonProperty("EdielID") val edielId: String,
)
