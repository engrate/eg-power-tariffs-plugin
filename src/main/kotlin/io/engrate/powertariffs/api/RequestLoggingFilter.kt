package io.engrate.powertariffs.api

import jakarta.servlet.Filter
import jakarta.servlet.FilterChain
import jakarta.servlet.ServletRequest
import jakarta.servlet.ServletResponse
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component

@Component
class RequestLoggingFilter : Filter {
    private val logger = LoggerFactory.getLogger(RequestLoggingFilter::class.java)

    override fun doFilter(request: ServletRequest, response: ServletResponse, chain: FilterChain) {
        val httpRequest = request as HttpServletRequest
        val httpResponse = response as HttpServletResponse

        val method = httpRequest.method
        val uri = httpRequest.requestURI
        val query = httpRequest.queryString?.let { "?$it" } ?: ""

        chain.doFilter(request, response)

        val status = httpResponse.status

        logger.info("Request: $method $uri$query -> Status: $status")
    }
}
