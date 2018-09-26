#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import subprocess
import os
import argparse
import json

import sys
sys.path.append('../py-utils/')
#sys.path.append('../global--env/')
import utils
#from envconfig import *

cs_inst = None
addr_dict = {}
contract_addr = ''

def dry_run() :
    cmds = [
        #'wrp-qtum-cli getnewaddress',
        #'wrp-qtum-cli sendtoaddress <new-address> <value>',
        #'wrp-qtum-cli gettransaction <txid>',
        #'wrp-qtum-cli decoderawtxid <txid>',
        ##'wrp-qtum-cli listunspent 0 50 <address-list>'
        #'wrp-qtum-cli listunspent 0 50'
    ]
    for c in cmds:
        print c

def getnewaddress_with_names(cs_inst, logger, names) :
    global addr_dict
    for n in names :
        qa = cs_inst.check_output(utils.CmdBuiler.qtum_cli__getnewaddress(n), shell=True)
        qha = utils.CQHAddress(cs_inst)
        qha.setQa(qa)
        addr_dict.update({n : qha})
        logger.info('addr_dict[%s]\t=>\tqa:%s\tha:%s' % (n, qa, qha.getHa()))
    
def step0_prepare(cs_inst, logger):
    global addr_dict
    names = ['a', 'b', 'c']
    getnewaddress_with_names(cs_inst, logger, names)

    if not os.path.exists('ctcoinjs-cli'):
        cs_inst.check_call('git clone https://github.com/danX-4q/ctcoinjs-cli.git ctcoinjs-cli', shell=True)
        cs_inst.check_call('git clone https://github.com/danX-4q/ctcoin-solidity.git ctcoinjs-cli/ctcoin-solidity', shell=True)
        
        os.chdir('ctcoinjs-cli')
        env_inst = utils.CEnv()
        def cb_apply_env(prog_env, nodes_env):
            for node_name in sorted(nodes_env.keys()) :
                t = file('nodeX--index.js.tmpl')
                d = file(node_name + '--index.js', 'w')
                s = t.read()
                d.write(s % nodes_env[node_name])
            f_r = prog_env['QTUM_DFT_NODE'] + '--' + 'index.js'
            f_l = 'wrp-index.js'
            try:
                os.remove(f_l)
            except OSError as e:
                if e.errno == 2:
                    pass
                else :
                    raise
            os.symlink(f_r, f_l)
            logger.info('symlink %s -> %s' %(f_l, f_r))
        env_inst.apply_env_callback(cb_apply_env)

        cs_inst.check_call('yarn install', shell=True)
    else :
        os.chdir('ctcoinjs-cli')

def __dump_tx_info(cs_inst, logger, txid):
    cmd = utils.CmdBuiler.qtum_cli__gettransaction(txid)
    cs_inst.check_output(cmd, shell=True)
    cmd = utils.CmdBuiler.qtum_cli__decoderawtxid(txid)
    cs_inst.check_output(cmd, shell=True)
    cmd = utils.CmdBuiler.qtum_cli__listunspent()
    cs_inst.check_output(cmd, shell=True)

def __transfer_coin_to_qhaX(cs_inst, logger, qhaX, value):
    cmd = utils.CmdBuiler.qtum_cli__sendtoaddress(qhaX.getQa(), value)
    txid = cs_inst.check_output(cmd, shell=True)
    __dump_tx_info(cs_inst, logger, txid)

def __qhaX_create_contract(cs_inst, logger, qhaX, contract_file, construct_args_str):
    cmd = utils.CmdBuiler.solar__deploy(
        qhaX, contract_file, construct_args_str)
    cs_inst.check_call(cmd, shell=True)
    cmd = utils.CmdBuiler.solar__status()
    output = cs_inst.check_output(cmd, shell=True)
    '''output like:
    ret-out: ✅  zeppelin-solidity/contracts/token/ERC20/ERC20Capped.sol
         txid: 86a6af5b1eb5c12966348b9ddcc8a68a374fa3f748f29a8e9f40400ef73d1dcf
      address: bf8f23f647799551b24a30f35bbf7972ce4d9014
    confirmed: true
        owner: qSX6Hjuo965jkzpc1uFo1g31mCs4GRE7Lh
    '''
    txid = output.split('\n')[1].split(':')[1].strip()
    global contract_addr
    contract_addr = output.split('\n')[2].split(':')[1].strip()
    __dump_tx_info(cs_inst, logger, txid)

