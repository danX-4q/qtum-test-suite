#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler
import subprocess
from copy import deepcopy

import sys
sys.path.append('../global--env/')
from envconfig import *

class CmdBuiler:
    def __init__(self):
        self.ct_dict = {}
    
    @staticmethod
    def qtum_cli__gethexaddress(qa):
        return 'wrp-qtum-cli gethexaddress %s' % qa

    @staticmethod
    def qtum_cli__fromhexaddress(ha):
        return 'wrp-qtum-cli fromhexaddress %s' % ha

    @staticmethod
    def qtum_cli__getnewaddress(account=''):
        return ('wrp-qtum-cli getnewaddress %s' % account)

    @staticmethod
    def git_clone(url, dst_dir=''):
        return ('git clone %s %s' % (url, dst_dir))

    @staticmethod
    def qtum_cli__sendtoaddress(qa, value=100):
        return ('wrp-qtum-cli sendtoaddress %s %s' % (qa, value))

    @staticmethod
    def qtum_cli__gettransaction(txid):
        return ('wrp-qtum-cli gettransaction %s' % txid)

    @staticmethod
    def qtum_cli__decoderawtxid(txid):
        return ('wrp-qtum-cli decoderawtxid %s' % txid)

    @staticmethod
    def qtum_cli__listunspent(min_s=0, max_s=20, addr_filter_json=''):
        return ('wrp-qtum-cli listunspent %s %s %s' % (min_s, max_s, addr_filter_json))

    @staticmethod
    def solar__deploy(sender, contract_file, construct_args_str):
        return ('wrp-solar --qtum_sender=%s deploy --force %s %s' % (sender.getQa(), contract_file, construct_args_str))
    
    @staticmethod
    def solar__status():
        return ('wrp-solar status')

    @staticmethod
    def qtumjs_cli__mint(qha, value=1000):
        return ('node wrp-index.js mint %s %s #qa=%s' % (qha.getHa(), value, qha.getQa()))

    @staticmethod
    def qtumjs_cli__events():
        return ('node wrp-index.js events')
    
    @staticmethod
    def qtumjs_cli__transfer(qha_a, qha_b, value=40) :
        return ('node wrp-index.js transfer %s %s %s #qa_b=%s' % 
            (qha_a.getQa(), qha_b.getHa(), value, qha_b.getQa())
            #a must be Qa(qtum address, base58), b must be Ha(eth address, hex)
        )

    @staticmethod
    def qtumjs_cli__balance(qha) :
        return ('node wrp-index.js balance %s #qa=%s' % (qha.getHa(), qha.getQa()))

    @staticmethod
    def ctcoinjs_cli__deposit(qha, msg_value) :
        return ('node wrp-index.js deposit %s %s' % (qha.getQa(), msg_value))

    @staticmethod
    def ctcoinjs_cli__transport(qha_a, qha_b, value=30):
        return (
            'node wrp-index.js transport %s %s %d' % (qha_a.getQa(), qha_b.getHa(), value)
        )

    @staticmethod
    def ctcoinjs_cli__getbalance(qha_a, ha):
        return (
            'node wrp-index.js getbalance %s %s' % (qha_a.getQa(), ha)
        )

    @staticmethod
    def ctcoinjs_cli__refund(qha_a, value=5):
        return (
            'node wrp-index.js refund %s %s' % (qha_a.getQa(), value)
        )

    @staticmethod
    def ctcoinjs_cli__transferCCY(qha_a, qha_b, msg_value=7, value=7):
        return (
            'node wrp-index.js transferCCY %s %s %s %s' % (qha_a.getQa(), qha_b.getHa(), msg_value, value)
        )
    
    @staticmethod
    def ctcoinjs_cli__newcon(value = 10):
        return (
            'node wrp-index.js Newcon %s' % (value)
        )

    @staticmethod
    def ctcoinjs_cli__newconwithcoin(account = 10, value = 5):
        return (
            'node wrp-index.js Newcon %s %s' % (account, value)
        )
    
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

    def popen(self, cmd, shell=False, stdout=subprocess.PIPE) :
        self.logger.info('cmd-line(popened): %s' % cmd)
        p = subprocess.Popen(cmd,shell=shell,stdout=stdout)
        return p

    def popen_stdout(self, p, cb_return=None):
        ret = ''
        for i in iter(p.stdout.readline, b''):  #until meet the string ''
            ret += i
            if cb_return and cb_return(ret):
                break

        self.logger.info('ret-out(popened): %s' % ret)
        return ret


class CQHAddress:
    def __init__(self, cs_inst):
        self.cs_inst = cs_inst
        self.qa = None
        self.ha = None
    
    def setQa(self, qa):
        self.qa = qa
        self.ha = self.cs_inst.check_output(
            CmdBuiler.qtum_cli__gethexaddress(qa),
            shell=True
        )
    
    def setHa(self, ha):
        self.ha = ha
        self.qa = self.cs_inst.check_output(
            CmdBuiler.qtum_cli__fromhexaddress(ha),
            shell=True
        )

    def getQa(self):
        return self.qa

    def getHa(self):
        return self.ha

    def __str__(self):
        return ('{"qa":"%s","ha":"%s"}' % (self.qa, self.ha))

class CEnv:
    def __init__(self):
        self.env_kv = self.load_env_kv()
        self.prog_env = self.env_kv[0]
        self.nodes_env = self.env_kv[1]

    def load_env_kv(self) :    #return [prog_env, nodes_env]
        prog = {
            'QTUM_PREFIX' : QTUM_PREFIX,
            'QTUM_BIN' : QTUM_BIN,
            'CMD_QTUMD': CMD_QTUMD,
            'CMD_QTUMCLI': CMD_QTUMCLI,
            'QTUM_DFT_NODE': QTUM_DFT_NODE,
        }

        return [
            deepcopy(prog),
            deepcopy(QTUM_NODES)
        ]

    def apply_env_callback(self, cbfun):
        cbfun(self.prog_env, self.nodes_env)
