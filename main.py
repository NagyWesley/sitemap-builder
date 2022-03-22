import time
from crawler import build_site_map
from xml_builder import create_site_map

if __name__ == '__main__':
    start_time = time.perf_counter()
    # entry_point = input('entry point:') or 'https://eg.hatla2ee.com/ar/car/hyundai/h1'
    # make = input("make:") or "hyundai"
    entry_point = 'https://eg.hatla2ee.com/ar/car/hyundai/h1'
    make = "hyundai"
    links = build_site_map(entry_point, make)
    # create_site_map(links, entry_point)
    duration = time.perf_counter() - start_time
    links_length = len(links) if isinstance(links, list) else 0
    print(f"Downloaded {links_length} in {round(duration, 2)} seconds")
