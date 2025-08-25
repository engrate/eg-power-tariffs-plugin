package io.engrate.powertariffs.persistence.schema

import jakarta.persistence.*
import java.util.UUID

@Entity
@Table(name = "providers")
data class GridProvider(
    @Id @Column(name = "uid", nullable = false, unique = true) val uid: UUID = UUID.randomUUID(),
    @Column(name = "name", nullable = false, unique = true) val name: String,
    @Column(name = "ediel", nullable = false, unique = true) val ediel: Int,
    @Column(name = "org_number", length = 50, nullable = false, unique = true)
    val orgNumber: String,
    @Column(name = "active", nullable = false) val active: Boolean = true,
    @OneToOne(mappedBy = "provider", fetch = FetchType.LAZY) val powerTariff: PowerTariff? = null,
)
