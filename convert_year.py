

from files.handler import load_cars_data, save_cars_data


if __name__ == "__main__":
    cars = load_cars_data()
    for car in cars:
        car.first_use = f"{car.first_use}-01-01"
    save_cars_data(cars)
