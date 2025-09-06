package io.engrate.powertariffs.api

import io.engrate.powertariffs.persistence.schema.DaysEnum
import io.engrate.powertariffs.persistence.schema.MonthEnum
import io.engrate.powertariffs.persistence.schema.PowerTariff
import java.time.ZonedDateTime
import java.util.UUID

data class PowerTariffDto(
    val uid: UUID,
    val name: String,
    val model: String,
    val description: String?,
    val samplesPerMonth: Int,
    val timeUnit: String,
    val buildingType: String,
    val lastUpdated: ZonedDateTime,
    val voltage: String,
    val compositions: List<CompositionDto>,
    val meteringGridAreas: List<MeteringGridAreaDto>,
)

data class CompositionDto(
    val months: List<MonthEnum>,
    val days: List<DaysEnum>,
    val fuseFrom: String,
    val fuseTo: String,
    val unit: String,
    val priceExcVat: Double,
    val priceIncVat: Double,
    val intervals: List<IntervalDto>,
)

data class IntervalDto(val from: String, val to: String, val multiplier: Double)

data class MeteringGridAreaDto(
    val code: String,
    val name: String,
    val countryCode: String,
    val meteringBusinessArea: String,
    val gridOperator: GridOperatorDto,
)

data class GridOperatorDto(val uid: UUID, val name: String, val ediel: Int)

fun PowerTariff.toDto(): PowerTariffDto {
    return PowerTariffDto(
        uid = this.uid,
        name = this.name,
        model = this.model,
        description = this.description,
        samplesPerMonth = this.samplesPerMonth,
        timeUnit = this.timeUnit,
        buildingType = this.buildingType,
        lastUpdated = this.lastUpdated,
        voltage = this.voltage,
        compositions =
            this.compositions.map { comp ->
                CompositionDto(
                    months = comp.months,
                    days = comp.days,
                    fuseFrom = comp.fuseFrom,
                    fuseTo = comp.fuseTo,
                    unit = comp.unit,
                    priceExcVat = comp.priceExcVat,
                    priceIncVat = comp.priceIncVat,
                    intervals =
                        comp.intervals.map { it ->
                            IntervalDto(from = it.from, to = it.to, multiplier = it.multiplier)
                        },
                )
            },
        meteringGridAreas =
            this.areaAssociations.map { area ->
                MeteringGridAreaDto(
                    code = area.meteringGridArea.code,
                    name = area.meteringGridArea.name,
                    countryCode = area.meteringGridArea.countryCode,
                    meteringBusinessArea = area.meteringGridArea.meteringBusinessArea,
                    gridOperator =
                        GridOperatorDto(
                            uid = area.meteringGridArea.gridOperator.uid,
                            name = area.meteringGridArea.gridOperator.name,
                            ediel = area.meteringGridArea.gridOperator.ediel,
                        ),
                )
            },
    )
}
