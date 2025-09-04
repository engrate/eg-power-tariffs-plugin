from engrate_sdk.utils import log

from src.model import GridOperatorSpec
from src.repositories.power_tariffs_repository import repository

logger = log.get_logger(__name__)


async def load_grid_operators():
    from pathlib import Path
    import csv

    with open(Path("data/operators/operators.csv"), "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=";")
        next(reader)
        for row in reader:
            if len(row) < 4:
                logger.warning(f"Skipping malformed row: {row}")
                continue

            # Extract fields
            name = row[0].strip()
            ediel_id = row[1].strip()

            # Check if operator already exists
            existing_operator = await repository.get_operator_by_ediel(int(ediel_id))
            if existing_operator:
                logger.warning(f"Operator {name} already exists, skipping")
                continue

            # Create new grid operator
            grid_operator = GridOperatorSpec(
                name=name,
                ediel=int(ediel_id),
            )

            await repository.save_operator(grid_operator)
            logger.info(f"Created grid operator: {name} (Ediel: {ediel_id})")
