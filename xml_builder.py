import datetime
import xml.etree.cElementTree as Element_Tree
from xml.dom import minidom
import re


def create_site_map(links, ep):
    try:
        ct = datetime.datetime.now().strftime('%Y-%m-%d')
        url_set = Element_Tree.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        pattern = r"/[/\w%-]*"
        pattern = re.compile(pattern)
        for link in links:
            url = Element_Tree.SubElement(url_set, "url")
            route_reg = pattern.search(link)
            if route_reg.group(0):
                route = route_reg.group(0)
                priority = str(round(1 / route.count('/'), 2))
                Element_Tree.SubElement(url, "loc").text = f'{ep}{route}'
                Element_Tree.SubElement(url, "lastmod").text = str(ct)
                Element_Tree.SubElement(url, "priority").text = priority
        xml_str = minidom.parseString(Element_Tree.tostring(url_set)).toprettyxml(indent="   ")
        ptah_name = "sitemap.xml"
        with open(ptah_name, "w") as f:
            f.write(xml_str)
    except Exception as e:
        print(e)