def __qhaX_deposit(cs_inst, logger, contract_addr, qhaX, msg_value):
    cmd = utils.CmdBuiler.ctcoinjs_cli__deposit(qhaX, msg_value)
    output = cs_inst.check_output(cmd, shell=True)
    #logger.debug(output)
    '''output like:
        deposit tx: 55c3b2a8961b9815829d6129170c124a7759c0d3ecc5968c3959ef2b9e680025
        { amount: -80,
          fee: -0.080944,
          confirmations: 0,
          ...
    '''
    txid = output.split('\n')[0].split(':')[1].strip()
    #logger.debug(txid)
    __dump_tx_info(cs_inst, logger, txid)
    cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qhaX, contract_addr)
    cs_inst.check_output(cmd, shell=True)

def __qhaX_transport_to_qhaY(cs_inst, logger, contract_addr, qhaX, qhaY, value):
    cmd = utils.CmdBuiler.ctcoinjs_cli__transport(qhaX, qhaY, value)
    output = cs_inst.check_output(cmd, shell=True)
    txid = output.split('\n')[0].split(':')[1].strip()
    __dump_tx_info(cs_inst, logger, txid)
    cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qhaX, contract_addr)
    cs_inst.check_output(cmd, shell=True)

def transfer_coin_to_a(cs_inst, logger):
    global addr_dict
    qha_a = addr_dict['a']
    __transfer_coin_to_qhaX(cs_inst, logger, qha_a, 100)

def transfer_coin_to_b(cs_inst, logger):
    global addr_dict
    qha_b = addr_dict['b']
    __transfer_coin_to_qhaX(cs_inst, logger, qha_b, 99)

def transfer_coin_to_c(cs_inst, logger):
    global addr_dict
    qha_b = addr_dict['c']
    __transfer_coin_to_qhaX(cs_inst, logger, qha_b, 98)

def a_create_ctcoin_contract(cs_inst, logger):
    global addr_dict
    qha_a = addr_dict['a']

    __qhaX_create_contract(cs_inst, logger, qha_a, 
        'ctcoin-solidity/ctcoin.sol', '')

def a_call__deposit(cs_inst, logger):
    global addr_dict
    global contract_addr
    qha_a = addr_dict['a']
    __qhaX_deposit(cs_inst, logger, contract_addr, qha_a, 80)

def a_call__transport_to_b(cs_inst, logger):
    global addr_dict
    global contract_addr
    qha_a = addr_dict['a']
    qha_b = addr_dict['b']
    __qhaX_transport_to_qhaY(cs_inst, logger, contract_addr, qha_a, qha_b, 30)

def go_step_by_step(cs_inst, logger):
    step_list = [
        transfer_coin_to_a, #100
        transfer_coin_to_b, #99
        transfer_coin_to_c, #98
        ####
        a_create_ctcoin_contract,
        ####
        a_call__deposit,        #a -> ct 80
        a_call__transport_to_b, #ct -> b 30
        ####
        #c_call__transport_to_b, #ct -> b 20
        ####
        #a_call__refund,         #ct -> a 3
        #b_call__refund,         #ct -> b 2
        #c_call__refund,         #ct -> c 1
        ####
        #a_call__transferCCY_to_b,   #a -> ct -> b, msg.value 10, value 7
        #b_call__transferCCY_to_c,   #b -> ct -> c, msg.value 13, value 7
    ]
    for i in range(len(step_list)):
        step_name = 'step' + str(i)
        logger.info(step_name + '--' + step_list[i].__name__ + ' begin:')
        step_list[i](cs_inst, logger)
        logger.info(step_name + '--' + step_list[i].__name__ + ' end.')

def run(cs_inst, logger):

    step0_prepare(cs_inst, logger)
    go_step_by_step(cs_inst, logger)

def main() :
    global cs_inst
    parser = argparse.ArgumentParser(
            description="qtum-test-suite -- s2__erc20-transfer-token",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-d', '--dry-run', action='store_true',
                        dest='dry_run', help='enable dry-run')
    prog_args = parser.parse_args()
    #print prog_args

    logger = utils.make_logger('./rt-data/run.log')
    cs_inst = utils.CSubprocess(logger)

    if prog_args.dry_run :
        dry_run()
    else :
        run(cs_inst, logger)

if __name__ == '__main__' :
    main()
