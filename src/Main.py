#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''
from src.WurzelBot import WurzelBot
import logging

def initWurzelBot():
    logging.basicConfig(handlers=[logging.FileHandler("wurzelbot.log", 'a', 'utf-8')], level=logging.DEBUG, format='%(asctime)s - %(message)s')
    return WurzelBot()

#TODO: Konstruktor prüfen, evtl um Accountdaten erweitern