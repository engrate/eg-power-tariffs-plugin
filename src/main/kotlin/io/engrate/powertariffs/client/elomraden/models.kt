package io.engrate.powertariffs.client.elomraden

import com.fasterxml.jackson.annotation.JsonProperty

data class PostalNumberResponse(val natomradePostnummer: PostalNumberResponseData)

data class PostalNumberResponseData(
    val success: Int,
    val error: Error? = null,
    val item: List<PostalNumber> = emptyList(),
)

data class PostalNumber(val elnat: ElnatData? = null, val geografi: GeografiData? = null)

data class ElnatData(
    val natomradeNamn: String? = null,
    val natomradeBeteckning: String? = null,
    val elomrade: Int? = null,
    val natagare: String? = null,
    @field:JsonProperty("EdielID") val edielId: String? = null,
    val epost: String? = null,
    val telefon: String? = null,
)

data class GeografiData(
    val kommun: String? = null,
    val elskatt: Boolean? = null,
    val elskattNamn: String? = null,
    val ort: String? = null,
)

data class Error(val errorCode: Int, val errorString: String)
