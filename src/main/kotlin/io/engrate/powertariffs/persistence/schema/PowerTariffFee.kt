package io.engrate.powertariffs.persistence.schema

import jakarta.persistence.*
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes

@Entity
@Table(name = "power_tariff_fees")
data class PowerTariffFee(
    @Id
    @Column(name = "uid", nullable = false, unique = true)
    val uid: java.util.UUID = java.util.UUID.randomUUID(),
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "tariff_uid", nullable = false)
    val tariff: PowerTariff,
    @Column(name = "name", length = 255, nullable = false) val name: String,
    @Column(name = "model", length = 50, nullable = false) val model: String,
    @Column(name = "description") val description: String? = null,
    @Column(name = "samples_per_month", nullable = false) val samplesPerMonth: Int,
    @Column(name = "time_unit", length = 20, nullable = false) val timeUnit: String,
    @JdbcTypeCode(SqlTypes.ARRAY)
    @Column(name = "building_types", columnDefinition = "text[]")
    val buildingTypes: List<String> = emptyList(),
    @OneToMany(
        mappedBy = "fee",
        cascade = [CascadeType.ALL],
        orphanRemoval = true,
        fetch = FetchType.LAZY,
    )
    val compositions: MutableList<TariffComposition> = mutableListOf(),
)
