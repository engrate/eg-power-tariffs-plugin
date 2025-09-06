package io.engrate.powertariffs.persistence.schema

import com.fasterxml.jackson.annotation.JsonProperty
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.OneToMany
import jakarta.persistence.Table
import jakarta.persistence.Temporal
import jakarta.persistence.TemporalType
import java.time.LocalDateTime
import java.time.ZonedDateTime
import java.util.UUID
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes

@Entity
@Table(name = "power_tariffs")
class PowerTariff(
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "uid", nullable = false, unique = true)
    val uid: UUID = UUID.randomUUID(),
    @Column(name = "name", nullable = false, length = 255) val name: String,
    @Column(name = "model", nullable = false, length = 50) val model: String,
    @Column(name = "description", columnDefinition = "TEXT") val description: String? = null,
    @Column(name = "samples_per_month", nullable = false) val samplesPerMonth: Int,
    @Column(name = "time_unit", nullable = false, length = 20) val timeUnit: String,
    @Column(name = "building_type", nullable = false, length = 50) val buildingType: String = "All",
    @Column(name = "last_updated", nullable = false)
    @Temporal(TemporalType.TIMESTAMP)
    val lastUpdated: ZonedDateTime = ZonedDateTime.now(),
    @Column(name = "valid_from")
    @Temporal(TemporalType.TIMESTAMP)
    val validFrom: LocalDateTime? = null,
    @Column(name = "valid_to") @Temporal(TemporalType.TIMESTAMP) val validTo: LocalDateTime? = null,
    @Column(name = "voltage", nullable = false, length = 10) val voltage: String,
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "compositions", nullable = false, columnDefinition = "jsonb")
    val compositions: List<TariffComposition>,
    @OneToMany(mappedBy = "powerTariff") val areaAssociations: Set<MeteringGridAreaPowerTariff>,
)

data class TimeInterval(
    @param:JsonProperty("from_time") val from: String,
    @param:JsonProperty("to_time") val to: String,
    val multiplier: Double,
)

data class TariffComposition(
    val months: List<MonthEnum>,
    val days: List<DaysEnum>,
    @param:JsonProperty("fuse_from") val fuseFrom: String,
    @param:JsonProperty("fuse_to") val fuseTo: String,
    val unit: String,
    @param:JsonProperty("price_exc_vat") val priceExcVat: Double,
    @param:JsonProperty("price_inc_vat") val priceIncVat: Double,
    val intervals: List<TimeInterval>,
)

enum class MonthEnum {
    @JsonProperty("jan") JANUARY,
    @JsonProperty("feb") FEBRUARY,
    @JsonProperty("mar") MARCH,
    @JsonProperty("apr") APRIL,
    @JsonProperty("may") MAY,
    @JsonProperty("jun") JUNE,
    @JsonProperty("jul") JULY,
    @JsonProperty("aug") AUGUST,
    @JsonProperty("sep") SEPTEMBER,
    @JsonProperty("oct") OCTOBER,
    @JsonProperty("nov") NOVEMBER,
    @JsonProperty("dec") DECEMBER,
}

enum class DaysEnum {
    @JsonProperty("mon") MONDAY,
    @JsonProperty("tue") TUESDAY,
    @JsonProperty("wed") WEDNESDAY,
    @JsonProperty("thu") THURSDAY,
    @JsonProperty("fri") FRIDAY,
    @JsonProperty("sat") SATURDAY,
    @JsonProperty("sun") SUNDAY,
}
