#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.01.2017

@author: MrFlamez
'''

from src.logger.Logger import Logger
import time, i18n

i18n.load_path.append('lang')

class Session:
    """Session represents a PHP session"""
    # Session is valid for 2 h (7200 s)
    __lifetime         = 7200
    # Reserve time is used to complete all actions in before the end of the session
    __lifetime_reserve =  300

    def __init__(self):
        """Initialization of all attributes with a default value"""
        self.__session_id = None
        self.__server_url = None
        self.__server = None
        self.__start_time = None
        self.__end_time = None

    def __is_expired(self):
        """Check if open session is elapsed"""
        return time.time() > self.__end_time

    def is_valid(self):
        """Check is the current session is valid"""
        # TODO: Check where this function can be used
        if (self.__session_id == None):
            return False
        if (self.__is_expired()):
            return False
        return True

    def open(self, session_id, server, server_url):
        """Open a new session"""
        self.__session_id = session_id
        self.__server = server
        self.__server_url = server_url

        self.__start_time = time.time()
        self.__end_time = self.__start_time + (self.__lifetime - self.__lifetime_reserve)
        Logger().debug(f'Session (ID: {str(self.__session_id)}) started')

    def close(self):
        """Reset all informations"""
        session_id = str(self.__session_id)
        self.__session_id = None
        self.__server = None
        self.__start_time = None
        self.__end_time = None
        Logger().debug(f'Session (ID: {session_id}) closed')

    def get_remaining_time(self):
        """Get remaining time unit the session expires"""
        return self.__end_time - time.time()

    def get_session_id(self):
        """Get session id"""
        return self.__session_id

    def get_server(self):
        """Get server number"""
        return self.__server

    def get_server_url(self):
        """Get server URL"""
        return self.__server_url
