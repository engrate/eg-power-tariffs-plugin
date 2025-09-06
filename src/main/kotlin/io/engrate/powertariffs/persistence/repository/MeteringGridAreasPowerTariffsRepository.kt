package io.engrate.powertariffs.persistence.repository

import io.engrate.powertariffs.persistence.schema.MeteringGridAreaPowerTariff
import java.util.UUID
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface MeteringGridAreasPowerTariffsRepository :
    JpaRepository<MeteringGridAreaPowerTariff, UUID> {}
