from bs4 import BeautifulSoup
import requests
import json
import sys

def get_soup_instance(url):
	headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
			'Accept-Language': "en,en-US;q=0,5",
			'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8"
			}
	response = requests.get(url, headers=headers)

	if response.status_code != 200:
		print("Request ended with bad code", response.status_code)
		return None

	try:
		soup = BeautifulSoup(response.text, "html.parser")
		return soup
	except Exception as e:
		print("Failed to parse HTML, exception was:", str(e))
		return None

def download_listing(url):
	soup = get_soup_instance(url)

	try:
		return (json.loads(soup.find('script', {'type': 'application/ld+json'}).text), url)
	except Exception as e:
		return None

def get_listings(search_url):
	soup = get_soup_instance(search_url)

	f = soup.find_all('a', {'class': 'OLXad-list-link'})
	ret = []
	for result in f:
		ret.append(result['href'])
	return ret

if len(sys.argv) < 2:
	print("a search URL is required")
	exit(1)

pages = int(input("How many pages? "))

listings = []

print("Downloading pages", end='')
for page_num in range(pages):
	suffix = '&o=' + str(page_num+1)
	listings += get_listings(sys.argv[1] + suffix)
	print('. ', end='')
print()

option = -1
excluded_brands = []
while option != 0:
	print("1. Exclude brand [", end='')
	for brand in excluded_brands:
		print(brand + ',', end='')
	print(']')
	print("0. Init search")

	option = int(input())

	if option == 1:
		excluded_brands.append(input("Brand name: "))

for listing in listings:
	_json = download_listing(listing)
	try:
		if _json[0] and _json[0]['makesOffer']['itemOffered']['brand'] not in excluded_brands:
			print(_json[0]['makesOffer']['itemOffered']['name'], _json[1])
	except Exception as e:
		pass
