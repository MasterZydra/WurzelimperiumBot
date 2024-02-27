#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: xRuffKez
'''

import logging, os, time

logtime = time.strftime("%d-%m-%y-%H.%M.%S")
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, f'wurzelbot_{logtime}.log')

def logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    
    logging.basicConfig(
        handlers=[logging.FileHandler(LOG_FILE, 'a', 'utf-8')],
        level=logging.DEBUG,
        format='%(asctime)s - %(message)s'
    )

if __name__ == "__main__":
    logger()