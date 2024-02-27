#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez / Reworked: xRuffKez
'''

from urllib.parse import urlencode
from http.cookies import SimpleCookie
import json
import re
import httplib2
import yaml
import time
import logging
import math
import io
import i18n
import requests
import xml.etree.ElementTree as eTree
from src.Session import Session
from lxml import html, etree

# Load language files
i18n.load_path.append('lang')

# HTTP response status codes
HTTP_STATE_OK = 200
HTTP_STATE_FOUND = 302  # Moved Temporarily

# Server URLs
SERVER_URLS = {
    'de': '.wurzelimperium.de/',
    'bg': '.bg.molehillempire.com/',
    'en': '.molehillempire.com/',
    'us': '.molehillempire.com/',
    'ru': '.sadowajaimperija.ru/'
}

class HTTPConnection:
    """Class for handling HTTP connections."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HTTPConnection, cls).__new__(cls)
            cls._instance.__initClass()
        return cls._instance
    
    def __initClass(self):
        """Initializes class attributes."""
        self.__webclient = httplib2.Http(disable_ssl_certificate_validation=True)
        self.__webclient.follow_redirects = False
        self.__userAgent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 Vivaldi/2.2.1388.37'
        self.__logHTTPConn = logging.getLogger('bot.HTTPConn')
        self.__logHTTPConn.setLevel(logging.DEBUG)
        self.__Session = Session()
        self.__token = None
        self.__userID = None
        self.__cookie = None
        self.__unr = None
        self.__portunr = None

    def __del__(self):
        """Deletes class attributes."""
        self.__Session = None
        self.__token = None
        self.__userID = None
        self.__unr = None
        self.__portunr = None

    def sendRequest(self, address: str, method: str = 'GET', body=None, headers: dict = {}):
        """Sends an HTTP request."""
        return self.__sendRequest(address, method, body, headers)

    def __sendRequest(self, address: str, method: str = 'GET', body=None, headers: dict = {}):
        """Sends an HTTP request and returns the response."""
        uri = self.__getServer() + address
        headers = {**self.__getHeaders(), **headers}
        try:
            return self.__webclient.request(uri, method, body, headers)
        except Exception as e:
            raise e

    def __getUserDataFromJSONContent(self, content):
        """Extracts user data from JSON content."""
        return {'bar': str(content['bar']),
                'bar_unformat': float(content['bar_unformat']),
                'points': int(content['points']),
                'coins': int(content['coins']),
                'level': str(content['level']),
                'levelnr': int(content['levelnr']),
                'mail': int(content['mail']),
                'contracts': int(content['contracts']),
                'g_tag': str(content['g_tag']),
                'time': int(content['time'])}

    def checkIfHTTPStateIsOK(self, response):
        """Checks if HTTP status is OK."""
        return self.__checkIfHTTPStateIsOK(response)

    def __checkIfHTTPStateIsOK(self, response):
        """Checks if HTTP status is OK."""
        if not (response['status'] == str(HTTP_STATE_OK)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status is not OK')

    def __checkIfHTTPStateIsFOUND(self, response):
        """Checks if HTTP status is FOUND."""
        if not (response['status'] == str(HTTP_STATE_FOUND)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status is not FOUND')

    def __generateJSONContentAndCheckForSuccess(self, content):
        """Processes and checks the received JSON data from the server."""
        j_content = json.loads(content)
        if j_content['success'] == 1:
            return j_content
        else:
            raise JSONError()

    def __generateJSONContentAndCheckForOK(self, content: str):
        """Processes and checks the received JSON data from the server."""
        j_content = json.loads(content)
        if j_content['status'] == 'ok':
            return j_content
        else:
            raise JSONError()

    def __isFieldWatered(self, jContent, fieldID):
        """Determines if a field is watered."""
        oneDayInSeconds = (24 * 60 * 60) + 30
        currentTimeInSeconds = time.time()
        waterDateInSeconds = int(jContent['water'][fieldID - 1][1])

        if waterDateInSeconds == 0 or (currentTimeInSeconds - waterDateInSeconds) > oneDayInSeconds:
            return False
        else:
            return True

    def __getTokenFromURL(self, url):
        """Extracts the security token from a URL."""
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
            raise JSONError('Error extracting token')
        else:
            self.__token = tmpToken

    def __getTokenFromURLPORT(self, url):
        """Extracts the security token from the given URL."""
        split = re.search(r'.*portal/port_logw.php.*token=([a-f0-9]{32})', url)
        if split:
            tmpToken = split.group(1)
            if not tmpToken:  # Simplified if condition
                iErr = 1
            else:
                self.__token = tmpToken
                return
        else:
            iErr = 1

        # Moved debug logging and error raising outside the if-else block
        self.__logHTTPConn.debug(tmpToken)
        raise JSONError('Error determining the token')

    def __getunrFromURLPORT(self, url):
        """Extracts the unr (user token) from the given URL."""
        split = re.search(r'.*portal/port_logw.php.*unr=([a-f0-9]+)&port', url)
        if split:
            tmpunr = split.group(1)
            if not tmpunr:
                iErr = 1
            else:
                self.__unr = tmpunr
                return
        else:
            iErr = 1

        self.__logHTTPConn.debug(tmpunr)
        raise JSONError('Error determining the token')

    def __getportunrFromURLPORT(self, url):
        """Extracts the portunr (port user token) from the given URL."""
        split = re.search(r'.*portal/port_logw.php.*portunr=([a-f0-9]+)&token', url)
        if split:
            tmpportunr = split.group(1)
            if not tmpportunr:
                iErr = 1
            else:
                self.__portunr = tmpportunr
                return
        else:
            iErr = 1

        self.__logHTTPConn.debug(tmpportunr)
        raise JSONError('Error determining the token')

    def __getInfoFromJSONContent(self, jContent, info):
        """Looks up certain info in the given JSON object and returns it."""
        # Define mapping of info to table indices
        info_table_mapping = {
            'Username': 0,
            'Gardens': 16,
            'CompletedQuests': 5,
            'CactusQuest': 7,
            'EchinoQuest': 8,
            'BigheadQuest': 9,
            'OpuntiaQuest': 10,
            'SaguaroQuest': 11
        }
        
        # Check if info exists in mapping
        if info in info_table_mapping:
            # Extract the table index corresponding to the info
            table_index = info_table_mapping[info]
            # Find the desired info in the specified table
            parsed_string_list = re.findall(r"<td>(.+?)</td>", str(jContent['table'][table_index]).replace(r'&nbsp;', ''))
            # Ensure parsed_string_list is not empty
            if parsed_string_list:
                # Parse and return the result
                if info == 'Username':
                    return parsed_string_list[1]
                else:
                    return int(parsed_string_list[1])
            else:
                # Log table content and raise error if info not found
                self.__logHTTPConn.debug(jContent['table'])
                raise JSONError('Info:' + info + " not found.")
        else:
            # Raise error if info not found in mapping
            raise ValueError('Info:' + info + " not supported.")

    def __checkIfSessionIsDeleted(self, cookie):
        """Prüft, ob die Session gelöscht wurde."""
        session_id = cookie.get('PHPSESSID', None)
        if session_id and session_id.value != 'deleted':
            self.__logHTTPConn.debug('SessionID: ' + session_id.value)
            raise HTTPRequestError('Session wurde nicht gelöscht')

    def __findPlantsToBeWateredFromJSONContent(self, jContent):
        """Searches the JSON content for plants that can be watered and returns them along with their plant size."""
        plantsToBeWatered = {'fieldID': [], 'sx': [], 'sy': []}
        garden = jContent['garden']
        for field_info in jContent['grow']:
            plantedFieldID, _ = field_info[:2]
            plantSize = garden[str(plantedFieldID)][9]
            sx, sy = map(int, plantSize.split('x'))

            if not self.__isFieldWatered(jContent, plantedFieldID):
                plantsToBeWatered['fieldID'].append(plantedFieldID)
                plantsToBeWatered['sx'].append(sx)
                plantsToBeWatered['sy'].append(sy)

        return plantsToBeWatered

    def __findEmptyFieldsFromJSONContent(self, jContent):
        """Searches the JSON content for empty fields and returns them."""
        emptyFields = [int(field) for field, info in jContent['garden'].items() if info[0] == 0]
        emptyFields.sort()
        return emptyFields

    def __findWeedFieldsFromJSONContent(self, jContent):
        """Searches the JSON content for fields infested with weeds and returns them."""
        weedFields = {int(field): float(info[6]) for field, info in jContent['garden'].items() if info[0] in [41, 42, 43, 45]}
        weedFields = dict(sorted(weedFields.items(), key=lambda item: item[1]))
        return weedFields

    def __findGrowingPlantsFromJSONContent(self, jContent):
        """Returns a list of growing plants from the JSON content."""
        growingPlants = [field_info[1] for field_info in jContent['grow']]
        return growingPlants

    def __findWimpsDataFromJSONContent(self, jContent):
        """Returns list of growing plants from JSON content"""
        wimpsData = {}
        for wimp in jContent['wimps']:
            product_data = {str(product['pid']): int(product['amount']) for product in wimp['sheet']['products']}
            wimpsData[wimp['sheet']['id']] = [wimp['sheet']['sum'], product_data]
        return wimpsData

    def __findEmptyAquaFieldsFromJSONContent(self, jContent):
        emptyAquaFields = [int(field) for field in jContent['garden'] if jContent['garden'][field][0] == 0]
        if emptyAquaFields:
            emptyAquaFields.sort()
        return emptyAquaFields

    def __generateYAMLContentAndCheckForSuccess(self, content: str):
        """Processes and checks the YAML data received from the server for success."""
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        yContent = yaml.safe_load(content)

        if yContent['success'] != 1:
            raise YAMLError()

    def __generateYAMLContentAndCheckStatusForOK(self, content):
        """Processes and checks the YAML data received from the server for status 'ok'."""
        yContent = yaml.safe_load(content)

        if yContent.get('status') != 'ok':
            raise YAMLError()

    def _changeGarden(self, gardenID):
        """Changes the garden."""
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={gardenID}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            self.__generateJSONContentAndCheckForOK(content)
        except Exception as e:
            raise e

    def __parseNPCPricesFromHtml(self, html_data):
        """Parses all NPC prices from the HTML script of the game help."""
        my_parser = etree.HTMLParser(recover=True)
        html_tree = etree.fromstring(html_data, parser=my_parser)

        table = html_tree.find('.//body/div[@id="content"]/table')

        dictResult = {}

        for row in table.iter('tr'):
            cells = row.findall('td')
            if len(cells) >= 2:
                produktname = cells[0].text.strip() if cells[0].text else None
                npc_preis_text = cells[1].text.strip() if cells[1].text else None

                if produktname is not None and npc_preis_text is not None:
                    # Extract the numerical value from npc_preis_text
                    npc_preis_text = npc_preis_text.split()[0]
                    
                    # Handle '-' case
                    npc_preis = float(npc_preis_text.replace('.', '').replace(',', '.')) if npc_preis_text.strip() != '-' else None

                    dictResult[produktname] = npc_preis

        return dictResult

    def __getHeaders(self):
        return {'Cookie': f'PHPSESSID={self.__Session.getSessionID()};wunr={self.__userID}',
                'Connection': 'Keep-Alive'}

    def __getServer(self):
        return f'http://s{self.__Session.getServer()}{self.__Session.getServerURL()}'

############################################################################################## ^^^^^^^^^^^^^^^^ OPTIMIZED ^^^^^^^^^^^^^^^^^^^^^^^^

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
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            self.__getTokenFromURL(jContent['url'])
            response, content = self.__webclient.request(jContent['url'], 'GET', headers=headers)
            self.__checkIfHTTPStateIsFOUND(response)
        except:
            raise
        else:
            cookie = SimpleCookie(response['set-cookie'])
            cookie.load(str(response["set-cookie"]).replace("secure, ", "", -1))
            self.__Session.openSession(cookie['PHPSESSID'].value, str(loginDaten.server), serverURL)
            self.__cookie = cookie
            self.__userID = cookie['wunr'].value

    def logInPortal(self, loginData):
        """Performs a login and opens a session."""
        serverURL = SERVER_URLS[loginData.language]
        portal_login_url = f'https://www{serverURL}/portal/game2port_login.php'
        loginAddress = f'https://s{loginData.server}{serverURL}/logw.php'

        # Construct login parameters
        login_parameters = {
            'portserver': 'server' + str(loginData.server),
            'portname': loginData.user,
            'portpass': loginData.password,
            'portsubmit': 'Login'
        }

        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Connection': 'keep-alive'}

        try:
            # First login request
            response, content = self.__webclient.request(portal_login_url, 'POST', urlencode(login_parameters), headers)
            response.raise_for_status()  # Check for HTTP errors

            # Extract necessary tokens from the redirected location
            self.__getTokenFromURLPORT(response.headers['location'])
            self.__getunrFromURLPORT(response.headers['location'])
            self.__getportunrFromURLPORT(response.headers['location'])
        except Exception as e:
            raise RuntimeError("Failed to login to portal:", e)

        # Prepare headers for the next request with necessary cookies
        headers['Cookie'] = f'PHPSESSID={self.__unr}'

        try:
            # Second login request
            login_params = {
                'port': '1',
                'unr': self.__unr,
                'portunr': self.__portunr,
                'hash': self.__token,
                'sno': loginData.server
            }
            response, content = self.__webclient.request(f"{loginAddress}?{urlencode(login_params)}", 'GET', headers=headers)
            response.raise_for_status()

            # Process response
            cookie = SimpleCookie(response['set-cookie'])
            cookie.load(str(response["set-cookie"]).replace("secure, ", "", -1))
            self.__Session.openSession(cookie['PHPSESSID'].value, str(loginData.server), serverURL)
            self.__userID = self.__unr
        except Exception as e:
            raise RuntimeError("Failed to complete portal login:", e)

    def getUserID(self):
        """Returns the wunr as userID obtained from the cookie during login."""
        return self.__userID

    def logOut(self):
        """Logs out the player including deleting the session."""
        # TODO: What happens when logging out of an already logged out session
        try: # Content is empty during logout
            response, content = self.__sendRequest('main.php?page=logout')
            self.__checkIfHTTPStateIsFOUND(response)
            cookie = SimpleCookie(response['set-cookie'])
            self.__checkIfSessionIsDeleted(cookie)
        except:
            raise
        else:
            self.__del__()

    def getInfoFromStats(self, info):
        """
        Returns different parameters from user's stats.
        @param info: available values: 'Username', 'Gardens', 'CompletedQuests'
        @return: parameter value
        """
        try:
            address =   f'ajax/ajax.php?do=statsGetStats&which=0&start=0' \
                        f'&additional={self.__userID}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content.decode('UTF-8'))
            result = self.__getInfoFromJSONContent(jContent, info)
        except:
            raise
        else:
            return result

    def readUserDataFromServer(self, data_type="UserData"):
        """Calls an update function in the game and processes the received user data."""
        try:
            response, content = self.__sendRequest('ajax/menu-update.php')
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForSuccess(content)
        except:
            raise
        else:
            if data_type == "UserData":
                return self.__getUserDataFromJSONContent(jContent)
            else:
                return jContent

    def getPlantsToWaterInGarden(self, gardenID):
        """
        Retrieves all planted fields in the garden with the number gardenID,
        which can also be watered, and returns them.
        """
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={str(self.__token)}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
        except:
            raise
        else:
            return self.__findPlantsToBeWateredFromJSONContent(jContent)

    def waterPlantInGarden(self, garden, field, fieldsToWater):
        """Waters the plant field with the size fieldsToWater in the garden."""
        try:
            address =   f'save/wasser.php?feld[]={str(field)}&felder[]={fieldsToWater}' \
                        f'&cid={self.__token}&garden={str(garden)}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            self.__generateYAMLContentAndCheckForSuccess(content.decode('UTF-8'))
        except:
            raise

    def getPlantsToWaterInAquaGarden(self):
        """
        Retrieves all planted fields in the water garden that can also be watered and returns them.
        """
        try:
            response, content = self.__sendRequest(f'ajax/ajax.php?do=watergardenGetGarden&token={self.__token}')
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return self.__findPlantsToBeWateredFromJSONContent(jContent)
        except:
            raise

    def waterPlantInAquaGarden(self, field, fieldsToWater):
        """Waters all plants in the water garden."""
        listFieldsToWater = fieldsToWater.split(',')

        sFields = ''
        for i in listFieldsToWater:
            sFields += f'&water[]={i}'

        try:
            address = f'ajax/ajax.php?do=watergardenCache{sFields}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise

    def isHoneyFarmAvailable(self, userLevel):
        if not (userLevel < 10):
            try:
                response, content = self.__sendRequest(f'ajax/ajax.php?do=citymap_init&token={self.__token}')
                self.__checkIfHTTPStateIsOK(response)
                jContent = self.__generateJSONContentAndCheckForOK(content)
                return jContent['data']['location']['bees']['bought'] == 1
            except:
                raise
        else:
            return False

    def isAquaGardenAvailable(self, userLevel):
        """
        Function determines whether an Aqua Garden is available.
        This requires reaching a minimum level of 19 and then unlocking it.
        Unlocking is checked based on achievements in the game.
        """
        if not (userLevel < 19):
            try:
                response, content = self.__sendRequest(f'ajax/achievements.php?token={self.__token}')
                self.__checkIfHTTPStateIsOK(response)
                jContent = self.__generateJSONContentAndCheckForOK(content)
            except:
                raise
            else:
                result = re.search(r'trophy_54.png\);[^;]*(gray)[^;^class$]*class', jContent['html'])
                return result is None
        else:
            return False

    def isBonsaiFarmAvailable(self, userLevel):
        if not (userLevel < 10):
            try:
                response, content = self.__sendRequest(f'ajax/ajax.php?do=citymap_init&token={self.__token}')
                self.__checkIfHTTPStateIsOK(response)
                jContent = self.__generateJSONContentAndCheckForOK(content)
                if 'bonsai' in jContent['data']['location']:
                    if jContent['data']['location']['bonsai']['bought'] == 1:
                        return True
                    else:
                        return False
                else:
                    return False
            except:
                raise
        else:
            return False

    def isCityParkAvailable(self, userLevel):
        return userLevel >= 5

    # TODO: What happens when a garden is added (parallel sessions in the browser and bot)? Global update function?

    def checkIfEmailAddressIsConfirmed(self):
        """Checks if the email address in the profile is confirmed."""
        try:
            response, content = self.__sendRequest('user/profile.php')
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise
        else:
            result = re.search(r'Unconfirmed Email:', content)
            if result is None:
                return True
            else:
                return False

    def createNewMessageAndReturnResult(self):
        """Creates a new message and returns its ID needed for sending."""
        try:
            response, content = self.__sendRequest('messages/new.php')
            self.__checkIfHTTPStateIsOK(response)
            return content
        except:
            raise

    def sendMessageAndReturnResult(self, msg_id, msg_to, msg_subject, msg_body):
        """Sends a message with the provided parameters."""
        parameter = urlencode({'hpc': msg_id,
                            'msg_to': msg_to,
                            'msg_subject': msg_subject,
                            'msg_body': msg_body,
                            'msg_send': 'send'})
        try:
            response, content = self.__sendRequest('messages/new.php', 'POST', parameter)
            self.__checkIfHTTPStateIsOK(response)
            return content
        except:
            raise

    def getUsrList(self, start, end):
        """
        #TODO: finalize
        """
        userList = {'Nr': [], 'Gilde': [], 'Name': [], 'Punkte': []}
        # start must not be 0, otherwise -1 will be passed for the corrected index
        if start <= 0:
            start = 1

        if start == end or start > end:
            return False

        startCorr = start - 1
        calls = int(math.ceil(float(end - start) / 100))

        print(calls)
        for i in range(calls):
            print(i)
            try:
                address =   f'ajax/ajax.php?do=statsGetStats&which=1&start={str(startCorr)}' \
                            f'&showMe=0&additional=0&token={self.__token}'
                response, content = self.__sendRequest(address)
                self.__checkIfHTTPStateIsOK(response)
                jContent = self.__generateJSONContentAndCheckForOK(content)
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

            startCorr = startCorr + 100

        return userList

    def getEmptyFieldsOfGarden(self, gardenID):
        """Returns all empty fields of a garden."""
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            emptyFields = self.__findEmptyFieldsFromJSONContent(jContent)
        except:
            raise
        else:
            return emptyFields

    def getWeedFieldsOfGarden(self, gardenID):
        """Returns all weed fields of a garden."""
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            weedFields = self.__findWeedFieldsFromJSONContent(jContent)
        except:
            raise
        else:
            return weedFields

    def getGrowingPlantsOfGarden(self, gardenID):
        """Returns all fields with growing plants of a garden."""
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            growingPlants = self.__findGrowingPlantsFromJSONContent(jContent)
        except:
            raise
        else:
            return growingPlants

    def getEmptyFieldsAqua(self):
        try:
            address = f'ajax/ajax.php?do=watergardenGetGarden&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            emptyAquaFields = self.__findEmptyAquaFieldsFromJSONContent(jContent)
        except:
            raise
        else:
            return emptyAquaFields

    def harvestGarden(self, gardenID):
        """Erntet alle fertigen Pflanzen im Garten."""
        try:
            self._changeGarden(gardenID)
            address = f'ajax/ajax.php?do=gardenHarvestAll&token={self.__token}'
            response, content = self.__sendRequest(address)
            jContent = json.loads(content)

            if jContent['status'] == 'error':
                print(jContent['message'])
                self.__logHTTPConn.info(jContent['message'])
            elif jContent['status'] == 'ok':
                msg = jContent['harvestMsg'].replace('</div>', '\n').replace('&nbsp;', ' ')
                msg = re.sub('<div.*>', '', msg)
                msg = re.sub('x[ \n]*', 'x ', msg)
                msg = msg.strip()
                if 'biogas' in jContent:
                    biogas = jContent['biogas']
                    msg = msg + f"\n{biogas} Gartenabfälle"
                if 'eventitems' in jContent:
                    eventitems = jContent['collectevent']
                    msg = msg + f"\n{eventitems} Eventitems" #TODO check which event is active
                print(msg)
                self.__logHTTPConn.info(msg)
        except:
            raise

    def harvestAquaGarden(self):
        """Erntet alle fertigen Pflanzen im Garten."""
        try:
            address = f'ajax/ajax.php?do=watergardenHarvestAll&token={self.__token}'
            response, content = self.__sendRequest(address)
            jContent = json.loads(content)

            if jContent['status'] == 'error':
                print(jContent['message'])
                self.__logHTTPConn.info(jContent['message'])
            elif jContent['status'] == 'ok':
                msg = jContent['harvestMsg'].replace('</div>', '\n').replace('&nbsp;', ' ')
                msg = re.sub('<div.*>', '', msg)
                msg = re.sub('x[ \n]*', 'x ', msg)
                msg = msg.strip()
                print(msg)
                self.__logHTTPConn.info(msg)
        except:
            raise

    def growPlant(self, field, plant, gardenID, fields):
        """Baut eine Pflanze auf einem Feld an."""
        address =   f'save/pflanz.php?pflanze[]={str(plant)}&feld[]={str(field)}' \
                    f'&felder[]={fields}&cid={self.__token}&garden={str(gardenID)}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise

    def growAquaPlant(self, plant, field):
        """Baut eine Pflanze im Wassergarten an."""
        address = f'ajax/ajax.php?do=watergardenCache&plant[{plant}]={field}&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            self.__generateJSONContentAndCheckForOK(content)
        except:
            raise

    def getAllProductInformations(self):
        """Sammelt alle Produktinformationen und gibt diese zur Weiterverarbeitung zurück."""
        try:
            response, content = self.__sendRequest('main.php?page=garden')
            content = content.decode('UTF-8')
            self.__checkIfHTTPStateIsOK(response)
            reToken = re.search(r'ajax\.setToken\(\"(.*)\"\);', content)
            self.__token = reToken.group(1) #TODO: except, wenn token nicht aktualisiert werden kann
            reProducts = re.search(r'data_products = ({.*}});var', content)
            return reProducts.group(1)
        except:
            raise

    def getInventory(self):
        """Ermittelt den Lagerbestand und gibt diesen zurück."""
        try:
            address = f'ajax/updatelager.php?all=1&sort=1&type=honey&token={self.__token}'
            response, content = self.__sendRequest(address, 'POST')
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent['produkte']
        except:
            pass

    def getWimpsData(self, gardenID):
        """Get wimps data including wimp_id and list of products with amount"""
        try:
            self._changeGarden(gardenID)

            response, content = self.__sendRequest(f'ajax/verkaufajax.php?do=getAreaData&token={self.__token}')
            self.__checkIfHTTPStateIsOK(response)

            jContent = self.__generateJSONContentAndCheckForOK(content)
            return self.__findWimpsDataFromJSONContent(jContent)
        except:
            raise

    def sellWimpProducts(self, wimp_id):
        """
        Sell products to wimp with a given id
        @param wimp_id: str
        @return: dict of new balance of sold products
        """
        try:
            address = f'ajax/verkaufajax.php?do=accept&id={wimp_id}&token={self.__token}'
            response, content = self.__sendRequest(address, 'POST')
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent['newProductCounts']
        except:
            pass


    def declineWimp(self, wimp_id):
        """
        Decline wimp with a given id
        @param wimp_id: str
        @return: 'decline'
        """
        try:
            address = f'ajax/verkaufajax.php?do=decline&id={wimp_id}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent['action']
        except:
            pass

    def getNPCPrices(self):
        """Ermittelt aus der Wurzelimperium-Hilfe die NPC Preise aller Produkte."""
        response, content = self.__sendRequest('hilfe.php?item=2')
        self.__checkIfHTTPStateIsOK(response)
        content = content.decode('UTF-8').replace('Gärten & Regale', 'Gärten und Regale')
        dictNPCPrices = self.__parseNPCPricesFromHtml(content)
        return dictNPCPrices


    def getAllTradeableProductsFromOverview(self):
        """Gibt eine Liste zurück, welche Produkte handelbar sind."""
        try:
            response, content = self.__sendRequest('stadt/markt.php?show=overview')
            self.__checkIfHTTPStateIsOK(response)
            tradeableProducts = re.findall(r'markt\.php\?order=p&v=([0-9]{1,3})&filter=1', content)
        except:
            pass #TODO: exception definieren
        else:
            for i in range(0, len(tradeableProducts)):
                tradeableProducts[i] = int(tradeableProducts[i])

            return tradeableProducts


    def getOffersFromProduct(self, prod_id):
        """Gibt eine Liste mit allen Angeboten eines Produkts zurück."""
        nextPage = True
        iPage = 1
        listOffers = []
        while nextPage:
            nextPage = False

            try:
                address = f'stadt/markt.php?order=p&v={str(prod_id)}&filter=1&page={str(iPage)}'
                response, content = self.__sendRequest(address)
                self.__checkIfHTTPStateIsOK(response)
            except:
                pass #TODO: exception definieren
            else:
                html_file = io.BytesIO(content)
                html_tree = html.parse(html_file)
                root = html_tree.getroot()
                table = root.findall('./body/div/table/*')

                if table[1][0].text == 'Keine Angebote':
                    pass
                else:
                    #range von 1 bis länge-1, da erste Zeile Überschriften sind und die letzte Weiter/Zurück.
                    #Falls es mehrere seiten gibt.
                    for i in range(1, len(table)-1):
                        anzahl = table[i][0].text
                        anzahl = anzahl.encode('utf-8')
                        anzahl = anzahl.replace('.', '')

                        preis = table[i][3].text
                        preis = preis.encode('utf-8')
                        preis = preis.replace('\xc2\xa0wT', '')
                        preis = preis.replace('.', '')
                        preis = preis.replace(',', '.')
                        #produkt = table[i][1][0].text
                        #verkaeufer = table[i][2][0].text

                        listOffers.append([int(anzahl), float(preis)])

                    for element in table[len(table)-1][0]:
                        if 'weiter' in element.text:
                            nextPage = True
                            iPage = iPage + 1

        return listOffers

    def getBigQuestData(self):
        """Returns Data from Yearly Series of Quests"""
        try:
            address = f'ajax/ajax.php?do=bigquest_init&id=3&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent['data']
        except:
            pass

    def getDailyLoginBonus(self, day):
        """
        @param day: string (day of daily bonus)
        """
        try:
            address = f'ajax/ajax.php?do=dailyloginbonus_getreward&day={str(day)}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            return self.__generateJSONContentAndCheckForOK(content)
        except:
            pass

    def removeWeedOnFieldInGarden(self, gardenID, fieldID):
        """Befreit ein Feld im Garten von Unkraut."""
        self._changeGarden(gardenID)
        try:
            response, content = self.__sendRequest(f'save/abriss.php?tile={fieldID}', 'POST')
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForSuccess(content)
            return jContent['success']
        except:
            raise

    def removeWeedOnFieldInAquaGarden(self, gardenID, fieldID):
        """Befreit ein Feld im Garten von Unkraut."""
        self._changeGarden(gardenID)
        try:
            response, content = self.__sendRequest(f'save/abriss.php?tile={fieldID}', 'POST')
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForSuccess(content)
            return jContent['success']
        except:
            raise

    def initInfinityQuest(self):
        headers = self.__getHeaders()
        server = self.__getServer()
        adresse = f'{server}ajax/ajax.php?do=infinite_quest_get&token={self.__token}'
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            pass

    def sendInfinityQuest(self, questnr, product, amount):
        try:
            address =   f'ajax/ajax.php?do=infinite_quest_entry&pid={product}' \
                        f'&amount={amount}&questnr={questnr}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            pass

    def __getAvailableHives(self, jContent):
        """Sucht im JSON Content nach verfügbaren Bienenstöcken und gibt diese zurück."""
        availableHives = []

        for hive in jContent['data']['data']['hives']:
            if "blocked" not in jContent['data']['data']['hives'][hive]:
                availableHives.append(int(hive))

        # Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(availableHives) > 0:
            availableHives.sort(reverse=False)

        return availableHives

    def __getHiveType(self, jContent):
        """Sucht im JSON Content nach dem Typ der Bienenstöcke und gibt diese zurück."""
        hiveType = []

        for hive in jContent['data']['data']['hives']:
            if "blocked" not in jContent['data']['data']['hives'][hive]:
                hiveType.append(int(hive))

        # Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(hiveType) > 0:
            hiveType.sort(reverse=False)

        return hiveType

    def __getHoneyQuest(self, jContent):
        """Sucht im JSON Content nach verfügbaren Bienenquesten und gibt diese zurück."""
        honeyQuest = {}
        i = 1
        for course in jContent['questData']['products']:
            new = {i: {'pid': course['pid'], 'type': course['name']}}
            honeyQuest.update(new)
            i = i + 1
        return honeyQuest

    def getHoneyFarmInfos(self):
        """Funktion ermittelt, alle wichtigen Infos des Bienengarten und gibt diese aus."""
        try:
            response, content = self.__sendRequest(f'ajax/ajax.php?do=bees_init&token={self.__token}')
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            honeyQuestNr = jContent['questnr']
            honeyQuest = self.__getHoneyQuest(jContent)
            hives = self.__getAvailableHives(jContent)
            hivetype = self.__getHiveType(jContent)
            return honeyQuestNr, honeyQuest, hives, hivetype
        except:
            raise

    def harvestBienen(self):
        """Erntet den vollen Honigtopf"""

        try:
            response, content = self.__sendRequest(f'ajax/ajax.php?do=bees_fill&token={self.__token}')
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise

    def changeHivesTypeQuest(self, hive, Questanforderung):
        """Ändert den Typ vom Bienenstock auf die Questanforderung."""

        try:
            address =   f'ajax/ajax.php?do=bees_changehiveproduct&id={str(hive)}' \
                        f'&pid={str(Questanforderung)}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
        except:
            pass

    def sendeBienen(self, hive):
        """Sendet die Bienen für 2 Stunden"""
        #TODO: Check if bee is sended, sometimes 1 hives got skipped
        try:
            address = f'ajax/ajax.php?do=bees_startflight&id={str(hive)}&tour=1&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
        except:
            pass

    #Bonsai
    def bonsaiInit(self):
        """selects bonsaigarden returns JSON content(status, data, init, questnr, questData, quest)"""
        address = f'ajax/ajax.php?do=bonsai_init&token={self.__token}'
        try:
            response, content = self.__sendRequest(f'{address}')
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise

    def cutBonsaiBranch(self, slot, sissor, branch):
        """Cuts the branch from the bonsai and returns JSON content(status, data, branchclick, updateMenu)"""
        address =   f'ajax/ajax.php?do=bonsai_branch_click&slot={slot}' \
                    f'&scissor={sissor}&cache=%5B{branch}%5D&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise

    def finishBonsai(self, slot):
        """finishes bonsai to the bonsaigarden and returns JSON content"""
        address =   f'ajax/ajax.php?do=bonsai_finish_breed&slot={slot}&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise

    def buyAndPlaceBonsaiItem(self, item, pack, slot):
        """
        buys and places an item from the bonsai shop and returns JSON content

        Parameters
        -------------
            slot: 0-10; if 0, item stays in storage
            item:
                bonsais: 1-10 (Mädchenkiefer, Mangrove, Geldbaum, Fichten-Wald, Zypresse, Wacholder, Eiche, ...),
                pots: 11-20 (Einfache Schale, ...),
                scissors: 21-24 (Normale Schere, ...)
            pack:
                1, 5, 10 for bonsais or pots;
                1, 2, 3, 4 for 10, 50, 100, 500 scissors
        """
        address = f'ajax/ajax.php?do=bonsai_buy_item&item={item}&pack={pack}&slot={slot}&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise

    def placeBonsaiItem(self, id, slot):
        """
        places an item from the internal storage and returns JSON content

        Parameters
        -------------
            id: item id from internal storage --> has to be determined individually
            slot: 0-10; if 0, item stays in storage
        """
        address = f'ajax/ajax.php?do=bonsai_set_item&id={id}&slot={slot}&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise

# Stadtpark
    def initPark(self):
        """activate the park and return JSON content(status, data, init, questnr, questData, quest)"""
        address = f'ajax/ajax.php?do=park_init&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise

    def initCashPoint(self): #TODO: usecase?!
        """open the cashpoint and return JSON content(status, data, initcashpoint)"""
        address = f'ajax/ajax.php?do=park_initcashpoint&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent ### return jContent["data"]["data"]["cashpoint"] contains money, points, parkpoints
        except:
            raise
        
    def collectCashPointFromPark(self):
        """collect the rewards from the cashpoint and return JSON content(status, data, clearcashpoint, updateMenu)"""
        address = f'ajax/ajax.php?do=park_clearcashpoint&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise

    def renewItemInPark(self, tile, parkID=1):
        """renew an item on the given tile in the park and return JSON content(status, data, renewitem, updateMenu)"""
        address = f'ajax/ajax.php?do=park_renewitem&parkid={parkID}&tile={tile}&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise

# Shop
    def buyFromShop(self, shop: int, productId: int, amount: int = 1):
        parameter = urlencode({'s': shop,
                               'page': 1,
                               'change_page_only': 0,
                               'produkt[0]': productId,
                               'anzahl[0]': amount
                               })
        try:
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            response, content = self.__sendRequest(f'stadt/shop.php?s={shop}', 'POST', parameter, header)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise

    def buyFromAquaShop(self, productId: int, amount: int = 1):
        adresse = f'ajax/ajax.php?products={productId}:{amount}&do=shopBuyProducts&type=aqua&token={self.__token}'

        try:
            response, content = self.__sendRequest(f'{adresse}')
            self.__checkIfHTTPStateIsOK(response)
        except:
            return ''

class HTTPStateError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class JSONError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class HTTPRequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class YAMLError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
