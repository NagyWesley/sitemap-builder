from cmath import inf
import dataclasses
import json

from data.car import Car


def load_cars_data():
    try:
        with open('files/cerato-18-3-2022.json') as json_file:
            data = json.load(json_file)
            cars = [Car(**car) for car in data.get("cars")]
            return cars
    except:
        return None


def save_cars_data(cars):
    serialized_cars = [dataclasses.asdict(car)
                       for car in cars if isinstance(car, Car)]
    with open('files/cars.json', 'w') as outfile:
        json.dump({"cars": serialized_cars}, outfile)
