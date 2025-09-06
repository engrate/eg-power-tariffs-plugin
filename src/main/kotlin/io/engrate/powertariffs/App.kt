package io.engrate.powertariffs

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.stereotype.Component
import org.springframework.web.servlet.config.annotation.ViewControllerRegistry
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer

@SpringBootApplication class App

@Suppress("SpreadOperator")
fun main(args: Array<String>) {
    runApplication<App>(*args)
}

@Component
@Suppress("unused")
class MetricsForwarder : WebMvcConfigurer {
    override fun addViewControllers(registry: ViewControllerRegistry) {
        registry.addRedirectViewController("/metrics", "/actuator/prometheus")
    }
}
