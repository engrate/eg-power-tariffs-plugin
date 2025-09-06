package io.engrate.powertariffs.persistence.repository

import io.engrate.powertariffs.persistence.schema.MeteringGridArea
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface MeteringGridAreasRepository : JpaRepository<MeteringGridArea, String> {
    fun findByCode(code: String): MeteringGridArea?
}
