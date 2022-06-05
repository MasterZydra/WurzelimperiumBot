#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''
from src.WurzelBot import WurzelBot
import logging

def initWurzelBot():
    return WurzelBot()

def logger():
    logging.basicConfig(filename='wurzelbot.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

#TODO: Konstruktor prüfen, evtl um Accountdaten erweitern