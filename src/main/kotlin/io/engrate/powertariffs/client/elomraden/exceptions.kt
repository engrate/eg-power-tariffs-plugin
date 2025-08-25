package io.engrate.powertariffs.client.elomraden

import io.engrate.powertariffs.HttpException
import org.springframework.http.HttpStatus

class NotEnabledException(error: Error) :
    HttpException(HttpStatus.NOT_FOUND, "API method or operation not enabled", error)

class UnknownException(error: Error) :
    HttpException(HttpStatus.INTERNAL_SERVER_ERROR, "Unknown error", error)

class MissingAreaException(searchParameter: String, error: Error) :
    HttpException(HttpStatus.NOT_FOUND, "Area not found for: $searchParameter", error)

class WrongArgumentException(error: Error) :
    HttpException(HttpStatus.BAD_REQUEST, "Wrong Argument", error)
