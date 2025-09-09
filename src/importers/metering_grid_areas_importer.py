from engrate_sdk.utils import log

from src.model import MeteringGridAreaSpec
from src.repositories.power_tariffs_repository import repository

logger = log.get_logger(__name__)


async def load_metering_grid_areas():
    from pathlib import Path
    import csv

    with open(Path("data/metering_grid_areas/mgas.csv"), "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=";")
        for row in reader:
            if len(row) < 6:
                logger.warning(f"Skipping malformed row: {row}")
                continue

            # Extract fields
            operator_name = row[0].strip()
            mga_name = row[1].strip()
            mga_code = row[2].strip()
            mga_type = row[3].strip()
            mba_code = row[4].strip()
            country = row[5].strip()

            # Skip if not a grid operator (Nätägare)
            if "DISTRIBUTION" not in mga_type:
                logger.warning(
                    f"Skipping {mga_name} - only DISTRIBUTION types are supported"
                )
                continue

            # Check if operator already exists
            existing_operator = await repository.get_operator_by_name(operator_name)
            if not existing_operator:
                logger.warning(f"Operator {operator_name} does not exists, skipping")
                continue

            mag = MeteringGridAreaSpec(
                code=mga_code,
                country_code=country,
                name=mga_name,
                metering_business_area=mba_code,
                grid_operator=existing_operator.model_dump(),
            )
            existing_mga = await repository.get_metering_grid_area_by_code(mga_code)
            if existing_mga:
                logger.warning(
                    f"Metering grid area {mga_code} already exists, skipping"
                )
                continue
            await repository.save_metering_grid_area(mag)
            logger.info(f"Metering grid area saved: {mga_name} (Code: {mga_code})")
