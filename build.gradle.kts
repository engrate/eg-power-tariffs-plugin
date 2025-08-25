plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.kotlin.spring)
    alias(libs.plugins.kotlin.jpa)
    alias(libs.plugins.spring.boot)
    alias(libs.plugins.spring.dependency.management)
    alias(libs.plugins.ktfmt)
    alias(libs.plugins.detekt)
}

group = "io.engrate"

version = "0.0.1-SNAPSHOT"

java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }

repositories { mavenCentral() }

dependencies {
    implementation(libs.spring.boot.starter.web)
    implementation(libs.spring.aop)
    implementation(libs.jackson)
    implementation(libs.kotlin.reflect)
    // DB
    implementation(libs.spring.boot.starter.data.jpa)
    implementation("org.postgresql:postgresql:42.7.3")

    testImplementation(libs.spring.boot.starter.test)
}

ktfmt { kotlinLangStyle() }

detekt { config.setFrom("$projectDir/detekt.yaml") }

tasks.test { useJUnitPlatform() }

tasks.withType<Jar> {
    // Exclude application-dev.yaml from resources in the JAR
    exclude("**/application-dev.yaml")
}
