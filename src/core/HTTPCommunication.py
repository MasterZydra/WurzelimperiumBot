#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from urllib.parse import urlencode
import json, re, httplib2, yaml, i18n
from http.cookies import SimpleCookie
from http import HTTPStatus
from src.core.HttpError import HTTPStateError, JSONError, HTTPRequestError, YAMLError
from src.core.ServerUrls import SERVER_URLS
from src.core.Session import Session
from src.logger.Logger import Logger

i18n.load_path.append('lang')

class HTTPConnection:
    """Mit der Klasse HTTPConnection werden alle anfallenden HTTP-Verbindungen verarbeitet."""

    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(HTTPConnection, self).__new__(self)
            self._instance.__initClass()
        return self._instance

    def __initClass(self):
        self.__webclient = httplib2.Http(disable_ssl_certificate_validation=True)
        self.__webclient.follow_redirects = False
        self.__session = Session()
        self.__token = None
        self.__userID = None
        self.__unr = None
        self.__portunr = None

    def __del__(self):
        self.__session = None
        self.__token = None
        self.__userID = None
        self.__unr = None
        self.__portunr = None

    def token(self):
        return self.__token

    def user_id(self):
        """Gibt die wunr als userID zurück die beim Login über das Cookie erhalten wurde."""
        return self.__userID

    def update_token_from_content(self, content):
        if not isinstance(content, str):
            content = content.decode('UTF-8')
        reToken = re.search(r'ajax\.setToken\(\"(.*)\"\);', content)
        self.__token = reToken.group(1)

    def send(self, address: str, method: str = 'GET', body = None, headers: dict = {}):
        uri = f'http://s{self.__session.get_server()}{self.__session.get_server_url()}{address}'
        defaultHeaders = {
            'Cookie': f'PHPSESSID={self.__session.get_session_id()};wunr={self.__userID}',
            'Connection': 'Keep-Alive'
        }
        headers = {**defaultHeaders, **headers}
        return self.__webclient.request(uri, method, body, headers)

    def check_http_state_ok(self, response):
        """Prüft, ob der Status der HTTP Anfrage OK ist."""
        if not (response['status'] == str(HTTPStatus.OK.value)):
            Logger().info('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht OK')

    def check_http_state_found(self, response):
        """Prüft, ob der Status der HTTP Anfrage FOUND ist."""
        if not (response['status'] == str(HTTPStatus.FOUND.value)):
            Logger().info('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht FOUND')

    def get_json_and_check_for_success(self, content):
        """Aufbereitung und Prüfung der vom Server empfangenen JSON Daten."""
        j_content = json.loads(content)
        if j_content.get('success', 0) == 1 or j_content.get('status', 0) == "SUCCESS":
            return j_content
        else:
            raise JSONError(f"success = {j_content['success']}")

    def get_json_and_check_for_ok(self, content: str):
        """Aufbereitung und Prüfung der vom Server empfangenen JSON Daten."""
        j_content = json.loads(content)
        if j_content['status'] == 'ok':
            return j_content
        else:
            raise JSONError(f"status = {j_content['status']}")

    def get_yaml_and_check_for_success(self, content: str):
        """Aufbereitung und Prüfung der vom Server empfangenen YAML Daten auf Erfolg."""
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        yContent = yaml.load(content, Loader=yaml.FullLoader)

        if yContent['success'] != 1:
            raise YAMLError()

    def __get_token_from_url(self, url):
        """Ermittelt aus einer übergebenen URL den security token."""
        split = re.search(r'https://.*/logw.php.*token=([a-f0-9]{32})', url)
        if split:
            tmpToken = split.group(1)
            if tmpToken != '':
                self.__token = tmpToken
                return

        raise JSONError('Fehler bei der Ermittlung des tokens')

    def __get_token_from_url_portal(self, url):
        """Ermittelt aus einer übergebenen URL den security token."""
        split = re.search(r'.*portal/port_logw.php.*token=([a-f0-9]{32})', url)
        if split:
            tmpToken = split.group(1)
            if tmpToken != '':
                self.__token = tmpToken
                return

        raise JSONError(f'Fehler bei der Ermittlung des tokens')

    def __get_unr_from_url_portal(self, url):
        """Ermittelt aus einer übergebenen URL den security token."""
        split = re.search(r'.*portal/port_logw.php.*unr=([a-f0-9]+)&port', url)
        if split:
            tmpunr = split.group(1)
            if tmpunr != '':
                self.__unr = tmpunr
                return

        Logger().info(tmpunr)
        raise JSONError(f'Fehler bei der Ermittlung des tokens')

    def __get_port_unr_from_url_portal(self, url):
        """Ermittelt aus einer übergebenen URL den security token."""
        split = re.search(r'.*portal/port_logw.php.*portunr=([a-f0-9]+)&token', url)
        if split:
            tmpportunr = split.group(1)
            if tmpportunr != '':
                self.__portunr = tmpportunr
                return

        Logger().info(tmpportunr)
        raise JSONError(f'Fehler bei der Ermittlung des tokens')

    def logIn(self, loginDaten) -> bool:
        """Führt einen login durch und öffnet eine Session."""
        serverURL = SERVER_URLS[loginDaten.language]
        parameter = urlencode({
            'do': 'login',
            'server': f'server{str(loginDaten.server)}',
            'user': loginDaten.user,
            'pass': loginDaten.password
        })
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive'
        }

        try:
            response, content = self.__webclient.request(
                f'https://www{serverURL}dispatch.php',
                'POST',
                parameter,
                headers
            )
            self.check_http_state_ok(response)
            jContent = self.get_json_and_check_for_ok(content)
            self.__get_token_from_url(jContent['url'])
            response, content = self.__webclient.request(jContent['url'], 'GET', headers=headers)
            self.check_http_state_found(response)
            cookie = SimpleCookie(response['set-cookie'])
            cookie.load(str(response['set-cookie']).replace('secure, ', '', -1))
            self.__session.open(cookie['PHPSESSID'].value, str(loginDaten.server), serverURL)
            self.__userID = cookie['wunr'].value
            return True
        except Exception:
            Logger().print_exception('Login failed')
            return False

    def logInPortal(self, loginDaten) -> bool:
        """Führt einen login durch und öffnet eine Session."""
        parameter = urlencode({
            'portserver': 'server' + str(loginDaten.server),
            'portname': loginDaten.user,
            'portpass': loginDaten.password,
            'portsubmit': 'Einloggen'
        })
        serverURL = SERVER_URLS[loginDaten.language]
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive'
        }

        try:
            response, content = self.__webclient.request(
                f'https://www{serverURL}/portal/game2port_login.php', \
                'POST', \
                parameter, \
                headers
            )
            self.__get_token_from_url_portal(response['location'])
            self.__get_unr_from_url_portal(response['location'])
            self.__get_port_unr_from_url_portal(response['location'])
        except Exception:
            Logger().print_exception("Portal login failed")
            return False

        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Cookie': self.__unr
        }

        try:
            loginadresse = f'https://s{str(loginDaten.server)}{serverURL}/logw.php?port=1&unr=' + \
                           f'{self.__unr}&portunr={self.__portunr}&hash={self.__token}&sno={loginDaten.server}'
            response, content = self.__webclient.request(loginadresse, 'GET', headers=headers)
            self.check_http_state_found(response)
            cookie = SimpleCookie(response['set-cookie'])
            cookie.load(str(response["set-cookie"]).replace("secure, ", "", -1))
            self.__session.open(cookie['PHPSESSID'].value, str(loginDaten.server), serverURL)
            self.__userID = self.__unr

            return True
        except Exception:
            Logger().print_exception("Portal login failed")
            return False

    def logOut(self) -> bool:
        """Logout des Spielers inkl. Löschen der Session."""
        #TODO: Was passiert beim Logout einer bereits ausgeloggten Session
        try: #content ist beim Logout leer
            response, content = self.send('main.php?page=logout')
            self.check_http_state_found(response)

            # Check if session was deleted
            cookie = SimpleCookie(response['set-cookie'])
            if not (cookie['PHPSESSID'].value == 'deleted'):
                Logger().info('SessionID: ' + cookie['PHPSESSID'].value)
                raise HTTPRequestError('Session wurde nicht gelöscht')
            
            self.__session.close()
            self.__del__()

            return True
        except Exception:
            Logger().print_exception("Failed to log out")
            return False

    def initInfinityQuest(self):
        adresse = f'ajax/ajax.php?do=infinite_quest_get&token={self.__token}'
        try:
            response, content = self.send(adresse)
            self.check_http_state_ok(response)
            jContent = self.get_json_and_check_for_ok(content)
            return jContent
        except Exception:
            Logger().print_exception("Failed to init infinity quest")
            return None

    def sendInfinityQuest(self, questnr, product, amount):
        try:
            address =   f'ajax/ajax.php?do=infinite_quest_entry&pid={product}' \
                        f'&amount={amount}&questnr={questnr}&token={self.__token}'
            response, content = self.send(address)
            self.check_http_state_ok(response)
            jContent = self.get_json_and_check_for_ok(content)
            return jContent
        except Exception:
            Logger().print_exception('Failed to send infinity quest')
            return None
