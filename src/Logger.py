#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: xRuffKez
'''

import logging, os, time

#vars
#BG- Променливи
logtime = time.strftime("%y-%m-%d-%H.%M.%S")

if not os.path.exists('logs'):
    os.makedirs('logs')

def logger():
    logging.basicConfig(
        handlers=[logging.FileHandler(f'logs/wurzelbot {logtime}.log', 'a', 'utf-8'), logging.StreamHandler()], 
        level=logging.DEBUG, 
        format='%(asctime)s - %(message)s')
