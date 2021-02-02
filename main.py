import time
from crawler import build_site_map
from xml_builder import create_site_map

if __name__ == '__main__':
    start_time = time.perf_counter()
    entry_point = input('entry point:')
    links = build_site_map(entry_point)
    create_site_map(links, entry_point)
    duration = time.perf_counter() - start_time
    print(f"Downloaded {len(links)} in {round(duration, 2)} seconds")
