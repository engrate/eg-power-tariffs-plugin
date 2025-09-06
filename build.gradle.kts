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
    implementation(libs.bundles.spring)
    implementation(libs.jackson)
    implementation(libs.kotlin.reflect)
    implementation(libs.bundles.db)
    implementation(libs.spring.boot.starter.data.jpa)
    implementation(libs.logstash)
    implementation(libs.bundles.instrumentation)

    testImplementation(libs.spring.boot.starter.test)
}

ktfmt { kotlinLangStyle() }

detekt { config.setFrom("$projectDir/detekt.yaml") }

tasks.test { useJUnitPlatform() }

tasks.withType<Jar> {
    // Exclude application-dev.yaml from resources in the JAR
    exclude("**/application-dev.yaml")
}

tasks.withType<org.springframework.boot.gradle.tasks.bundling.BootJar> {
    archiveBaseName.set("app")
    archiveVersion.set("")
    archiveClassifier.set("")
}
