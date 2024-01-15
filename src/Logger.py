#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: xRuffKez
'''

import logging, os, time

#vars
logtime = time.strftime("%y-%m-%d-%H.%M.%S")

if not os.path.exists('logs'):
    os.makedirs('logs')

def logger():
    logging.basicConfig(handlers=[logging.FileHandler(f'logs/wurzelbot {logtime}.log', 'a', 'utf-8')], level=logging.DEBUG, format='%(asctime)s - %(message)s')