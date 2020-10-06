from bs4 import BeautifulSoup

import sys
import time
import threading
from olx import OLX
from olx import get_soup_instance

if len(sys.argv) < 3:
    print("USAGE: %s <urls_filename.txt> <min_ratio>" % sys.argv[0])
    exit(1)
else:
    filename = sys.argv[1]
    MIN_RATIO = float(sys.argv[2])

o = OLX()

try:
    _file = open(filename)
except Exception:
    print("Failed to open file %s" % (filename))
    exit(1)

def execute(urls):
    page_count = 1
    for url in urls:
        print("PAGE", page_count)
        page_count += 1
        page = o.get_page(url)
        for listing_url in page:
            listing_soup = get_soup_instance(listing_url)
            if not listing_soup:
                print("Listing soup download failed", listing_url)
                continue
            listing = o.get_fipe_from_listing_soup(listing_soup)
            if listing:
                try:
                    ratio = float(listing.price)/float(listing.fipe)
                    if ratio < MIN_RATIO:
                        if listing.leilao:
                            print("LEILAO! ", end='')
                        print(listing.year, listing.brand, listing.version, "-listing R$", listing.price, "-fipe R$", listing.fipe, "-ratio", ratio, listing_url)
                except Exception as e:
                    print(str(e))

print("Showing listings with ratio better than %s" % (MIN_RATIO))

threads = []

for url in _file:
    urls = o.get_page_urls(url.strip())
    if urls:
        print("%s; %d pages" % (url.strip(), len(urls)))
        t = threading.Thread(target=execute, args=(urls,))
        t.daemon = True
        t.start()
        threads.append(t)

while True:
    running = False
    for t in threads:
        if t.is_alive():
            running = True
        time.sleep(2)

    if not running:
        exit(1)

