#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.01.2017

@author: MrFlamez
'''

import time
import logging

class Session(object):
    """
    The Session class is the Python equivalent of a PHP session and is designed accordingly.
    """
    # Session lifetime (2 hours -> 7200 s)
    __lifetime = 7200
    __lifetime_reserve = 300

    def __init__(self):
        self.__logSession = logging.getLogger('bot.Session')
        self.__sessionID = None
        self.__serverURL = None
        self.__server = None
        self.__startTime = None
        self.__endTime = None

    def __isSessionTimeElapsed(self):
        """Checks if the open session has expired."""
        return time.time() > self.__endTime

    def isSessionValid(self):
        """Checks various criteria to determine if the current session is valid."""
        isValid = True
        if self.__sessionID is None:
            isValid = False
            self.__logSession.debug("Session ID is None.")
        if self.__isSessionTimeElapsed():
            isValid = False
            self.__logSession.debug("Session has expired.")
        return isValid

    def openSession(self, sessionID, server, serverURL):
        """Creates a new session with all necessary data."""
        self.__sessionID = sessionID
        self.__server = server
        self.__serverURL = serverURL
        self.__startTime = time.time()
        self.__endTime = self.__startTime + (self.__lifetime - self.__lifetime_reserve)
        sID = str(self.__sessionID)
        self.__logSession.info(f'Session (ID: {sID}) opened.')

    def closeSession(self, wunr, server):
        """Resets all information. Equivalent to closing the session."""
        sID = str(self.__sessionID)
        self.__sessionID = None
        self.__server = None
        self.__startTime = None
        self.__endTime = None
        self.__logSession.info(f'Session (ID: {sID}) closed.')

    def getRemainingTime(self):
        """Returns the remaining time until the session expires."""
        remainingTime = self.__endTime - time.time()
        self.__logSession.debug(f'Remaining session time: {remainingTime} seconds.')
        return remainingTime

    def getSessionID(self):
        """Returns the session ID."""
        return self.__sessionID

    def getServer(self):
        """Returns the server number."""
        return self.__server

    def getServerURL(self):
        """Returns the server URL."""
        return self.__serverURL
