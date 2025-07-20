#!/usr/bin/env python
# -*- coding: utf-8 -*-

import html, re
from src.core.HTTPCommunication import HTTPConnection
from src.core.HttpError import JSONError
from src.logger.Logger import Logger


class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def load_data(self, data_type="UserData"):
        """Ruft eine Updatefunktion im Spiel auf und verarbeitet die empfangenen userdaten."""
        try:
            response, content = self.__http.send('ajax/menu-update.php')
            self.__http.check_http_state_ok(response)
            content = self.__http.get_json_and_check_for_success(content)
            if data_type == "UserData":
                return {
                    'uname': str(content['uname']),
                    'bar': str(content['bar']),
                    'bar_unformat': float(content['bar_unformat']),
                    'points': int(content['points']),
                    'coins': int(content['coins']),
                    'level': str(content['level']),
                    'levelnr': int(content['levelnr']),
                    'mail': int(content['mail']),
                    'contracts': int(content['contracts']),
                    'g_tag': str(content['g_tag']),
                    'time': int(content['time']),
                    'citymap': content['citymap'],
                }
            else:
                return content
        except Exception:
            Logger().exception('Failed to load user data')
            return None

    def get_info_from_stats(self, info):
        """
        Returns different parameters from user's stats'
        @param info: available values: 'Username', 'Gardens', 'CompletedQuests'
        @return: parameter value
        """
        try:
            address =   f'ajax/ajax.php?do=statsGetStats&which=0&start=0' \
                        f'&additional={self.user_id()}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content.decode('UTF-8'))
            return self.__get_info_from_json(jContent, info)
        except Exception:
            Logger().exception('Failed to get info from stats')
            return None

    def __get_info_from_json(self, jContent, info):
        """Looks up certain info in the given JSON object and returns it."""
        # ToDo: Dumb Style. Needs refactoring
        success = False
        result = None
        if info == 'Username':
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][0]).replace(r'&nbsp;', ''))
            result = parsed_string_list[1]
            success = True
        elif info == 'Gardens':
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][16]).replace(r'&nbsp;', ''))
            result = int(parsed_string_list[1])
            success = True
        elif info == 'CompletedQuests':
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][5]).replace(r'&nbsp;', ''))
            result = int(parsed_string_list[1])
            success = True
        elif info == 'AquagardenQuest':
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][6]).replace(r'&nbsp;', ''))
            result = int(parsed_string_list[1])
            success = True
        elif info == 'CactusQuest':
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][7]).replace(r'&nbsp;', ''))
            result = int(parsed_string_list[1])
            success = True
        elif info == 'EchinoQuest':
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][8]).replace(r'&nbsp;', ''))
            result = int(parsed_string_list[1])
            success = True
        elif info == 'BigheadQuest':
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][9]).replace(r'&nbsp;', ''))
            result = int(parsed_string_list[1])
            success = True
        elif info == 'OpuntiaQuest':
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][10]).replace(r'&nbsp;', ''))
            result = int(parsed_string_list[1])
            success = True
        elif info == 'SaguaroQuest':
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][11]).replace(r'&nbsp;', ''))
            result = int(parsed_string_list[1])
            success = True
        elif info == 'Wimps':
            parsed_string_list_sales = re.findall(r"<td>(.+?)</td>", str(jContent['table'][12]).replace(r'&nbsp;', '').replace('.', ''))
            sales = int(parsed_string_list_sales[1])
            parsed_string_list_revenue = re.findall(r"<td>(.+?)</td>", str(jContent['table'][13]).replace(r'&nbsp;', ' '))
            revenue = parsed_string_list_revenue[1]
            success = True
            return sales, revenue

        if success:
            return result
        else:
            print(jContent['table'])
            raise JSONError('Info:' + info + " not found.")

    def user_id(self):
        return self.__http.user_id()

    def check_mail_confirmed(self):
        """Check if mail address is confirmed"""
        try:
            response, content = self.__http.send('nutzer/profil.php')
            self.__http.check_http_state_ok(response)
            result = re.search('Unbestätigte Email:', html.unescape(str(content)))
            return result == None
        except Exception:
            Logger().exception('Failed to check if mail is confirmed')
            return None

    def has_watering_gnome_helper(self):
        try:
            response, content = self.__http.send('main.php?page=garden')
            content = content.decode('UTF-8')
            self.__http.update_token_from_content(content)
            self.__http.check_http_state_ok(response)
            re_gnome = re.search(r'wimparea.init.*\"helper\":.*(water).*\"garbage', content)
            return re_gnome is not None and re_gnome.group(1) == "water"
        except Exception:
            Logger.exception('Failed to check is user has watering gnome')
            return None

