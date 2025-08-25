package io.engrate.powertariffs.persistence.schema

import jakarta.persistence.*
import java.time.ZonedDateTime
import java.util.UUID

@Entity
@Table(name = "power_tariffs")
data class PowerTariff(
    @Id @Column(name = "uid", nullable = false, unique = true) val uid: UUID = UUID.randomUUID(),
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "provider_uid", nullable = false)
    val provider: GridProvider,
    @Column(name = "country_code", length = 5, nullable = false) val countryCode: String,
    @Column(name = "time_zone", length = 50, nullable = false)
    val timeZone: String = "Europe/Stockholm",
    @Column(name = "valid_from", nullable = false) val validFrom: ZonedDateTime,
    @Column(name = "valid_to", nullable = false) val validTo: ZonedDateTime,
    @Column(name = "last_updated", nullable = false)
    val lastUpdated: ZonedDateTime = ZonedDateTime.now(),
    @OneToMany(
        mappedBy = "tariff",
        cascade = [CascadeType.ALL],
        orphanRemoval = true,
        fetch = FetchType.LAZY,
    )
    val fees: MutableList<PowerTariffFee> = mutableListOf(),
)
