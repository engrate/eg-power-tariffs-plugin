import calendar
import re

from src.importers.power_tariffs.models import Interval
from src.model import BuildingType


def parse_building_type(string) -> BuildingType:
    if not string:
        return BuildingType.ALL
    has_house = "_house" in string
    has_apartments = "apartments" in string
    if has_house and has_apartments:
        return BuildingType.ALL
    if has_house:
        return BuildingType.HOUSE
    if has_apartments:
        return BuildingType.APARTMENT
    raise ValueError("Invalid building type")


def parse_months(string):
    if not string:
        string = "1,2,3,4,5,6,7,8,9,10,11,12"
    return [calendar.month_abbr[int(month)].lower() for month in string.split(",")]


def parse_days(string):
    string = re.sub(r"\s+", "", string)  # remove empty spaces
    if not string:
        string = "M,T,W,T,F,S,S"
    days = []
    if "M,T,W,T,F" in string:
        days.extend(
            [
                calendar.MONDAY,
                calendar.TUESDAY,
                calendar.WEDNESDAY,
                calendar.THURSDAY,
                calendar.FRIDAY,
            ]
        )
    if "S,S" in string:
        days.extend([calendar.SATURDAY, calendar.SUNDAY])

    if not days:
        raise ValueError("Invalid days format")
    return [calendar.day_abbr[day].lower() for day in days]


def parse_fuse(string):
    return string


def parse_price(string):
    try:
        return float(string)
    except ValueError:
        raise ValueError(f"Invalid price format {string}")


def parse_intervals(row) -> list[Interval]:
    from1 = row["From"]
    if not from1:
        raise ValueError(f"Invalid From interval value {from1}")

    to1 = row["To"]
    if to1 == "0:00":
        to1 = "24:00"
    multiplier1 = float(row["Multiplier"])
    intervals = [Interval(from_time=from1, to_time=to1, multiplier=multiplier1)]

    from2 = row["From2"]
    if from2:
        to2 = row["To2"]
        if to2 == "0:00":
            to2 = "24:00"

        multiplier2 = float(row["Multiplier2"])
        intervals.append(Interval(from_time=from2, to_time=to2, multiplier=multiplier2))

    return intervals

def parse_mgas(value: str) -> list[str]:
    if not value or value.strip().lower() == "all":
        return []
    return [item.strip() for item in value.strip().split(",") if item.strip()]