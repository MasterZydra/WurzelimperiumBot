#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017
@author: MrFlamez
'''

import logging
import os
import time

#vars
logtime = time.strftime("%d-%m-%y-%H.%M.%S")

if not os.path.exists('logs'):
    os.makedirs('logs')

def logger():
    logging.basicConfig(filename='logs/wurzelbot '+logtime+'.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

#TODO: Konstruktor prüfen, evtl um Accountdaten erweitern