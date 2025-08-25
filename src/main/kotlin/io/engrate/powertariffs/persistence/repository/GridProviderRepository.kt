package io.engrate.powertariffs.persistence.repository

import io.engrate.powertariffs.persistence.schema.GridProvider
import java.util.UUID
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface GridProviderRepository : JpaRepository<GridProvider, UUID> {
    fun findByEdiel(ediel: Int): GridProvider?
}
