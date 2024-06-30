#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from urllib.parse import urlencode
import json, re, httplib2, yaml, time, logging, math, i18n
from http.cookies import SimpleCookie
from src.Session import Session
from lxml import etree

i18n.load_path.append('lang')

# Defines
HTTP_STATE_OK = 200
HTTP_STATE_FOUND = 302 # moved temporarily

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
        self.__Session = Session()
        self.__token = None
        self.__userID = None
        self.__cookie = None
        self.__unr = None
        self.__portunr = None

    def __del__(self):
        self.__Session = None
        self.__token = None
        self.__userID = None
        self.__unr = None
        self.__portunr = None

    def token(self):
        return self.__token

    def sendRequest(self, address: str, method: str = 'GET', body = None, headers: dict = {}):
        return self.__sendRequest(address, method, body, headers)

    def __sendRequest(self, address: str, method: str = 'GET', body = None, headers: dict = {}):
        uri = self.__getServer() + address
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
        return self.__checkIfHTTPStateIsOK(response)

    def __checkIfHTTPStateIsOK(self, response):
        """Prüft, ob der Status der HTTP Anfrage OK ist."""
        if not (response['status'] == str(HTTP_STATE_OK)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht OK')


    def __checkIfHTTPStateIsFOUND(self, response):
        """Prüft, ob der Status der HTTP Anfrage FOUND ist."""
        if not (response['status'] == str(HTTP_STATE_FOUND)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht FOUND')


    def __generateJSONContentAndCheckForSuccess(self, content):
        """Aufbereitung und Prüfung der vom Server empfangenen JSON Daten."""
        j_content = json.loads(content)
        if j_content['success'] == 1:
            return j_content
        else:
            raise JSONError()

    def generateJSONContentAndCheckForOK(self, content: str):
        return self.__generateJSONContentAndCheckForOK(content)

    def __generateJSONContentAndCheckForOK(self, content: str):
        """Aufbereitung und Prüfung der vom Server empfangenen JSON Daten."""
        j_content = json.loads(content)
        if j_content['status'] == 'ok':
            return j_content
        else:
            raise JSONError()


    def __isFieldWatered(self, jContent, fieldID):
        """
        Ermittelt, ob ein Feld fieldID gegossen ist und gibt True/False zurück.
        Ist das Datum der Bewässerung 0, wurde das Feld noch nie gegossen.
        Eine Bewässerung hält 24 Stunden an. Liegt die Zeit der letzten Bewässerung
        also 24 Stunden + 30 Sekunden (Sicherheit) zurück, wurde das Feld zwar bereits gegossen,
        kann jedoch wieder gegossen werden.
        """
        oneDayInSeconds = (24*60*60) + 30
        currentTimeInSeconds = time.time()
        waterDateInSeconds = int(jContent['water'][fieldID-1][1])

        if waterDateInSeconds == '0' or (currentTimeInSeconds - waterDateInSeconds) > oneDayInSeconds:
            return False
        else:
            return True

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


    def __findPlantsToBeWateredFromJSONContent(self, jContent):
        """Sucht im JSON Content nach Pflanzen die bewässert werden können und gibt diese inkl. der Pflanzengröße zurück."""
        plantsToBeWatered = {'fieldID': [], 'sx': [], 'sy': []}
        for field in range(0, len(jContent['grow'])):
            plantedFieldID = jContent['grow'][field][0]
            plantSize = jContent['garden'][str(plantedFieldID)][9]
            splittedPlantSize = str(plantSize).split('x')
            sx = splittedPlantSize[0]
            sy = splittedPlantSize[1]

            if not self.__isFieldWatered(jContent, plantedFieldID):
                fieldIDToBeWatered = plantedFieldID
                plantsToBeWatered['fieldID'].append(fieldIDToBeWatered)
                plantsToBeWatered['sx'].append(int(sx))
                plantsToBeWatered['sy'].append(int(sy))

        return plantsToBeWatered

    def __findEmptyFieldsFromJSONContent(self, jContent):
        """Sucht im JSON Content nach Felder die leer sind und gibt diese zurück."""
        emptyFields = []

        for field in jContent['garden']:
            if jContent['garden'][field][0] == 0:
                emptyFields.append(int(field))

        #Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(emptyFields) > 0:
            emptyFields.sort(reverse=False)

        return emptyFields

    def __findWeedFieldsFromJSONContent(self, jContent):
        """Sucht im JSON Content nach Felder die mit Unkraut befallen sind und gibt diese zurück."""
        weedFields = {}

        # 41 Unkraut, 42 Baumstumpf, 43 Stein, 45 Maulwurf
        for field in jContent['garden']:
            if jContent['garden'][field][0] in [41, 42, 43, 45]:
                weedFields[int(field)] = float(jContent['garden'][field][6])

        #Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(weedFields) > 0:
            weedFields = {key: value for key, value in sorted(weedFields.items(), key=lambda item: item[1])}

        return weedFields

    def __findGrowingPlantsFromJSONContent(self, jContent):
        """Returns list of growing plants from JSON content"""
        growingPlants = []
        for field in jContent['grow']:
            growingPlants.append(field[1])
        return growingPlants

    def __findEmptyAquaFieldsFromJSONContent(self, jContent):
        emptyAquaFields = []
        for field in jContent['garden']:
            if jContent['garden'][field][0] == 0:
                emptyAquaFields.append(int(field))
        # Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(emptyAquaFields) > 0:
            emptyAquaFields.sort(reverse=False)
        return emptyAquaFields

    def __generateYAMLContentAndCheckForSuccess(self, content: str):
        """Aufbereitung und Prüfung der vom Server empfangenen YAML Daten auf Erfolg."""
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        yContent = yaml.load(content, Loader=yaml.FullLoader)

        if yContent['success'] != 1:
            raise YAMLError()


    def __generateYAMLContentAndCheckStatusForOK(self, content):
        """Aufbereitung und Prüfung der vom Server empfangenen YAML Daten auf iO Status."""
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        yContent = yaml.load(content, Loader=yaml.FullLoader)

        if yContent['status'] != 'ok':
            raise YAMLError()

    def _changeGarden(self, gardenID):
        """Wechselt den Garten."""
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            return self.__generateJSONContentAndCheckForOK(content)
        except:
            raise

    def __parseNPCPricesFromHtml(self, html_data):
        """Parsen aller NPC Preise aus dem HTML Skript der Spielehilfe."""
        #ElementTree benötigt eine Datei zum Parsen.
        #Mit BytesIO wird eine Datei im Speicher angelegt, nicht auf der Festplatte.
        my_parser = etree.HTMLParser(recover=True)
        html_tree = etree.fromstring(str(html_data), parser=my_parser)

        table = html_tree.find('./body/div[@id="content"]/table')

        dictResult = {}

        for row in table.iter('tr'):

            produktname = row[0].text
            npc_preis = row[1].text

            #Bei der Tabellenüberschrift ist der Text None
            if produktname != None and npc_preis != None:
                # NPC-Preis aufbereiten
                npc_preis = str(npc_preis)
                npc_preis = npc_preis[0:len(npc_preis) - 3]
                npc_preis = npc_preis.replace('.', '')
                npc_preis = npc_preis.replace(',', '.')
                npc_preis = npc_preis.replace(' ', '')
                npc_preis = npc_preis.strip()
                if len(npc_preis) == 0:
                    npc_preis = None
                else:
                    npc_preis = float(npc_preis)

                dictResult[produktname] = npc_preis

        return dictResult

    def __getHeaders(self):
        headers = {'Cookie': f'PHPSESSID={self.__Session.getSessionID()};wunr={self.__userID}',
                   'Connection': 'Keep-Alive'}
        return headers

    def __getServer(self):
        return f'http://s{self.__Session.getServer()}{self.__Session.getServerURL()}'


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
            self.__Session.openSession(cookie['PHPSESSID'].value, str(loginDaten.server), serverURL)
            self.__cookie = cookie
            self.__userID = self.__unr

    def get_user_id(self):
        """Gibt die wunr als userID zurück die beim Login über das Cookie erhalten wurde."""
        return self.__userID


    def logOut(self):
        """Logout des Spielers inkl. Löschen der Session."""
        #TODO: Was passiert beim Logout einer bereits ausgeloggten Session
        try: #content ist beim Logout leer
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
        Returns different parameters from user's stats'
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
        """Ruft eine Updatefunktion im Spiel auf und verarbeitet die empfangenen userdaten."""
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
        Ermittelt alle bepflanzten Felder im Garten mit der Nummer gardenID,
        die auch gegossen werden können und gibt diese zurück.
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


    def waterPlantInGarden(self, iGarten, iField, sFieldsToWater):
        """Bewässert die Pflanze iField mit der Größe sSize im Garten iGarten."""
        try:
            address =   f'save/wasser.php?feld[]={str(iField)}&felder[]={sFieldsToWater}' \
                        f'&cid={self.__token}&garden={str(iGarten)}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            self.__generateYAMLContentAndCheckForSuccess(content.decode('UTF-8'))
        except:
            raise


    def getPlantsToWaterInAquaGarden(self):
        """
        Ermittelt alle bepflanzten Felder im Wassergartens, die auch gegossen werden können und gibt diese zurück.
        """
        try:
            response, content = self.__sendRequest(f'ajax/ajax.php?do=watergardenGetGarden&token={self.__token}')
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            return self.__findPlantsToBeWateredFromJSONContent(jContent)
        except:
            raise


    def waterPlantInAquaGarden(self, iField, sFieldsToWater):
        """Gießt alle Pflanzen im Wassergarten"""
        listFieldsToWater = sFieldsToWater.split(',')

        sFields = ''
        for i in listFieldsToWater:
            sFields += f'&water[]={i}'

        try:
            address = f'ajax/ajax.php?do=watergardenCache{sFields}&token={self.__token}'
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise

    #TODO: Was passiert wenn ein Garten hinzukommt (parallele Sitzungen im Browser und Bot)? Globale Aktualisierungsfunktion?

    def createNewMessageAndReturnResult(self):
        """Erstellt eine neue Nachricht und gibt deren ID zurück, die für das Senden benötigt wird."""
        try:
            response, content = self.__sendRequest('nachrichten/new.php')
            self.__checkIfHTTPStateIsOK(response)
            return content
        except:
            raise


    def sendMessageAndReturnResult(self, msg_id, msg_to, msg_subject, msg_body):
        """Verschickt eine Nachricht mit den übergebenen Parametern."""
        parameter = urlencode({'hpc': msg_id,
                               'msg_to': msg_to,
                               'msg_subject': msg_subject,
                               'msg_body': msg_body,
                               'msg_send': 'senden'})
        try:
            response, content = self.__sendRequest('nachrichten/new.php', 'POST', parameter)
            self.__checkIfHTTPStateIsOK(response)
            return content
        except:
            raise


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

            iStartCorr = iStartCorr + 100

        return userList

    def getEmptyFieldsOfGarden(self, gardenID):
        """Gibt alle leeren Felder eines Gartens zurück."""
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
        """Gibt alle Unkraut-Felder eines Gartens zurück."""
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

    def getNPCPrices(self):
        """Ermittelt aus der Wurzelimperium-Hilfe die NPC Preise aller Produkte."""
        response, content = self.__sendRequest('hilfe.php?item=2')
        self.__checkIfHTTPStateIsOK(response)
        content = content.decode('UTF-8').replace('Gärten & Regale', 'Gärten und Regale')
        dictNPCPrices = self.__parseNPCPricesFromHtml(content)
        return dictNPCPrices

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

    # Guild
    def init_guild(self):
        address = f"ajax/ajax.php?do=gildeGetData&&token={self.__token}"
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            return self.__generateJSONContentAndCheckForOK(content)
        except:
            raise

    def collect_lucky_mole(self, guild_id):
        address = f"ajax/ajax.php?do=gilde&action=luckyWurf&id={guild_id}&token={self.__token}"
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            return self.__generateJSONContentAndCheckForOK(content)
        except:
            raise

    # Herb garden
    def init_herb_garden(self):
        address = f"ajax/ajax.php?do=herb&action=getGarden&token={self.__token}"
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            return self.__generateJSONContentAndCheckForOK(content)
        except:
            raise

    def harvest_herb_garden(self):
        address = f'ajax/ajax.php?do=gardenHarvestAll&token={self.__token}'
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            return json.loads(content)
        except:
            raise

    def remove_weed_in_herb_garden(self):
        address = f"ajax/ajax.php?do=herb&action=removeHerbWeed&token={self.__token}"
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            return self.__generateJSONContentAndCheckForOK(content)
        except:
            raise

    def exchange_herb(self, plantID):
        address = f"ajax/ajax.php?do=herbEvent&action=exchange&plantid={plantID}&token={self.__token}"
        try:
            response, content = self.__sendRequest(address)
            self.__checkIfHTTPStateIsOK(response)
            return self.__generateJSONContentAndCheckForOK(content)
        except:
            raise

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
