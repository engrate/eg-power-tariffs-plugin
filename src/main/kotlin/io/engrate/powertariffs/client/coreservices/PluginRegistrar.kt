package io.engrate.powertariffs.client.coreservices

import org.springframework.boot.context.event.ApplicationReadyEvent
import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.context.event.EventListener
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Component
import org.springframework.web.client.HttpClientErrorException
import org.springframework.web.client.RestTemplate
import org.springframework.web.client.postForEntity

@EnableConfigurationProperties(PluginManifest::class)
@Component
class PluginRegistrar(
    pluginRegistrarRestTemplate: RestTemplate,
    private val manifest: PluginManifest,
) {
    private val logger = org.slf4j.LoggerFactory.getLogger(PluginRegistrar::class.java)
    private val restTemplate = pluginRegistrarRestTemplate

    @EventListener(ApplicationReadyEvent::class)
    @Suppress("unused")
    fun registerPlugin() {
        try {
            val response = restTemplate.postForEntity<Any>("/v1/plugins", manifest)
            if (response.statusCode.isSameCodeAs(HttpStatus.CREATED)) {
                logger.info("Successfully registered plugin '${manifest.name}'")
            } else {
                logger.warn(
                    "Failed to register plugin '${manifest.name}': ${response.statusCode} ${response.body}"
                )
            }
        } catch (ex: HttpClientErrorException.Conflict) {
            logger.warn("Plugin '${manifest.name}' is already registered")
            return
        } catch (ex: Exception) {
            logger.error("Failed to register plugin '${manifest.name}': ${ex.message}")
            return
        }
    }
}

@ConfigurationProperties(prefix = "plugin-manifest")
data class PluginManifest(
    val name: String,
    val author: String,
    val description: String? = null,
    val productCategory: String,
    val enabled: Boolean = false,
    val extensions: Map<String, Any> = emptyMap(),
    val pluginMetadata: Map<String, Any>,
)
