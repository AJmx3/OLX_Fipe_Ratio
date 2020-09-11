from bs4 import BeautifulSoup
import requests
import json
import sys

class Listing:
    def __init__(self, brand, model, version, year, price, fipe):
        self.brand = brand
        self.model = model
        self.version = version
        self.year = year
        self.price = price
        self.fipe = fipe

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

class OLX():
    def __init__(self):
            self.base_fipe_url = 'https://www.olx.com.br/tabela-fipe/'

    def download_listing(self, url):
            soup = get_soup_instance(url)

            try:
                    return (json.loads(soup.find('script', {'type': 'application/ld+json'}).text), url)
            except Exception as e:
                    return None

    def listing_soup_to_json(self, soup):
            try:
                    return json.loads(soup.find('script', {'type': 'application/ld+json'}).text)
            except Exception as e:
                    return None

    def get_page(self, page_url):
            soup = get_soup_instance(page_url)

            f = soup.find_all('a', {'data-lurker-detail': 'list_id'})
            ret = []
            for result in f:
                    ret.append(result['href'])
            return ret

    def get_pages_from_base(self, base_url, count):
            pages =  []
            for page_num in range(count):
                    suffix = '?o=' + str(page_num+1)
                    pages.append(self.get_page(base_url+ suffix))
            return pages

    def get_number_of_pages(self, base_url):
        soup = get_soup_instance(base_url)
        a = soup.find('a', {'data-lurker-detail': 'last_page'})
        if a:
            try:
                if a['href'].split('o=')[1].startswith('100'):
                    return 100
                else:
                    count = a['href'].split('o=')[1][:2]
                    if not count[1].isdigit():
                        return int(count[0])
                    else:
                        return int(count)
            except Exception as e:
                print(str(e))
        return None

    def get_all_pages(self, base_url):
            soup = get_soup_instance(base_url)
            count = self.get_number_of_pages(soup)

            pages =  []
            for page_num in range(count):
                    suffix = '?o=' + str(page_num+1)
                    pages.append(self.get_page(base_url + suffix))
            return pages

    def get_page_urls(self, base_url):
            count = self.get_number_of_pages(base_url)
            if count == None:
                count = 1
            page_urls =  []
            if '?' in base_url:
                    add = '&o='
            else:
                    add = '?o='

            for page_num in range(count):
                    suffix = add + str(page_num+1)
                    page_urls.append(base_url + suffix)
            return page_urls

    def get_version_url(self, model_url, version):
        soup = get_soup_instance(model_url)
        if soup:
            ul = soup.find('ul', {'class': 'versions__List-bie68s-2 ePtyzD'})
            if ul:
                for li in ul.find_all('li'):
                    if li.text == version:
                        return li.a['href']
        else:
            print(model_url)
        return None

    def get_fipe_value(self, url):
            soup = get_soup_instance(url)
            _json = soup.find('script', {'type': 'application/json'})
            if _json:
                return json.loads(_json.text)
            return None

    def get_fipe_from_listing_soup(self, listing_soup):
        _json = None
        scripts = listing_soup.find_all('script')
        for script in scripts:
            if script and script.text and script.text.startswith('window.dfpPageSegmentationDataLayer'):
                _json = '{' + script.text.split('{')[1][:-1]
                _json = json.loads(_json)

        try:
            brand    = _json['marca_carro']
            year     = _json['ano_carro']
            model    = _json['modelo_carro']
            model_version  = _json['dfp_vas_car_version']
            price = _json['dfp_vas_car_price']
        except Exception:
            return False

        if not brand or not year or not model or not model_version:
            return False

        version  = model_version[len(model)+1:]


        fipe_url = self.base_fipe_url + brand.replace(' ', '').lower() + '/' + model.lower() + '/' + year
        url = self.get_version_url(fipe_url, model_version)
        if url:
            fipe_url = self.base_fipe_url + brand.replace(' ', '').lower() + '/' + model.lower() + '/' + url

            try:
                fipe = self.get_fipe_value(fipe_url)['props']['pageProps']['version']['price']
                return Listing(brand, model, version, year, price, fipe)
            except Exception as e:
                print(str(e))
                return None
        else:
            return None
