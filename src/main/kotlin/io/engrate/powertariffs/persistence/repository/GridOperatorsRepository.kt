package io.engrate.powertariffs.persistence.repository

import io.engrate.powertariffs.persistence.schema.GridOperator
import java.util.UUID
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface GridOperatorsRepository : JpaRepository<GridOperator, UUID> {
    fun findByEdiel(ediel: Int): GridOperator?

    fun findByName(name: String): GridOperator?
}
