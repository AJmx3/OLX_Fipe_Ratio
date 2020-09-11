from bs4 import BeautifulSoup

import sys
from olx import OLX
from olx import get_soup_instance

if len(sys.argv) < 3:
        print("USAGE: %s <base_url> <min_ratio>" % sys.argv[0])
        exit(1)
else:
        base_url = sys.argv[1]
        MIN_RATIO = float(sys.argv[2])

o = OLX()

urls = o.get_page_urls(base_url)
print("Downloading %s pages" % len(urls))
print("Showing listings with ratio better than %s" % (MIN_RATIO))
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
                    print(listing.year, listing.brand, listing.version, "-listing R$", listing.price, "-fipe R$", listing.fipe, "-ratio", ratio, listing_url)
            except Exception as e:
                print(str(e))
