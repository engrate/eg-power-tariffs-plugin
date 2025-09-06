package io.engrate.powertariffs.persistence.schema

import jakarta.persistence.*

@Entity
@Table(name = "metering_grid_areas")
class MeteringGridArea(
    @Id @Column(name = "code", nullable = false, length = 5) val code: String,
    @Column(name = "name", nullable = false, unique = true, length = 255) val name: String,
    @Column(name = "country_code", nullable = false, length = 2) val countryCode: String,
    @Column(name = "metering_business_area", nullable = false, length = 5)
    val meteringBusinessArea: String,
    @ManyToOne @JoinColumn(name = "grid_operator_uid") val gridOperator: GridOperator,
    @OneToMany(mappedBy = "meteringGridArea")
    val tariffAssociations: Set<MeteringGridAreaPowerTariff>,
)
