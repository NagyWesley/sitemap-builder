
from dataclasses import dataclass


def convert(key):
    switcher = {
        "الموديل": "model",
        "أول إستخدام": "first_use",
        "كم": "mileage",
        "اللون": "color",
        "ناقل الحركة": "transmission",
        "الوقود": "fuel",
        "طراز": "line"
    }
    return switcher.get(key)


def clean_value(key, value):
    if key in ["mileage", "price"]:
        holder = value.split(" ")[0]
        parts = holder.split(",")
        value = int(parts[0]+parts[1])
    if key in ["id", "first_use"]:
        value = int(value)
    if key in ["publish_date"]:
        value = value.split("\n")[1]
    return value


@dataclass(order=True)
class Car:
    id: int
    publish_date: str = ""
    model: str = ""
    line: str = ""
    first_use: str = ""
    mileage: int = 0
    color: str = ""
    price: int = 0
    fuel: str = ""
    transmission: str = ""
    url: str = ""
