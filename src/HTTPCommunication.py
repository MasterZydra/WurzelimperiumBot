#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from urllib import urlencode
import json, re, httplib2
from Cookie import SimpleCookie
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


    def __del__(self):
        self.__Session = None
        self.__token = None
        self.__userID = None


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


    def __generateJSONContentAndCheckForOK(self, content):
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
            raise JSONError('Fehler bei der Ermittlung des tokens')
        else:
            self.__token = tmpToken


    def __getUserNameFromJSONContent(self, jContent):
        """
        Sucht im übergebenen JSON Objekt nach dem Usernamen und gibt diesen zurück.
        """
        result = False
        for i in range(0, len(jContent['table'])):
            sUserName = str(jContent['table'][i].encode('utf-8'))  
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
            sGartenAnz = str(jContent['table'][i].encode('utf-8'))   
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

    def __generateYAMLContentAndCheckForSuccess(self, content):
        """
        Aufbereitung und Prüfung der vom Server empfangenen YAML Daten auf Erfolg.
        """
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        yContent = yaml.load(content)
        
        if (yContent['success'] != 1):
            raise YAMLError()


    def __generateYAMLContentAndCheckStatusForOK(self, content):
        """
        Aufbereitung und Prüfung der vom Server empfangenen YAML Daten auf iO Status.
        """
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        yContent = yaml.load(content)
        
        if (yContent['status'] != 'ok'):
            raise YAMLError()

    def __changeGarden(self, gardenID):
        """
        Wechselt den Garten.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}

        adresse = 'http://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=changeGarden&garden=' + \
                  str(gardenID) + '&token=' + self.__token

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
                
                #Produktname aufbereiten
                if type(produktname) == unicode:
                    produktname = produktname.encode('utf-8')
                    produktname = str(produktname)
                
                #NPC-Preis aufbereiten
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
            self.__Session.openSession(cookie['PHPSESSID'].value, str(loginDaten.server))
            self.__cookie = cookie
            self.__userID = cookie['wunr'].value


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
        
        adresse = 'http://s'+str(self.__Session.getServer()) + '.wurzelimperium.de/main.php?page=logout'
        
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
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=statsGetStats&which=0&start=0&additional='+\
                  self.__userID + '&token=' + self.__token
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
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
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=statsGetStats&which=0&start=0&additional='+\
                  self.__userID + '&token=' + self.__token
        
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
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/menu-update.php'
        
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
        adresse = 'http://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=changeGarden&garden=' + \
                  str(gardenID) + '&token=' + str(self.__token)

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
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/save/wasser.php?feld[]=' + \
                  str(iField) + '&felder[]=' + sFieldsToWater + '&cid=' + self.__token + '&garden=' + str(iGarten)

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            self.__generateYAMLContentAndCheckForSuccess(content)
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
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=watergardenGetGarden&token=' + self.__token
        
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
            sFields += '&water[]='+str(i)

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=watergardenCache' + sFields + '&token='+self.__token

        
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
        adresse = 'http://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/gettrophies.php?category=giver'
        
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

            
    def isAquaGardenAvailable(self, iUserLevel):
        """
        Funktion ermittelt, ob ein Wassergarten verfügbar ist.
        Dazu muss ein Mindestlevel von 19 erreicht sein und dieser dann freigeschaltet sein.
        Die Freischaltung wird anhand der Errungenschaften im Spiel geprüft.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/achievements.php?token='+self.__token

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

        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/nutzer/profil.php'

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

        adress = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/nachrichten/new.php'
        
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

        adress = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/nachrichten/new.php'

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
        print iCalls
        for i in range(iCalls):
            print i
            adress = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=statsGetStats&which=1&start='+str(iStartCorr)+'&showMe=0&additional=0&token=' + self.__token
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

        adress = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/updatelager.' + \
                 'php?all=1'

        try:
            response, content = self.__webclient.request(adress, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
        except:
            raise
        else:
            print jContent['produkte']

    def getEmptyFieldsOfGarden(self, gardenID):
        """
        Gibt alle leeren Felder eines Gartens zurück.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=changeGarden&garden=' + \
                  str(gardenID) + '&token=' + self.__token

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            emptyFields = self.__findEmptyFieldsFromJSONContent(jContent)
        except:
            raise
        else:
            return emptyFields

    def harvestGarden(self, gardenID):
        """
        Erntet alle fertigen Pflanzen im Garten.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
    
        adresse = 'http://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=gardenHarvestAll&token=' + self.__token

        try:
            self.__changeGarden(gardenID)
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
        # TODO: Response auf HTTP Fehler prüfen?
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
    
        adresse = 'http://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=watergardenHarvestAll&token=' + self.__token

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
    
        adresse = 'http://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/save/pflanz.php?pflanze[]=' + str(plant) + \
                  '&feld[]=' + str(field) + \
                  '&felder[]=' + fields + \
                  '&cid=' + self.__token + \
                  '&garden=' + str(gardenID)
    
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
        except:
            print 'except'
            raise
        else:
            pass
    
    
    def growPlantInAquaGarden(self, plant, field):
        """
        Baut eine Pflanze im Wassergarten an.
        """
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
    
        adresse = 'http://s' + str(self.__Session.getServer()) + \
                  '.wurzelimperium.de/ajax/ajax.php?do=watergardenCache&' + \
                  'plant[' + str(field) + ']=' + str(plant) + \
                  '&token=' + self.__token
    
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            print response
            print content
        except:
            print 'except'
            raise
        else:
            pass    
    def getAllProductInformations(self):
        """
        Sammelt alle Produktinformationen und gibt diese zur Weiterverarbeitung zurück.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID}

        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/main.php?page=garden'

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
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
    
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/updatelager.php?' + \
              'all=1&sort=1&type=honey&token=' + self.__token
              
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

        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/hilfe.php?item=2'

        #try:
        response, content = self.__webclient.request(adresse, 'GET', headers = headers)
        self.__checkIfHTTPStateIsOK(response)
        content = content.replace('&', 'und')
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

        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/stadt/markt.php?show=overview'
        
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
            adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/stadt/markt.php?order=p&v='+ str(id) +'&filter=1&page='+str(iPage)
            
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
