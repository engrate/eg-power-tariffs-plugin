import csv
from datetime import datetime
from pathlib import Path

from src.importers.power_tariffs.models import (
    Operator,
    PowerTariff,
    PowerTariffComposition,
)
from src.importers.power_tariffs.utils import (
    parse_building_type,
    parse_months,
    parse_days,
    parse_fuse,
    parse_price,
    parse_intervals,
    parse_mgas,
)
from src.model import (
    PowerTariffSpec,
    TariffCompositionSpec,
    TimeIntervalSpec,
    MeteringGridAreaSpec,
)
from src.repositories.power_tariffs_repository import repository, PowerTariffRepository
from engrate_sdk.utils import log

logger = log.get_logger(__name__)


def _parse_tariffs_headers_file() -> list[Operator]:
    operators = {}
    with open(
        Path("data/power_tariffs/tariffs_headers.csv"),
        "r",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        for row in reader:
            ediel = int(row["Provider Ediel"])
            operator = operators.get(ediel, Operator(ediel=ediel, power_tariffs=[]))
            power_tariff = PowerTariff(
                tariff_id=row["Tariff ID"],
                name=row["Name"],
                model=row["Model Name"],
                description=row["Description"],
                samples_per_month=row["Number of samples"],
                time_unit=row["Time unit"],
                building_type=parse_building_type(row["Building types"].lower()),
                mgas=parse_mgas(row["Geolocation -> MGA"]),
                tariff_composition=[],
            )
            operator.power_tariffs.append(power_tariff)
            operators[operator.ediel] = operator

    return list(operators.values())


def _parse_tariffs_compositions_file() -> dict[str, list[PowerTariffComposition]]:
    tariffs_compositions = {}
    with open(
        Path("data/power_tariffs/tariffs_compositions.csv"),
        "r",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        for row in reader:
            tariff_id = row["Fee ID"]
            try:
                tariff_compositions = tariffs_compositions.get(tariff_id, [])
                tariff_composition = PowerTariffComposition(
                    months=parse_months(row["Months Number"]),
                    days=parse_days(row["Days"]),
                    fuse_from=parse_fuse(row["Fuse From"]),
                    fuse_to=parse_fuse(row["Fuse To"]),
                    unit=row["Unit"],
                    price_exc_vat=parse_price(row["Price Ex Vat"]),
                    price_inc_vat=parse_price(row["Price Inc Vat"]),
                    intervals=parse_intervals(row),
                )
                tariff_compositions.append(tariff_composition)
                tariffs_compositions[tariff_id] = tariff_compositions
            except Exception as e:
                logger.error(f"Error parsing fee {tariff_id}: {e}")
    return tariffs_compositions


def _find_tariff(operators: list[Operator], tariff_id: str) -> PowerTariff | None:
    for operator in operators:
        for tariff in operator.power_tariffs:
            if tariff.tariff_id == tariff_id:
                return tariff
    return None  # Not found


async def _parse_files():
    operators = _parse_tariffs_headers_file()
    compositions = _parse_tariffs_compositions_file()
    for tariff_id in compositions.keys():
        tariff_composition = compositions[tariff_id]

        operator_tariff = _find_tariff(operators, tariff_id)
        if not operator_tariff:
            raise ValueError(f"Operator not found for tariff ID: {tariff_id}")

        operator_tariff.tariff_composition.extend(tariff_composition)
    return operators


async def load_tariffs_definitions():
    operators = await _parse_files()

    for operator in operators:
        # get the operator
        existing_operator = await repository.get_operator_by_ediel(operator.ediel)
        if not existing_operator:
            logger.warning(
                f"Skipping power tariff: Operator {operator.ediel} not found"
            )
            continue

        # get all the metering grid area for that operator
        metering_grid_areas = await repository.get_metering_grid_areas_by_operator(
            existing_operator.uid
        )
        if not metering_grid_areas:
            logger.warning(
                f"Skipping power tariff: No metering grid areas for {operator.ediel}"
            )
            continue

        operator_already_has_tariffs = False
        for metering_grid_area in metering_grid_areas:
            power_tariff = await repository.get_power_tariff_by_mga(
                metering_grid_area.country_code, metering_grid_area.code
            )
            if power_tariff:
                operator_already_has_tariffs = True
            break
        if operator_already_has_tariffs:
            logger.warning(f"Operator {operator.ediel} already has tariffs, skipping.")
            continue

        await _save_operator_tariffs(operator, metering_grid_areas)


async def _save_operator_tariffs(
    operator: Operator, metering_grid_areas: list[MeteringGridAreaSpec]
):
    for power_tariff in operator.power_tariffs:
        compositions = []
        for composition in power_tariff.tariff_composition:
            compositions.append(
                TariffCompositionSpec(
                    months=composition.months,
                    days=composition.days,
                    fuse_from=composition.fuse_from,
                    fuse_to=composition.fuse_to,
                    unit=composition.unit,
                    price_exc_vat=composition.price_exc_vat,
                    price_inc_vat=composition.price_inc_vat,
                    intervals=[
                        TimeIntervalSpec(
                            from_time=interval.from_time,
                            to_time=interval.to_time,
                            multiplier=interval.multiplier,
                        )
                        for interval in composition.intervals
                    ],
                )
            )

        if not compositions:
            logger.warning(
                f"No tariffs composition for {power_tariff.name} EDIEL {operator.ediel}"
            )

        if power_tariff.mgas:
            mgas = []
            for mga_id in power_tariff.mgas:
                mga = await repository.get_metering_grid_area_by_code(mga_id)
                if mga:
                    mgas.append(mga)
            metering_grid_areas = mgas

        if not metering_grid_areas:
            raise ValueError("No valid metering grid areas found")

        power_tariff = PowerTariffSpec(
            name=power_tariff.name,
            model=power_tariff.model,
            description=power_tariff.description,
            samples_per_month=power_tariff.samples_per_month,
            time_unit=power_tariff.time_unit,
            building_type=power_tariff.building_type,
            last_updated=datetime.now(),
            voltage="LV",
            compositions=compositions,
            metering_grid_areas=metering_grid_areas,
        )

        await repository.save_power_tariff(power_tariff)
