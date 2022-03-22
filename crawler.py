import requests
import re
import concurrent.futures


def crawl_page(*args, **kwargs):
    url = kwargs['url']
    ep = kwargs['ep']
    try:
        if 'href' in url:
            pattern = re.compile('/[a-zA-Z0-9/%-]*')
            to_crawl = pattern.findall(url)
            to_crawl = ep + to_crawl[0]
        else:
            to_crawl = url
        r = requests.get(to_crawl)
        return {"html": r.content.decode('utf-8'), "url": url}
    except Exception as e:
        print(type(e))


def get_page_links(html, make):
    pattern = re.compile(f"href=\S+\/hyundai\/[^>\s]+")
    return re.findall(pattern, html)


def is_leaf_link(url):
    return bool(re.search("\S+\/\d{5,}\"$", url))


def fetch_data_div(html):
    pattern = re.compile(r"^<div class=\"DescDataItem\"[\s\S]+?div>")
    result = re.search(pattern, html)
    div = result.group(1)
    return div


def populate_car(html):
    data_html = fetch_data_div(html)
    print(data_html)


def build_site_map(ep='https://eg.hatla2ee.com/ar/car', make="hyundai"):
    to_crawl = [ep]
    crawled = []
    links = []
    cars = []
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while len(to_crawl) > 0:
                results = [executor.submit(
                    crawl_page, url=url, ep=ep, make=make) for url in to_crawl]
                for f in concurrent.futures.as_completed(results):
                    result = f.result()
                    html = result['html']
                    crawled.append(result['url'])
                    if not is_leaf_link(result['url']):
                        page_links = get_page_links(html, make)
                        for link in page_links:
                            if link not in crawled and link not in to_crawl:
                                to_crawl.append(link)
                                links.append(link)
                    else:
                        cars.append(populate_car(html))
                    to_crawl.remove(result['url'])
        return sorted(links)
    except Exception as e:
        print(type(e))
