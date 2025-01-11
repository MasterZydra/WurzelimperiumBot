#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from urllib.parse import urlencode
import json, re, httplib2, yaml, logging, math, i18n
from http.cookies import SimpleCookie
from http import HTTPStatus
from src.core.HttpError import HTTPStateError, JSONError, HTTPRequestError, YAMLError
from src.core.Session import Session

i18n.load_path.append('lang')

SERVER_URLS = {
    'de': '.wurzelimperium.de/',
    'bg': '.bg.molehillempire.com/',
    'en': '.molehillempire.com/',
    'us': '.molehillempire.com/',
    'ru': '.sadowajaimperija.ru/'
}

class HTTPConnection(object):
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
        self.__userAgent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 Vivaldi/2.2.1388.37'
        self.__logHTTPConn = logging.getLogger('bot.HTTPConn')
        self.__logHTTPConn.setLevel(logging.DEBUG)
        self.__session = Session()
        self.__token = None
        self.__userID = None
        self.__cookie = None
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

    def update_token_from_content(self, content):
        if not isinstance(content, str):
            content = content.decode('UTF-8')
        reToken = re.search(r'ajax\.setToken\(\"(.*)\"\);', content)
        self.__token = reToken.group(1)

    def sendRequest(self, address: str, method: str = 'GET', body = None, headers: dict = {}):
        uri = self.__get_server() + address
        headers = {**self.__getHeaders(), **headers}
        try:
            return self.__webclient.request(uri, method, body, headers)
        except:
            raise

    def __getUserDataFromJSONContent(self, content):
        """Ermittelt userdaten aus JSON Content."""
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

    def checkIfHTTPStateIsOK(self, response):
        """Prüft, ob der Status der HTTP Anfrage OK ist."""
        if not (response['status'] == str(HTTPStatus.OK.value)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht OK')

    def __checkIfHTTPStateIsFOUND(self, response):
        """Prüft, ob der Status der HTTP Anfrage FOUND ist."""
        if not (response['status'] == str(HTTPStatus.FOUND.value)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht FOUND')


    def generateJSONContentAndCheckForSuccess(self, content):
        """Aufbereitung und Prüfung der vom Server empfangenen JSON Daten."""
        j_content = json.loads(content)
        if j_content.get('success', 0) == 1 or j_content.get('status', 0) == "SUCCESS":
            return j_content
        else:
            raise JSONError(f"success = {j_content['success']}")

    def generateJSONContentAndCheckForOK(self, content: str):
        """Aufbereitung und Prüfung der vom Server empfangenen JSON Daten."""
        j_content = json.loads(content)
        if j_content['status'] == 'ok':
            return j_content
        else:
            raise JSONError(f"status = {j_content['status']}")

    def __getTokenFromURL(self, url):
        """Ermittelt aus einer übergebenen URL den security token."""
        split = re.search(r'https://.*/logw.php.*token=([a-f0-9]{32})', url)
        iErr = 0
        if split:
            tmpToken = split.group(1)
            if tmpToken == '':
                iErr = 1
        else:
            iErr = 1

        if iErr == 1:
            self.__logHTTPConn.debug(tmpToken)
            raise JSONError('Fehler bei der Ermittlung des tokens')
        else:
            self.__token = tmpToken

    def __getTokenFromURLPORT(self, url):
        """Ermittelt aus einer übergebenen URL den security token."""
        split = re.search(r'.*portal/port_logw.php.*token=([a-f0-9]{32})', url)
        iErr = 0
        if split:
            tmpToken = split.group(1)
            if (tmpToken == ''):
                iErr = 1
        else:
            iErr = 1

        if (iErr == 1):
            self.__logHTTPConn.debug(tmpToken)
            raise JSONError(f'Fehler bei der Ermittlung des tokens')
        else:
            self.__token = tmpToken

    def __getunrFromURLPORT(self, url):
        """Ermittelt aus einer übergebenen URL den security token."""
        split = re.search(r'.*portal/port_logw.php.*unr=([a-f0-9]+)&port', url)
        iErr = 0
        if split:
            tmpunr = split.group(1)
            if (tmpunr == ''):
                iErr = 1
        else:
            iErr = 1

        if (iErr == 1):
            self.__logHTTPConn.debug(tmpunr)
            raise JSONError(f'Fehler bei der Ermittlung des tokens')
        else:
            self.__unr = tmpunr

    def __getportunrFromURLPORT(self, url):
        """Ermittelt aus einer übergebenen URL den security token."""
        split = re.search(r'.*portal/port_logw.php.*portunr=([a-f0-9]+)&token', url)
        iErr = 0
        if split:
            tmpportunr = split.group(1)
            if (tmpportunr == ''):
                iErr = 1
        else:
            iErr = 1

        if (iErr == 1):
            self.__logHTTPConn.debug(tmpportunr)
            raise JSONError(f'Fehler bei der Ermittlung des tokens')
        else:
            self.__portunr = tmpportunr

    def __getInfoFromJSONContent(self, jContent, info):
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
            self.__logHTTPConn.debug(jContent['table'])
            raise JSONError('Info:' + info + " not found.")

    def __checkIfSessionIsDeleted(self, cookie):
        """Prüft, ob die Session gelöscht wurde."""
        if not (cookie['PHPSESSID'].value == 'deleted'):
            self.__logHTTPConn.debug('SessionID: ' + cookie['PHPSESSID'].value)
            raise HTTPRequestError('Session wurde nicht gelöscht')

    def generateYAMLContentAndCheckForSuccess(self, content: str):
        """Aufbereitung und Prüfung der vom Server empfangenen YAML Daten auf Erfolg."""
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        yContent = yaml.load(content, Loader=yaml.FullLoader)

        if yContent['success'] != 1:
            raise YAMLError()

    def __getHeaders(self):
        headers = {'Cookie': f'PHPSESSID={self.__session.get_session_id()};wunr={self.__userID}',
                   'Connection': 'Keep-Alive'}
        return headers

    def __get_server(self):
        return f'http://s{self.__session.get_server()}{self.__session.get_server_url()}'


    def logIn(self, loginDaten):
        """Führt einen login durch und öffnet eine Session."""
        serverURL = SERVER_URLS[loginDaten.language]
        parameter = urlencode({'do': 'login',
                               'server': f'server{str(loginDaten.server)}',
                               'user': loginDaten.user,
                               'pass': loginDaten.password})

        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Connection': 'keep-alive'}

        try:
            response, content = self.__webclient.request(f'https://www{serverURL}dispatch.php',
                                                         'POST',
                                                         parameter,
                                                         headers)
            self.checkIfHTTPStateIsOK(response)
            jContent = self.generateJSONContentAndCheckForOK(content)
            self.__getTokenFromURL(jContent['url'])
            response, content = self.__webclient.request(jContent['url'], 'GET', headers=headers)
            self.__checkIfHTTPStateIsFOUND(response)
        except:
            raise
        else:
            cookie = SimpleCookie(response['set-cookie'])
            cookie.load(str(response["set-cookie"]).replace("secure, ", "", -1))
            self.__session.open(cookie['PHPSESSID'].value, str(loginDaten.server), serverURL)
            self.__cookie = cookie
            self.__userID = cookie['wunr'].value

    def logInPortal(self, loginDaten):
        """Führt einen login durch und öffnet eine Session."""
        parameter = urlencode({'portserver': 'server' + str(loginDaten.server),
                               'portname': loginDaten.user,
                               'portpass': loginDaten.password,
                               'portsubmit': 'Einloggen'})
        serverURL = SERVER_URLS[loginDaten.language]
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Connection': 'keep-alive'}

        try:
            response, content = self.__webclient.request(f'https://www{serverURL}/portal/game2port_login.php', \
                                                         'POST', \
                                                         parameter, \
                                                         headers)
            self.__getTokenFromURLPORT(response['location'])
            self.__getunrFromURLPORT(response['location'])
            self.__getportunrFromURLPORT(response['location'])
        except:
            raise

        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Connection': 'keep-alive',
                   'Cookie': self.__unr}

        try:
            loginadresse = f'https://s{str(loginDaten.server)}{serverURL}/logw.php?port=1&unr=' + \
                           f'{self.__unr}&portunr={self.__portunr}&hash={self.__token}&sno={loginDaten.server}'
            response, content = self.__webclient.request(loginadresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsFOUND(response)
        except:
            raise
        else:
            cookie = SimpleCookie(response['set-cookie'])
            cookie.load(str(response["set-cookie"]).replace("secure, ", "", -1))
            self.__session.open(cookie['PHPSESSID'].value, str(loginDaten.server), serverURL)
            self.__cookie = cookie
            self.__userID = self.__unr

    def get_user_id(self):
        """Gibt die wunr als userID zurück die beim Login über das Cookie erhalten wurde."""
        return self.__userID


    def logOut(self):
        """Logout des Spielers inkl. Löschen der Session."""
        #TODO: Was passiert beim Logout einer bereits ausgeloggten Session
        try: #content ist beim Logout leer
            response, content = self.sendRequest('main.php?page=logout')
            self.__checkIfHTTPStateIsFOUND(response)
            cookie = SimpleCookie(response['set-cookie'])
            self.__checkIfSessionIsDeleted(cookie)
            self.__session.close()
        except:
            raise
        else:
            self.__del__()


    def getInfoFromStats(self, info):
        """
        Returns different parameters from user's stats'
        @param info: available values: 'Username', 'Gardens', 'CompletedQuests'
        @return: parameter value
        """
        try:
            address =   f'ajax/ajax.php?do=statsGetStats&which=0&start=0' \
                        f'&additional={self.__userID}&token={self.__token}'
            response, content = self.sendRequest(address)
            self.checkIfHTTPStateIsOK(response)
            jContent = self.generateJSONContentAndCheckForOK(content.decode('UTF-8'))
            result = self.__getInfoFromJSONContent(jContent, info)
        except:
            raise
        else:
            return result


    def readUserDataFromServer(self, data_type="UserData"):
        """Ruft eine Updatefunktion im Spiel auf und verarbeitet die empfangenen userdaten."""
        try:
            response, content = self.sendRequest('ajax/menu-update.php')
            self.checkIfHTTPStateIsOK(response)
            jContent = self.generateJSONContentAndCheckForSuccess(content)
        except:
            raise
        else:
            if data_type == "UserData":
                return self.__getUserDataFromJSONContent(jContent)
            else:
                return jContent

    #TODO: Was passiert wenn ein Garten hinzukommt (parallele Sitzungen im Browser und Bot)? Globale Aktualisierungsfunktion?

    def getUsrList(self, iStart, iEnd):
        """
        #TODO: finalisieren
        """
        userList = {'Nr':[], 'Gilde':[], 'Name':[], 'Punkte':[]}
        #iStart darf nicht 0 sein, da sonst beim korrigierten Index -1 übergeben wird
        userList = {'Nr': [], 'Gilde': [], 'Name': [], 'Punkte': []}
        # iStart darf nicht 0 sein, da sonst beim korrigierten Index -1 übergeben wird
        if iStart <= 0:
            iStart = 1

        if iStart == iEnd or iStart > iEnd:
            return False

        iStartCorr = iStart - 1
        iCalls = int(math.ceil(float(iEnd - iStart) / 100))

        print(iCalls)
        for i in range(iCalls):
            print(i)
            try:
                address =   f'ajax/ajax.php?do=statsGetStats&which=1&start={str(iStartCorr)}' \
                            f'&showMe=0&additional=0&token={self.__token}'
                response, content = self.sendRequest(address)
                self.checkIfHTTPStateIsOK(response)
                jContent = self.generateJSONContentAndCheckForOK(content)
            except:
                raise
            else:
                try:
                    for j in jContent['table']:
                        result = re.search(r'<tr><td class=".*">(.*)<\/td><td class=".*tag">(.*)<\/td><td class=".*uname">([^<]*)<.*class=".*pkt">(.*)<\/td><\/tr>',j)
                        userList['Nr'].append(str(result.group(1)).replace('.', ''))
                        userList['Gilde'].append(str(result.group(2)))
                        userList['Name'].append(str(result.group(3).encode('utf-8')).replace('&nbsp;', ''))
                        userList['Punkte'].append(int(str(result.group(4).replace('.', ''))))
                except:
                    raise

            iStartCorr = iStartCorr + 100

        return userList

    def initInfinityQuest(self):
        headers = self.__getHeaders()
        server = self.__get_server()
        adresse = f'{server}ajax/ajax.php?do=infinite_quest_get&token={self.__token}'
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.checkIfHTTPStateIsOK(response)
            jContent = self.generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            pass

    def sendInfinityQuest(self, questnr, product, amount):
        try:
            address =   f'ajax/ajax.php?do=infinite_quest_entry&pid={product}' \
                        f'&amount={amount}&questnr={questnr}&token={self.__token}'
            response, content = self.sendRequest(address)
            self.checkIfHTTPStateIsOK(response)
            jContent = self.generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            pass

    # Shop
    def buy_from_shop(self, shop: int, productId: int, amount: int = 1):
        parameter = urlencode({
            's': shop,
            'page': 1,
            'change_page_only': 0,
            'produkt[0]': productId,
            'anzahl[0]': amount
        })
        try:
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            response, content = self.sendRequest(f'stadt/shop.php?s={shop}', 'POST', parameter, header)
            self.checkIfHTTPStateIsOK(response)
        except:
            raise

    def buyFromAquaShop(self, productId: int, amount: int = 1):
        adresse = f'ajax/ajax.php?products={productId}:{amount}&do=shopBuyProducts&type=aqua&token={self.__token}'

        try:
            response, content = self.sendRequest(f'{adresse}')
            self.checkIfHTTPStateIsOK(response)
        except:
            return ''
