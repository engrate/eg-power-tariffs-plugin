package io.engrate.powertariffs

import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatusCode
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice
import org.springframework.web.client.HttpStatusCodeException

open class HttpException(status: HttpStatusCode, msg: String, val body: Any? = null) :
    HttpStatusCodeException(status, msg)

@RestControllerAdvice
@Suppress("unused")
class HttpExceptionHandler {
    private val logger = LoggerFactory.getLogger(HttpExceptionHandler::class.java)

    @ExceptionHandler(HttpException::class)
    fun handleHttpException(ex: HttpException): ResponseEntity<Any> {
        logger.error(
            "Handled HttpException: status={}, message={}, body={}",
            ex.statusCode,
            ex.message,
            ex.body,
            ex,
        )

        return ResponseEntity.status(ex.statusCode).body(ex.body ?: ex.message)
    }
}
