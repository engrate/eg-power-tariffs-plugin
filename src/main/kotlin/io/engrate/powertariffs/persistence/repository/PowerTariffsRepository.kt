package io.engrate.powertariffs.persistence.repository

import io.engrate.powertariffs.persistence.schema.PowerTariff
import java.util.UUID
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository

@Repository
interface PowerTariffsRepository : JpaRepository<PowerTariff, UUID> {
    @Query(
        """
        SELECT distinct pt
        FROM PowerTariff pt
        JOIN FETCH pt.areaAssociations aa
        WHERE aa.meteringGridArea.countryCode = :countryCode
        AND aa.meteringGridArea.code = :mgaCode
        """
    )
    fun findPowerTariffsByMga(
        @Param("countryCode") countryCode: String,
        @Param("mgaCode") mgaCode: String,
    ): List<PowerTariff>
}
