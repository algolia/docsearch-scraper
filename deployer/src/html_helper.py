from lxml import html
from selenium import webdriver
import time
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import HtmlResponse
import random
from collections import Counter

def get_dom_from_content(content):
    page = html.fromstring(content)

    return page


def get_content_from_url(url):
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.http.accept-encoding.secure', 'gzip, deflate')

    driver = webdriver.Firefox(profile)
    driver.implicitly_wait(1)
    driver.get(url)
    time.sleep(1)

    content = driver.page_source.encode('utf-8')

    driver.quit()

    return content


def get_possible_main_container(url):
    content = get_content_from_url(url)
    page = get_dom_from_content(content)

    ps = page.xpath("//p")

    possible_main_container = []

    for p in ps:
        elt = p
        elt = elt.getparent()
        i = 0
        while elt is not None:
            if elt.tag != 'html' and (elt.tag != 'body' or i == 0):
                possible_main_container.append(elt)
            i +=1
            elt = elt.getparent()

    return set(possible_main_container)


def get_depth(div):
    depth = 0
    elt = div
    while elt is not None:
        elt = elt.getparent()
        depth += 1
    return depth - 1


def get_selectors(div):
    id = div.get('id', None)

    classes = div.get('class', None)

    if div.tag in ['main', 'article', 'section']:
        return div.tag

    if classes is not None:
        return ['.' + e.strip() for e in classes.split(' ')]

    if id is not None:
        return "#" + id

    if div.tag != 'div':
        return div.tag

    return None


def get_p_count(div):
    return len(div.findall('.//p'))


def get_selector_count(div):
    return 0

def sort_selectors(a, b):
    if a["p_count"] > b["p_count"]:
        return -1

    if a["p_count"] < b["p_count"]:
        return 1

    if a["depth"] > b["depth"]:
        return -1

    if a["depth"] < b["depth"]:
        return 1

    if isinstance(a["selector"], list) and not isinstance(b["selector"], list):
        return -1

    return 1


def get_eligible_divs(url):
    possible_main_container = get_possible_main_container(url)
    eligible_divs = []
    for div in possible_main_container:
        eligible_divs.append({
            "depth": get_depth(div),
            "selector": get_selectors(div),
            "selector_count": get_selector_count(div),
            "p_count": get_p_count(div),
        })
        #print get_selectors(div), get_p_count(div), get_depth(div)

    eligible_divs = [elt for elt in eligible_divs if elt['selector'] is not None]
    eligible_divs.sort(sort_selectors)

    return eligible_divs

def get_main_selector_for_url(url):
    eligible_divs = get_eligible_divs(url)
    best_div = eligible_divs[0] if len(eligible_divs) > 0 else None

    main_selector = None

    if best_div is not None:
        main_selector = best_div['selector']

        if isinstance(main_selector, list):
            if len(main_selector) == 1:
                main_selector = main_selector[0]
            else:
                i = 1
                print("Choose main selector")
                for selector in main_selector:
                    print(str(i) + ") " + selector)
                    i += 1
                choice = 1
                try:
                    choice = int(raw_input(""))
                    if choice < 1 or choice > len(main_selector):
                        choice = 1
                except ValueError:
                    pass
                main_selector = main_selector[choice - 1]
    return main_selector


def get_links(url, body):
    start_url = url
    if '.html' in start_url:
        start_url = start_url.rsplit('/', 1)[0]

    response = HtmlResponse(
        url=start_url,
        body=body,
        encoding='utf8'
    )

    link_extractor = LxmlLinkExtractor(
        allow=[start_url],
        deny=[],
        tags='a',
        attrs='href',
        canonicalize=True
    )

    return link_extractor.extract_links(response)


def get_main_selector(url):
    return "FIXME"
    content = get_content_from_url(url)

    links = [link.url for link in get_links(url, content) if link.url != url and link.url + '/' != url]

    if len(links) >= 3:
        random.shuffle(links)

        n = min(6, max(len(links), 3))
        selectors = [get_main_selector_for_url(link) for link in links[:n]]

        count = Counter(selectors)
        selector = count.most_common()[0][0]

        return selector
    else:
        return get_main_selector_for_url(url)
