#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler
import subprocess

def make_logger(log_file_name) :

    logging.basicConfig(level=logging.DEBUG, 
        format="%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)6s\n%(message)s\n----------", 
        datefmt="%Y-%m-%dT%H:%M:%S")
    
    Rthandler = RotatingFileHandler(log_file_name, 10485760, 8)
    formatter = logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s")
    Rthandler.setFormatter(formatter)
    logging.getLogger('').addHandler(Rthandler)

    logger = logging.getLogger()
    logger.info('start logger successfully! log file path: %s' % log_file_name)
    return logger

class CSubprocess :

    def __init__(self, logger):
        self.logger = logger
    
    def check_call(self, cmd, shell=False) :
        self.logger.info('cmd-line: %s' % cmd)
        ret = subprocess.check_call(cmd, shell=shell)
        self.logger.info('ret-code: %s' % ret)
        return ret

    def check_output(self, cmd, shell=False):
        self.logger.info('cmd-line: %s' % cmd)
        ret = subprocess.check_output(cmd, shell=shell).strip()
        self.logger.info('ret-out: %s' % ret)
        return ret


