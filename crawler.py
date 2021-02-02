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


def get_page_links(html):
    return re.findall(r'href="/[a-zA-Z0-9/%-]*"', html)


def build_site_map(ep='http://localhost:3000'):
    to_crawl = [ep]
    crawled = []
    links = []
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while len(to_crawl) > 0:
                results = [executor.submit(crawl_page, url=url, ep=ep) for url in to_crawl]
                for f in concurrent.futures.as_completed(results):
                    result = f.result()
                    html = result['html']
                    crawled.append(result['url'])
                    page_links = get_page_links(html)
                    for link in page_links:
                        if link not in crawled and link not in to_crawl:
                            to_crawl.append(link)
                            links.append(link)
                    to_crawl.remove(result['url'])
        return sorted(links)
    except Exception as e:
        print(type(e))
