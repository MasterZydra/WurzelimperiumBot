#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from urllib.parse import urlencode
import json, re, httplib2
from http.cookies import SimpleCookie
from src.Session import Session
import yaml, time, logging, math, io
import xml.etree.ElementTree as eTree
from lxml import html

#Defines
HTTP_STATE_CONTINUE            = 100
HTTP_STATE_SWITCHING_PROTOCOLS = 101
HTTP_STATE_PROCESSING          = 102
HTTP_STATE_OK                  = 200
HTTP_STATE_FOUND               = 302 #moved temporarily

class HTTPConnection(object):
    """
    Mit der Klasse HTTPConnection werden alle anfallenden HTTP-Verbindungen verarbeitet.
    """

    def __init__(self):
        self.__webclient = httplib2.Http(disable_ssl_certificate_validation=True)
        self.__webclient.follow_redirects = False
        self.__userAgent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 Vivaldi/2.2.1388.37'
        self.__logHTTPConn = logging.getLogger('bot.HTTPConn')
        self.__logHTTPConn.setLevel(logging.DEBUG)
        self.__Session = Session()
        self.__token = None
        self.__userID = None
        self.__unr = None
        self.__portunr = None


    def __del__(self):
        self.__Session = None
        self.__token = None
        self.__userID = None
        self.__unr = None
        self.__portunr = None


    def __getUserDataFromJSONContent(self, content):
        """
        Ermittelt userdaten aus JSON Content.
        """
        userData = {}
        userData['bar'] = str(content['bar'])
        userData['points'] = int(content['points'])
        userData['coins'] = int(content['coins'])
        userData['level'] = str(content['level'])
        userData['levelnr'] = int(content['levelnr'])
        userData['mail'] = int(content['mail'])
        userData['contracts'] = int(content['contracts'])
        userData['g_tag'] = str(content['g_tag'])
        userData['time'] = int(content['time'])
        return userData


    def __checkIfHTTPStateIsOK(self, response):
        """
        Prüft, ob der Status der HTTP Anfrage OK ist.
        """
        if not (response['status'] == str(HTTP_STATE_OK)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht OK')


    def __checkIfHTTPStateIsFOUND(self, response):
        """
        Prüft, ob der Status der HTTP Anfrage FOUND ist.
        """
        if not (response['status'] == str(HTTP_STATE_FOUND)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht FOUND')


    def __generateJSONContentAndCheckForSuccess(self, content):
        """
        Aufbereitung und Prüfung der vom Server empfangenen JSON Daten.
        """
        jContent = json.loads(content)
        if (jContent['success'] == 1): return jContent
        else: raise JSONError()


    def __generateJSONContentAndCheckForOK(self, content : str):
        """
        Aufbereitung und Prüfung der vom Server empfangenen JSON Daten.
        """
        jContent = json.loads(content)
        if (jContent['status'] == 'ok'): return jContent
        else: raise JSONError()


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

        if waterDateInSeconds == '0': return False
        elif (currentTimeInSeconds - waterDateInSeconds) > oneDayInSeconds: return False
        else: return True


    def __getTokenFromURL(self, url):
        """
        Ermittelt aus einer übergebenen URL den security token.
        """
        #token extrahieren
        split = re.search(r'https://.*/logw.php.*token=([a-f0-9]{32})', url)
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
    
    def __getTokenFromURLPORT(self, url):
        """
        Ermittelt aus einer übergebenen URL den security token.
        """
        # token extrahieren
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
        """
        Ermittelt aus einer übergebenen URL den security token.
        """
        # token extrahieren
        split = re.search(r'.*portal/port_logw.php.*unr=([a-f0-9]{6}).*port', url)
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
        """
        Ermittelt aus einer übergebenen URL den security token.
        """
        # token extrahieren
        split = re.search(r'.*portal/port_logw.php.*portunr=([a-f0-9]{7})', url)
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


    def __getUserNameFromJSONContent(self, jContent):
        """
        Sucht im übergebenen JSON Objekt nach dem Usernamen und gibt diesen zurück.
        """
        result = False
        for i in range(0, len(jContent['table'])):
            sUserName = str(jContent['table'][i])  
            if 'Spielername' in sUserName:
                sUserName = sUserName.replace('<tr>', '')
                sUserName = sUserName.replace('<td>', '')
                sUserName = sUserName.replace('</tr>', '')
                sUserName = sUserName.replace('</td>', '')
                sUserName = sUserName.replace('Spielername', '')
                sUserName = sUserName.replace('&nbsp;', '')
                sUserName = sUserName.strip()
                result = True
                break
        if result:
            return sUserName
        else:
            self.__logHTTPConn.debug(jContent['table'])
            raise JSONError('Spielername nicht gefunden.')


    def __getNumberOfGardensFromJSONContent(self, jContent):
        """
        Sucht im übergebenen JSON Objekt nach der Anzahl der Gärten und gibt diese zurück.
        """
        result = False
        for i in range(0, len(jContent['table'])):
            sGartenAnz = str(jContent['table'][i])
            if 'Gärten' in sGartenAnz:
                sGartenAnz = sGartenAnz.replace('<tr>', '')
                sGartenAnz = sGartenAnz.replace('<td>', '')
                sGartenAnz = sGartenAnz.replace('</tr>', '')
                sGartenAnz = sGartenAnz.replace('</td>', '')
                sGartenAnz = sGartenAnz.replace('Gärten', '')
                sGartenAnz = sGartenAnz.strip()
                iGartenAnz = int(sGartenAnz)
                result = True
                break

        if result:
            return iGartenAnz
        else:
            self.__logHTTPConn.debug(jContent['table'])
            raise JSONError('Anzahl der Gärten nicht gefunden.')


    def __checkIfSessionIsDeleted(self, cookie):
        """
        Prüft, ob die Session gelöscht wurde.
        """
        if not (cookie['PHPSESSID'].value == 'deleted'):
            self.__logHTTPConn.debug('SessionID: ' + cookie['PHPSESSID'].value)
            raise HTTPRequestError('Session wurde nicht gelöscht')


    def __findPlantsToBeWateredFromJSONContent(self, jContent):
        """
        Sucht im JSON Content nach Pflanzen die bewässert werden können und gibt diese inkl. der Pflanzengröße zurück.
        """
        plantsToBeWatered = {'fieldID':[], 'sx':[], 'sy':[]}
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
        """
        Sucht im JSON Content nach Felder die leer sind und gibt diese zurück.
        """
        emptyFields = []
        
        for field in jContent['garden']:
            if jContent['garden'][field][0] == 0:
                emptyFields.append(int(field))

        #Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(emptyFields) > 0:
            emptyFields.sort(reverse=False)

        return emptyFields

    def __findWeedFieldsFromJSONContent(self, jContent):
        """
        Sucht im JSON Content nach Felder die mit Unkraut befallen sind und gibt diese zurück.
        """
        weedFields = []
        
        # 41 Unkraut, 42 Baumstumpf, 43 Stein, 45 Maulwurf
        for field in jContent['garden']:
            if jContent['garden'][field][0] in [41, 42, 43, 45]:
                weedFields.append(int(field))

        #Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(weedFields) > 0:
            weedFields.sort(reverse=False)

        return weedFields
    
    def __findEmptyAquaFieldsFromJSONContent(self, jContent):

        emptyAquaFields = []

        for field in jContent['garden']:
            if jContent['garden'][field][0] == 0:
                emptyAquaFields.append(int(field))

        # Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(emptyAquaFields) > 0:
            emptyAquaFields.sort(reverse=False)

        return emptyAquaFields

    def __generateYAMLContentAndCheckForSuccess(self, content : str):
        """
        Aufbereitung und Prüfung der vom Server empfangenen YAML Daten auf Erfolg.
        """
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        yContent = yaml.load(content, Loader=yaml.FullLoader)
        
        if (yContent['success'] != 1):
            raise YAMLError()


    def __generateYAMLContentAndCheckStatusForOK(self, content):
        """
        Aufbereitung und Prüfung der vom Server empfangenen YAML Daten auf iO Status.
        """
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        yContent = yaml.load(content, Loader=yaml.FullLoader)
        
        if (yContent['status'] != 'ok'):
            raise YAMLError()

    def __changeGarden(self, gardenID):
        """
        Wechselt den Garten.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/ajax/' + \
                  f'ajax.php?do=changeGarden&garden={gardenID}&token={self.__token}'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise
        else:
            pass


    def __parseNPCPricesFromHtml(self, html):
        """
        Parsen aller NPC Preise aus dem HTML Skript der Spielehilfe.
        """
        #ElementTree benötigt eine Datei zum Parsen.
        #Mit BytesIO wird eine Datei im Speicher angelegt, nicht auf der Festplatte.
        html_file = io.BytesIO(html)
        
        html_tree = eTree.parse(html_file)
        root = html_tree.getroot()
        table = root.find('./body/div[@id="content"]/table')
        
        dictResult = {}
        
        for row in table.iter('tr'):
            
            produktname = row[0].text
            npc_preis = row[1].text
            
            #Bei der Tabellenüberschrift ist der Text None
            if produktname != None and npc_preis != None:
                # NPC-Preis aufbereiten
                npc_preis = str(npc_preis)
                npc_preis = npc_preis.replace(' wT', '')
                npc_preis = npc_preis.replace('.', '')
                npc_preis = npc_preis.replace(',', '.')
                npc_preis = npc_preis.strip()
                if '-' in npc_preis:
                    npc_preis = None
                else:
                    npc_preis = float(npc_preis)
                    
                dictResult[produktname] = npc_preis
                
        return dictResult

    def logIn(self, loginDaten):
        """
        Führt einen login durch und öffnet eine Session.
        """
        parameter = urlencode({'do': 'login',
                            'server': 'server' + str(loginDaten.server),
                            'user': loginDaten.user,
                            'pass': loginDaten.password}) 
    
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Connection': 'keep-alive'}

        try:
            response, content = self.__webclient.request('https://www.wurzelimperium.de/dispatch.php', \
                                                         'POST', \
                                                         parameter, \
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
            self.__Session.openSession(cookie['PHPSESSID'].value, str(loginDaten.server))
            self.__userID = cookie['wunr'].value
            
    def logInPortal(self, loginDaten):
        """
        Führt einen login durch und öffnet eine Session.
        """
        parameter = urlencode({'portserver': 'server' + str(loginDaten.server),
                               'portname': loginDaten.user,
                               'portpass': loginDaten.password,
                               'portsubmit': 'Einloggen'})

        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Connection': 'keep-alive'}

        try:
            response, content = self.__webclient.request('https://www.wurzelimperium.de/portal/game2port_login.php', \
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
            loginadresse = 'https://s1.wurzelimperium.de/logw.php?port=1&unr=' + self.__unr + '&portunr=' + self.__portunr + '&hash=' + self.__token + '&sno=1'
            response, content = self.__webclient.request(loginadresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsFOUND(response)
        except:
            raise
        else:
            cookie = SimpleCookie(response['set-cookie'])
            self.__Session.openSession(cookie['PHPSESSID'].value, str(loginDaten.server), "s")
            self.__cookie = cookie
            self.__userID = self.__unr

    def getUserID(self):
        """
        Gibt die wunr als userID zurück die beim Login über das Cookie erhalten wurde.
        """
        return self.__userID


    def logOut(self):
        """
        Logout des Spielers inkl. Löschen der Session.
        """
        #TODO: Was passiert beim Logout einer bereits ausgeloggten Session
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + 'wunr=' + self.__userID}
        
        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/main.php?page=logout'
        
        try: #content ist beim Logout leer
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsFOUND(response)
            cookie = SimpleCookie(response['set-cookie'])
            self.__checkIfSessionIsDeleted(cookie)
        except:
            raise
        else:
            self.__del__()


    def getNumberOfGardens(self):
        """
        Ermittelt die Anzahl der Gärten und gibt diese als int zurück.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/ajax/' + \
                  f'ajax.php?do=statsGetStats&which=0&start=0&additional={self.__userID}&token={self.__token}'
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content.decode('UTF-8'))
            iNumber = self.__getNumberOfGardensFromJSONContent(jContent)
        except:
            raise
        else:
            return iNumber


    def getUserName(self): 
        """
        Ermittelt den Usernamen auf Basis der userID und gibt diesen als str zurück.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive',
                   'Referer':'http://s46.wurzelimperium.de/main.php?page=garden', 
                   'X-Requested-With':'X-Requested-With: XMLHttpRequest'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/' + \
                  f'ajax/ajax.php?do=statsGetStats&which=0&start=0&additional={self.__userID}&token={self.__token}'
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            userName = self.__getUserNameFromJSONContent(jContent)
        except:
            raise
        else:
            return userName


    def readUserDataFromServer(self):
        """
        Ruft eine Updatefunktion im Spiel auf und verarbeitet die empfangenen userdaten.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/ajax/menu-update.php'
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForSuccess(content)
        except:
            raise
        else:
            return self.__getUserDataFromJSONContent(jContent)


    def getPlantsToWaterInGarden(self, gardenID):
        """
        Ermittelt alle bepflanzten Felder im Garten mit der Nummer gardenID,
        die auch gegossen werden können und gibt diese zurück.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/' + \
                  f'ajax/ajax.php?do=changeGarden&garden={gardenID}&token={self.__token}'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
        except:
            raise
        else:
            return self.__findPlantsToBeWateredFromJSONContent(jContent)


    def waterPlantInGarden(self, iGarten, iField, sFieldsToWater):
        """
        Bewässert die Pflanze iField mit der Größe sSize im Garten iGarten.
        """

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/save/wasser.php?feld[]=' + \
                  f'{iField}&felder[]={sFieldsToWater}&cid={self.__token}&garden={iGarten}'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            self.__generateYAMLContentAndCheckForSuccess(content.decode('UTF-8'))
        except:
            raise


    def getPlantsToWaterInAquaGarden(self):
        """
        Ermittelt alle bepflanzten Felder im Wassergartens,
        die auch gegossen werden können und gibt diese zurück.
        """

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/' + \
                  f'ajax/ajax.php?do=watergardenGetGarden&token={self.__token}'
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
        except:
            raise
        else:
            return self.__findPlantsToBeWateredFromJSONContent(jContent)
        

    def waterPlantInAquaGarden(self, iField, sFieldsToWater):
        """
        Status:
        """

        listFieldsToWater = sFieldsToWater.split(',')
        
        sFields = ''
        for i in listFieldsToWater:
            sFields += f'&water[]={i}'

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/' + \
                  f'ajax/ajax.php?do=watergardenCache{sFields}&token={self.__token}'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            self.__generateYAMLContentAndCheckStatusForOK(content)
        except:
            raise


    def isHoneyFarmAvailable(self, iUserLevel):
        """
        Funktion ermittelt, ob die Imkerei verfügbar ist und gibt True/False zurück.
        Dazu muss ein Mindestlevel von 10 erreicht sein und diese dann freigeschaltet sein.
        Die Freischaltung wird anhand eines Geschenks im Spiel geprüft.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}' + \
                  f'.wurzelimperium.de/ajax/gettrophies.php?category=giver'
        
        if not (iUserLevel < 10):
            try:
                response, content = self.__webclient.request(adresse, 'GET', headers = headers)
                self.__checkIfHTTPStateIsOK(response)
                jContent = self.__generateJSONContentAndCheckForOK(content)
            except:
                raise
            else:
                if '316' in jContent['gifts']:
                    if (jContent['gifts']['316']['name'] == 'Bienen-Fan'):
                        return True
                    else:
                        return False
                else:
                    return False
        else:
            return False
        
    def isBonsaiAvailable(self, iUserLevel):
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=bonsai_init' + '&token=' + self.__token

        if not (iUserLevel < 10):
            try:
                response, content = self.__webclient.request(adresse, 'GET', headers=headers)
                self.__checkIfHTTPStateIsOK(response)
                jContent = self.__generateJSONContentAndCheckForOK(content)
                return True
            except:
                raise
        else:
            return False

    def isBirdPostAvailable(self, iUserLevel):
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=birds_init' + '&token=' + self.__token

        if not (iUserLevel < 10):
            try:
                response, content = self.__webclient.request(adresse, 'GET', headers=headers)
                self.__checkIfHTTPStateIsOK(response)
                jContent = self.__generateJSONContentAndCheckForOK(content)
                return True
            except:
                raise
        else:
            return False
            
    def isAquaGardenAvailable(self, iUserLevel):
        """
        Funktion ermittelt, ob ein Wassergarten verfügbar ist.
        Dazu muss ein Mindestlevel von 19 erreicht sein und dieser dann freigeschaltet sein.
        Die Freischaltung wird anhand der Errungenschaften im Spiel geprüft.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}' + \
                  f'.wurzelimperium.de/ajax/achievements.php?token={self.__token}'

        if not (iUserLevel < 19):
            try:
                response, content = self.__webclient.request(adresse, 'GET', headers = headers)
                self.__checkIfHTTPStateIsOK(response)
                jContent = self.__generateJSONContentAndCheckForOK(content)
            except:
                raise
            else:
                result = re.search(r'trophy_54.png\);[^;]*(gray)[^;^class$]*class', jContent['html'])
                if result == None:
                    return True
                else:
                    return False
        else:
            return False

    #TODO: Was passiert wenn ein Garten hinzukommt (parallele Sitzungen im Browser und Bot)? Globale Aktualisierungsfunktion?

    def checkIfEMailAdressIsConfirmed(self):
        """
        Prüft, ob die E-Mail Adresse im Profil bestätigt ist.
        """
        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/nutzer/profil.php'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise
        else:
            result = re.search(r'Unbestätigte Email:', content)
            if (result == None): return True
            else: return False


    def createNewMessageAndReturnResult(self):
        """
        Erstellt eine neue Nachricht und gibt deren ID zurück, die für das Senden benötigt wird.
		"""

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,\
                   'Content-type': 'application/x-www-form-urlencoded'}

        adress = f'http://s{self.__Session.getServer()}.wurzelimperium.de/nachrichten/new.php'
        
        try:
            response, content = self.__webclient.request(adress, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise
        else:
            return content


    def sendMessageAndReturnResult(self, msg_id, msg_to, msg_subject, msg_body):
        """
        Verschickt eine Nachricht mit den übergebenen Parametern.
        """

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,\
                   'Content-type': 'application/x-www-form-urlencoded'}

        adress = f'http://s{self.__Session.getServer()}.wurzelimperium.de/nachrichten/new.php'

        #Nachricht absenden
        parameter = urlencode({'hpc': msg_id,
                               'msg_to': msg_to,
                               'msg_subject': msg_subject,
                               'msg_body': msg_body,
                               'msg_send': 'senden'}) 
        try:
            response, content = self.__webclient.request(adress, 'POST', parameter, headers)
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
        if (iStart <= 0): iStart = 1
        
        if (iStart == iEnd or iStart > iEnd):
            return False
                
        iStartCorr = iStart - 1
        iCalls = int(math.ceil(float(iEnd-iStart)/100))
        
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID}
        print(iCalls)
        for i in range(iCalls):
            print(i)
            adress = f'http://s{self.__Session.getServer()}.wurzelimperium.de/ajax/ajax.php?do' + \
                     f'=statsGetStats&which=1&start={iStartCorr}&showMe=0&additional=0&token={self.__token}'
            try:
                response, content = self.__webclient.request(adress, 'GET', headers = headers)
                self.__checkIfHTTPStateIsOK(response)
                jContent = self.__generateJSONContentAndCheckForOK(content)
            except:
                raise
            else:
                try:
                    for j in jContent['table']:
                        result = re.search(r'<tr><td class=".*">(.*)<\/td><td class=".*tag">(.*)<\/td><td class=".*uname">([^<]*)<.*class=".*pkt">(.*)<\/td><\/tr>', j)
                        userList['Nr'].append(str(result.group(1)).replace('.', ''))
                        userList['Gilde'].append(str(result.group(2)))
                        userList['Name'].append(str(result.group(3).encode('utf-8')).replace('&nbsp;', ''))
                        userList['Punkte'].append(int(str(result.group(4).replace('.', ''))))
                except:
                    raise

            iStartCorr = iStartCorr + 100

        return userList

    def readStorageFromServer(self):

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID}

        adress = f'http://s{self.__Session.getServer()}.wurzelimperium.de/ajax/updatelager.php?all=1'

        try:
            response, content = self.__webclient.request(adress, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
        except:
            raise
        else:
            print(jContent['produkte'])

    def getEmptyFieldsOfGarden(self, gardenID):
        """
        Gibt alle leeren Felder eines Gartens zurück.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/' + \
                  f'ajax/ajax.php?do=changeGarden&garden={gardenID}&token={self.__token}'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            emptyFields = self.__findEmptyFieldsFromJSONContent(jContent)
        except:
            raise
        else:
            return emptyFields

    def getWeedFieldsOfGarden(self, gardenID):
        """
        Gibt alle Unkraut-Felder eines Gartens zurück.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/' + \
                  f'ajax/ajax.php?do=changeGarden&garden={gardenID}&token={self.__token}'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            weedFields = self.__findWeedFieldsFromJSONContent(jContent)
        except:
            raise
        else:
            return weedFields
        
    def getEmptyFieldsAqua(self):
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=watergardenGetGarden' + '&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            emptyAquaFields = self.__findEmptyAquaFieldsFromJSONContent(jContent)
        except:
            raise
        else:
            return emptyAquaFields

    def harvestGarden(self, gardenID):
        """
        Erntet alle fertigen Pflanzen im Garten.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
    
        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}' + \
                  f'.wurzelimperium.de/ajax/ajax.php?do=gardenHarvestAll&token={self.__token}'

        try:
            self.__changeGarden(gardenID)
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            jContent = json.loads(content)
            #print(content.decode('UTF-8'))

            if jContent['status'] == 'error':
                print(jContent['message'])
                self.__logHTTPConn.info(jContent['message'])
            elif jContent['status'] == 'ok':
                msg = jContent['harvestMsg'].replace('<div>', '').replace('</div>', '\n').replace('&nbsp;', ' ')
                msg = msg.strip()
                print(msg)
                self.__logHTTPConn.info(msg)
        except:
            raise
        else:
            pass

    def harvestAquaGarden(self):
        """
        Erntet alle fertigen Pflanzen im Garten.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
    
        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}' + \
                  f'.wurzelimperium.de/ajax/ajax.php?do=watergardenHarvestAll&token={self.__token}'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise
        else:
            pass

    def growPlant(self, field, plant, gardenID, fields):
        """
        Baut eine Pflanze auf einem Feld an.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
    
        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}' + \
                  f'.wurzelimperium.de/save/pflanz.php?pflanze[]={plant}' + \
                  f'&feld[]={field}' + \
                  f'&felder[]={fields}' + \
                  f'&cid={self.__token}' + \
                  f'&garden={gardenID}'
    
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
        except:
            print('except')
            raise
        else:
            pass

    def growAquaPlant(self, field, plant):
        """
        Baut eine Pflanze im Wassergarten an.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=watergardenCache&' + \
                  'plant[' + str(field) + ']=' + str(plant) + \
                  '&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
        except:
            print('except')
            raise
        else:
            pass
        
    def getAllProductInformations(self):
        """
        Sammelt alle Produktinformationen und gibt diese zur Weiterverarbeitung zurück.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/main.php?page=garden'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            content = content.decode('UTF-8')
            self.__checkIfHTTPStateIsOK(response)
            reToken = re.search(r'ajax\.setToken\(\"(.*)\"\);', content)
            self.__token = reToken.group(1) #TODO: except, wenn token nicht aktualisiert werden kann
            reProducts = re.search(r'data_products = ({.*}});var', content)
        except:
            raise
        else:
            return reProducts.group(1)
            
    def getInventory(self):
        """
        Ermittelt den Lagerbestand und gibt diesen zurück.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                    'Content-Length':'0'}
    
        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/ajax/updatelager.php?' + \
                  f'all=1&sort=1&type=honey&token={self.__token}'
              
        try:
            response, content = self.__webclient.request(adresse, 'POST', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
        except:
            pass
        else:
            return jContent['produkte']


    def getNPCPrices(self):
        """
        Ermittelt aus der Wurzelimperium-Hilfe die NPC Preise aller Produkte.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                    'Content-Length':'0'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/hilfe.php?item=2'

        #try:
        response, content = self.__webclient.request(adresse, 'GET', headers = headers)
        self.__checkIfHTTPStateIsOK(response)

        content = content.decode('UTF-8').replace('Gärten & Regale', 'Gärten und Regale')
        content = bytearray(content, encoding='UTF-8')

        dictNPCPrices = self.__parseNPCPricesFromHtml(content)
        #except:
        #    pass #TODO Exception definieren
        #else:
        return dictNPCPrices
        

    def getAllTradeableProductsFromOverview(self):
        """
        Gibt eine Liste zurück, welche Produkte handelbar sind.
        """
        
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                    'Content-Length':'0'}

        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/stadt/markt.php?show=overview'
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            tradeableProducts = re.findall(r'markt\.php\?order=p&v=([0-9]{1,3})&filter=1', content)
        except:
            pass #TODO: exception definieren
        else:
            for i in range(0, len(tradeableProducts)):
                tradeableProducts[i] = int(tradeableProducts[i])
                
            return tradeableProducts


    def getOffersFromProduct(self, id):
        """
        Gibt eine Liste mit allen Angeboten eines Produkts zurück.
        """
        
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                    'Content-Length':'0'}

        nextPage = True
        iPage = 1
        listOffers = []
        while (nextPage):
            
            nextPage = False
            adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/stadt/markt.php?order=p&v={id}&filter=1&page={iPage}'
            
            try:
                response, content = self.__webclient.request(adresse, 'GET', headers = headers)
                self.__checkIfHTTPStateIsOK(response)
            except:
                pass #TODO: exception definieren
            else:
                html_file = io.BytesIO(content)
                html_tree = html.parse(html_file)
                root = html_tree.getroot()
                table = root.findall('./body/div/table/*')
                
                if (table[1][0].text == 'Keine Angebote'):
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

    def removeWeedOnFieldInGarden(self, gardenID, fieldID):
        """
        Befreit ein Feld im Garten von Unkraut.
        """

        self.__changeGarden(gardenID)

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                    'Content-Length':'0'}
    
        adresse = f'http{self.__Session.getSecure()}://s{self.__Session.getServer()}.wurzelimperium.de/save/abriss.php?tile={fieldID}'
        try:
            response, content = self.__webclient.request(adresse, 'POST', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForSuccess(content)
        except:
            raise
        else:
            return jContent['success']
        
    def __getavailablehives(self, jContent):
        """
        Sucht im JSON Content nach verfügbaren Bienenstöcken und gibt diese zurück.
        """
        availablehives = []

        for hive in jContent['data']['data']['hives']:
            if "blocked" not in jContent['data']['data']['hives'][hive]:
                availablehives.append(int(hive))

        # Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(availablehives) > 0:
            availablehives.sort(reverse=False)

        return availablehives

    def __gethivetype(self, jContent):
        """
        Sucht im JSON Content nach dme Typ der Bienenstöcke und gibt diese zurück.
        """
        hivetype = []

        for hive in jContent['data']['data']['hives']:
            if "blocked" not in jContent['data']['data']['hives'][hive]:
                hivetype.append(int(hive))

        # Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(hivetype) > 0:
            hivetype.sort(reverse=False)

        return hivetype

    def __gethoneyquest(self, jContent):
        """
        Sucht im JSON Content nach verfügbaren Bienenquesten und gibt diese zurück.
        """
        honeyquest = {}
        i = 1
        for course in jContent['questData']['products']:
            new = {i: {'pid': course['pid'], 'type': course['name']}}
            honeyquest.update(new)
            i = i + 1
        return honeyquest

    def __getavailablebonsaislots(self, jContent):
        """
        Sucht im JSON Content nach verfügbaren bonsai und gibt diese zurück.
        """
        availabletreeslots = []

        for tree in jContent['data']['data']['slots']:
            if "block" not in jContent['data']['data']['slots'][tree]:
                availabletreeslots.append(int(tree))

        # Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(availabletreeslots) > 0:
            availabletreeslots.sort(reverse=False)

        return availabletreeslots

    def __getbonsaiquest(self, jContent):
        """
        Sucht im JSON Content nach verfügbaren bonsaiquesten und gibt diese zurück.
        """
        bonsaiquest = {}
        i = 1
        for course in jContent['questData']['products']:
            new = {i: {'pid': course['pid'], 'type': course['name']}}
            bonsaiquest.update(new)
            i = i + 1
        return bonsaiquest
    
    def __getCityQuest(self):
        """
        Ermittelt aktuelle Quest und gibt diese zurück.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Content-Length': '0'}

        adresse = f'http{self.__Session.getSecure()}://s' + str(
            self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?' + \
                  'do=CityQuest&action=getQuest&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
        except:
            raise
        else:
            pass

    def doCityQuest(self):
        """
        Probiert die aktuelle Quest zu lösen.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Content-Length': '0'}

        adresse = f'http{self.__Session.getSecure()}://s' + str(
            self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?' + \
                  'do=CityQuest&action=send&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
        except:
            raise
        else:
            pass

    def __getTreeQuest(self):
        """
        Ermittelt aktuelle Quest und gibt diese zurück.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Content-Length': '0'}

        adresse = f'http{self.__Session.getSecure()}://s' + str(
            self.__Session.getServer()) + '.wurzelimperium.de/treequestquery.php?' + \
                  'op=listavailablequests'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = json.loads(content)
        except:
            raise

    def doTreeQuest(self):
        return

    def doLoginBonus(self):
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Content-Length': '0'}

        try:
            for day in range(1, 8):
                response, content = self.__webclient.request('http' + str(self.__Session.getSecure()) + '://s' + str(
                    self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=dailyloginbonus_getreward' + '&day=' + str(
                    day) + '&token=' + self.__token, 'GET', headers=headers)
                if response['status'] == 200:
                    self.__checkIfHTTPStateIsOK(response)
                    jContent = json.loads(content)
                    break
        except:
            raise
        
    def getHoneyFarmInfos(self):
        """
        Funktion ermittelt, alle wichtigen Infos des Bienengarten und gibt diese aus.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=bees_init' + '&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            honeyquestnr = jContent['questnr']
            honeyquest = self.__gethoneyquest(jContent)
            hives = self.__getavailablehives(jContent)
            hivetype = self.__gethivetype(jContent)
            return honeyquestnr, honeyquest, hives, hivetype
        except:
            raise

    def doQuestBienen(self):
        """
        Sucht im JSON Content nach verfügbaren Bienenquesten und gibt diese zurück.
        """

    def harvestBienen(self):
        """
        Erntet den vollen Honigtopf.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=bees_fill&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise
        else:
            pass

    def changeHivesTypeQuest(self, hive, Questanforderung):
        """
        Ändert den Typ vom Bienenstock auf die Questanforderung.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=bees_changehiveproduct&id=' + str(hive) + '&pid=' + str(Questanforderung) + '&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            pass

    #Bonsai
    def getBonsaiFarmInfos(self):
        """
        Funktion ermittelt, alle wichtigen Infos des Bonsaigarten und gibt diese aus.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=bonsai_init' + '&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            bonsaiquestnr = jContent['questnr']
            bonsaiquest = self.__getbonsaiquest(jContent)
            bonsaislots = self.__getavailablebonsaislots(jContent)
            return bonsaiquestnr, bonsaiquest, bonsaislots
        except:
            raise

    def doCutBonsai(self, tree):
        """
        Schneidet den Ast vom Bonsai..
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=bonsai_branch_click&slot=' + str(
            tree) + '&scissor=274252&cache=%5B2%5D&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            pass

    def sendBienen(self, hive):
        """
        sendet die Bienen für 2 Stunden.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = f'http{self.__Session.getSecure()}://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=bees_startflight&id=' + str(hive) + '&tour=1&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            pass

    #VogelPost

    def doBirdPost(self):
        """
        Schickt die Vögel auf die Reise.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Content-Length': '0'}

        try:
            for slot in range(1, 9):
                response, content = self.__webclient.request('http' + str(self.__Session.getSecure()) + '://s' + str(
                    self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=birds_finish_job' + '&slot=' + str(
                    slot) + '&token=' + self.__token, 'GET', headers=headers)
                response, content = self.__webclient.request('http' + str(self.__Session.getSecure()) + '://s' + str(
                    self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=birds_feed_bird' + '&slot=' + str(
                    slot) + '&token=' + self.__token, 'GET', headers=headers)
                if slot > 4:
                    jobslot = slot + 1
                    house = slot + 1
                elif slot < 5:
                    jobslot = slot
                    house = slot
                response, content = self.__webclient.request('http' + str(self.__Session.getSecure()) + '://s' + str(
                    self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=birds_start_job' + '&jobslot=' + str(
                    jobslot) + '&house=' + str(house) + '&token=' + self.__token, 'GET', headers=headers)
        except:
            raise

    def osterevent(self):
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Content-Length': '0'}

        try:
            response, content = self.__webclient.request('http' + str(self.__Session.getSecure()) + '://s' + str(
                self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=diggame_init' + '&token=' + self.__token,
                                                         'GET', headers=headers)
            # print "ostereventresponse: " + str(response)
            # print "ostereventcontent: " + str(content)
            self.__checkIfHTTPStateIsOK(response)
            jContent = json.loads(content)
            zone = 1
            for free in range(5):
                self.__webclient.request('http' + str(self.__Session.getSecure()) + '://s' + str(
                    self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=diggame_map_hit' + '&zone=' + str(
                    zone) + '&token=' + self.__token, 'GET', headers=headers)
            response1 = self.__webclient.request('http' + str(self.__Session.getSecure()) + '://s' + str(
                self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=diggame_map_finish&option=1' + '&token=' + self.__token,
                                                 'GET', headers=headers)
            # print response1
            for day in range(1, 11, 1):
                self.__webclient.request('http' + str(self.__Session.getSecure()) + '://s' + str(
                    self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=calendar_open' + '&field=' + str(
                    day) + '&token=' + self.__token, 'GET', headers=headers)
        except:
            raise
        return

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
