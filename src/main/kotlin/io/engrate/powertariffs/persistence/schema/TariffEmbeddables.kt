package io.engrate.powertariffs.persistence.schema

import jakarta.persistence.Column
import jakarta.persistence.Embeddable

@Embeddable
data class IntervalEntry(
    @Column(name = "from_time", length = 10, nullable = false) val from: String = "",
    @Column(name = "to_time", length = 10, nullable = false) val to: String = "",
    @Column(name = "multiplier", nullable = false) val multiplier: Double = 1.0,
)

@Embeddable
data class HintEntry(
    @Column(name = "hint_type", length = 50, nullable = false) val type: String = "",
    @Column(name = "hint_value", length = 255, nullable = false) val value: String = "",
)
