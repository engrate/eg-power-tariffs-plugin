package io.engrate.powertariffs.config

import com.fasterxml.jackson.databind.PropertyNamingStrategies
import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.boot.web.client.RestTemplateBuilder
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.http.converter.json.Jackson2ObjectMapperBuilder
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter
import org.springframework.web.client.RestTemplate

@ConfigurationProperties(prefix = "elomraden")
data class ElomradenProperties(val user: String, val apikey: String, val baseUrl: String)

@ConfigurationProperties(prefix = "plugin-registrar")
data class PluginRegistrarProperties(val url: String) {}

@Suppress("unused")
@Configuration
@EnableConfigurationProperties(ElomradenProperties::class, PluginRegistrarProperties::class)
class RestTemplateConfig {
    @Bean
    fun elomradenRestTemplate(
        builder: RestTemplateBuilder,
        objectMapperBuilder: Jackson2ObjectMapperBuilder,
        elomradenProperties: ElomradenProperties,
    ): RestTemplate =
        builder
            .rootUri(elomradenProperties.baseUrl)
            .messageConverters(
                MappingJackson2HttpMessageConverter(
                    objectMapperBuilder
                        .propertyNamingStrategy(PropertyNamingStrategies.LOWER_CAMEL_CASE)
                        .build()
                )
            )
            .build()

    @Bean
    fun pluginRegistrarRestTemplate(
        builder: RestTemplateBuilder,
        objectMapperBuilder: Jackson2ObjectMapperBuilder,
        registrarProperties: PluginRegistrarProperties,
    ): RestTemplate =
        builder
            .rootUri(registrarProperties.url)
            .messageConverters(
                MappingJackson2HttpMessageConverter(
                    objectMapperBuilder
                        .propertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE)
                        .build()
                )
            )
            .build()
}
