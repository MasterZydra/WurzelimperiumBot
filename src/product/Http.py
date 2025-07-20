#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
from lxml import etree

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_all_product_infos(self):
        """Collect all product infos"""
        try:
            response, content = self.__http.send('main.php?page=garden')
            content = content.decode('UTF-8')
            self.__http.update_token_from_content(content)
            self.__http.check_http_state_ok(response)

            products = re.search(r'data_products = ({.*}});var', content)
            return products.group(1)
        except Exception:
            Logger().print_exception('FAiled to get all product infos')
            return None

    def get_npc_prices(self):
        """Get all NPC prices for all products from the help dialog"""
        response, content = self.__http.send('hilfe.php?item=2')
        self.__http.check_http_state_ok(response)
        content = content.decode('UTF-8').replace('Gärten & Regale', 'Gärten und Regale')
        return self.__parse_npc_prices_from_html(content)

    def __parse_npc_prices_from_html(self, html_data) -> dict:
        """Parse all NPC prices from HTML"""
        my_parser = etree.HTMLParser(recover=True)
        html_tree = etree.fromstring(str(html_data), parser=my_parser)

        table = html_tree.find('./body/div[@id="content"]/table')

        result = {}

        for row in table.iter('tr'):

            product_name = row[0].text
            npc_price = row[1].text

            # Table heading has text "None"
            if product_name != None and npc_price != None:
                npc_price = str(npc_price)
                npc_price = npc_price[0:len(npc_price) - 3]
                npc_price = npc_price.replace('.', '')
                npc_price = npc_price.replace(',', '.')
                npc_price = npc_price.replace(' ', '')
                npc_price = npc_price.strip()
                if len(npc_price) == 0:
                    npc_price = None
                else:
                    npc_price = float(npc_price)

                result[product_name] = npc_price

        return result