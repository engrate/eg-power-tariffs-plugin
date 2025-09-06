package io.engrate.powertariffs.persistence.schema

import jakarta.persistence.*
import java.util.UUID

@Entity
@Table(name = "grid_operators")
class GridOperator(
    @Id @Column(name = "uid", nullable = false, unique = true) val uid: UUID = UUID.randomUUID(),
    @Column(name = "name", nullable = false, unique = true, length = 255) val name: String,
    @Column(name = "ediel", nullable = false, unique = true) val ediel: Int,
    @OneToMany(mappedBy = "gridOperator") val meteringGridAreas: Set<MeteringGridArea>,
)
