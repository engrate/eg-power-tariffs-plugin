package io.engrate.powertariffs.persistence.schema

import jakarta.persistence.*
import java.util.UUID

@Entity
@Table(name = "metering_grid_area_x_power_tariff")
class MeteringGridAreaPowerTariff(
    @Id @Column(name = "uid", nullable = false, unique = true) val uid: UUID = UUID.randomUUID(),
    @ManyToOne @JoinColumn(name = "mga_code") val meteringGridArea: MeteringGridArea,
    @ManyToOne @JoinColumn(name = "tariff_uid") val powerTariff: PowerTariff,
)
