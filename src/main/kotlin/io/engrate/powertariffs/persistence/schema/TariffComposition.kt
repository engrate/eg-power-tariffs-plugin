package io.engrate.powertariffs.persistence.schema

import jakarta.persistence.*
import java.math.BigDecimal
import java.util.UUID
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes

@Entity
@Table(name = "tariff_compositions")
data class TariffComposition(
    @Id @Column(name = "uid", nullable = false, unique = true) val uid: UUID = UUID.randomUUID(),
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "fee_id", nullable = false)
    val fee: PowerTariffFee,
    @JdbcTypeCode(SqlTypes.ARRAY)
    @Column(name = "months", columnDefinition = "integer[]")
    val months: List<Int> = emptyList(),
    @JdbcTypeCode(SqlTypes.ARRAY)
    @Column(name = "days", columnDefinition = "text[]")
    val days: List<String> = emptyList(),
    @Column(name = "fuse_from", length = 10, nullable = false) val fuseFrom: String,
    @Column(name = "fuse_to", length = 10, nullable = false) val fuseTo: String,
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "hints", columnDefinition = "jsonb", nullable = false)
    val hints: String,
    @Column(name = "unit", length = 20, nullable = false) val unit: String,
    @Column(name = "price_exc_vat", nullable = false) val priceExcVat: BigDecimal,
    @Column(name = "price_inc_vat", nullable = false) val priceIncVat: BigDecimal,
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "intervals", columnDefinition = "jsonb", nullable = false)
    val intervals: String,
)
