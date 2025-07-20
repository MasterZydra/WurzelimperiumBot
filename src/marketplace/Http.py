#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
from lxml import html
import io, re

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_tradeable_products_from_overview(self):
        """"Return list of all tradable products"""
        try:
            response, content = self.__http.send('stadt/markt.php?show=overview')
            self.__http.check_http_state_ok(response)
            tradeable_products = re.findall(r'markt\.php\?order=p&v=([0-9]{1,3})&filter=1', content)
            for i in range(0, len(tradeable_products)):
                tradeable_products[i] = int(tradeable_products[i])
            return tradeable_products
        except Exception:
            Logger().print_exception('Failed to get tradeable products from marketplace overview')
            return None

    def get_offers_for_product(self, product_id):
        """Determine all offers for a product"""
        next_page = True
        page_index = 1
        offers = []
        while next_page:
            next_page = False

            try:
                address = f'stadt/markt.php?order=p&v={str(product_id)}&filter=1&page={str(page_index)}'
                response, content = self.__http.send(address)
                self.__http.check_http_state_ok(response)
                html_file = io.BytesIO(content)
                html_tree = html.parse(html_file)
                root = html_tree.getroot()
                table = root.findall('./body/div/table/*')

                if table[1][0].text == 'Keine Angebote':
                    return

                # Range from 1 to length-1, as the first line is headings and the last is Next/Back.
                for i in range(1, len(table)-1):
                    amount = table[i][0].text.encode('utf-8').replace('.', '')
                    price = table[i][3].text.encode('utf-8').replace('\xc2\xa0wT', '').replace('.', '').replace(',', '.')
                    offers.append([int(amount), float(price)])

                # If there are several pages
                for element in table[len(table)-1][0]:
                    if 'weiter' in element.text:
                        next_page = True
                        page_index += 1
            except Exception:
                Logger().print_exception('Failed to get offers for products from marketplace')
                return None

        return offers