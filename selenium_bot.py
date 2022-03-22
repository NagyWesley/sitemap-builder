import time
from alive_progress import alive_bar
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import concurrent.futures

from data.car import Car, convert, clean_value
from files.handler import load_cars_data, save_cars_data


PATH = '/home/nagy/Downloads/chromedriver_linux64/chromedriver'
# URL = "https://eg.hatla2ee.com/ar/car/hyundai/h1"
URL = "https://eg.hatla2ee.com/ar/car/kia/cerato"

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument(f"PATH={PATH}")


def car_scrape(url):
    try:
        driver = webdriver.Chrome(PATH, options=chrome_options)
        driver.get(url)
        car_data: WebElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "usedUnitCarWrap"))
        )
        properties: WebElement = car_data.find_elements(
            by=By.CLASS_NAME, value="DescDataItem")

        price: WebElement = car_data.find_element(
            by=By.CLASS_NAME, value="usedUnitCarPrice")

        url_parts = driver.current_url.split("/")
        id = url_parts[len(url_parts)-1]

        publish_date: WebElement = car_data.find_element(
            by=By.CLASS_NAME, value="date")

        converted_properties = {"price": clean_value(
            "price", price.text), "id": id, "url": driver.current_url, "publish_date": clean_value("publish_date", publish_date.text)}
        for property in properties:
            try:

                keyElement = property.find_element(
                    by=By.CLASS_NAME, value="DescDataSubTit")
                valueElement = property.find_element(
                    by=By.CLASS_NAME, value="DescDataVal")
                key = convert(keyElement.text)
                if key:
                    converted_properties[key] = clean_value(
                        key, valueElement.text)
            except Exception as e:
                print(f"missing element {str(e)}")
        return Car(**converted_properties)
    except Exception as e:
        print(f"car_scrape - {str(e)}")
    finally:
        driver.quit()


def open_link(driver: webdriver.Chrome, link: WebElement):

    if link.tag_name == "a":
        # text = link.text.split("\n")[0]
        # link = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.LINK_TEXT, text)))
        link.send_keys(Keys.CONTROL + Keys.ENTER)


def check_mileage_presence(tags):
    tag: WebElement
    for tag in tags:
        if "كم" in tag.text:
            milage = tag.text.split(" ")[0]
            return milage != "-"


def model_scrape(driver: webdriver.Chrome):
    model_urls = []
    try:
        cars_list_element: WebElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "listCar-container"))
        )
        cars_list = cars_list_element.find_elements(
            by=By.CLASS_NAME, value="newCarListUnit_data_contain")
        car_div: WebElement

        for car_div in cars_list:
            # Car tags shown in the list
            tags = car_div.find_elements(
                by=By.CLASS_NAME, value="newCarListUnit_metaTag")
            if(check_mileage_presence(tags)):
                div_header = car_div.find_element(
                    by=By.CLASS_NAME, value="newCarListUnit_header")
                link:  WebElement = div_header.find_element(
                    by=By.TAG_NAME, value="a")
                url = link.get_attribute("href")
                model_urls.append(url)
        next_page = driver.find_element(
            by=By.LINK_TEXT, value="التالى »")
        if next_page:
            open_link(driver, next_page)
    except Exception as e:
        print(f"model_scrape - {str(e)}")
    finally:
        driver.close()
        return model_urls


def model_variant_scrape(driver: webdriver.Chrome):
    try:
        model_data: WebElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "model-labels-wrap"))
        )

        links: WebElement = model_data.find_elements(
            by=By.CLASS_NAME, value="label-link")

        # click on all models
        link: WebElement

        for link in links:
            open_link(driver, link)

    except Exception as e:
        print(f"model variant error {str(e)}")


def sorter(car: Car):
    years = 2022 - car.first_use
    # kilo per year
    kpy = car.mileage/(years+1)
    return kpy/car.price


def compute(cars_urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(car_scrape, url=url) for url in cars_urls]
        for f in concurrent.futures.as_completed(results):
            result = f.result()
            yield result


if __name__ == "__main__":
    start_time = time.perf_counter()
    saved_data = None
    if not saved_data:
        url = URL
        driver = webdriver.Chrome(PATH, options=chrome_options)
        cars_urls = []

        try:
            driver.get(url)
            print(f"opened {url}")
            model_variant_scrape(driver)

            while len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[1])
                print(
                    f"model_scrape - {driver.title} open tabs: {len(driver.window_handles)}")
                if driver.current_url != url:
                    cars_urls.extend(model_scrape(driver))

            cars = []
            driver.switch_to.window(driver.window_handles[0])
            cars_total = len(cars_urls)

            with alive_bar(cars_total) as bar:
                for i in compute(cars_urls):
                    cars.append(i)
                    bar()
            save_cars_data(cars)
        except Exception as e:
            driver.quit()

    else:
        cars = saved_data

    # filtered_cars = [car for car in cars if car.mileage >
    #                  0 and car.price < 220000 and car.first_use >= 2011 and car.first_use < 2012]
    # sorted_cars = sorted(
    #     filtered_cars, key=sorter, reverse=True)
    duration = time.perf_counter() - start_time
    print(f"scraped {len(cars)} car in {round(duration, 2)} seconds")
