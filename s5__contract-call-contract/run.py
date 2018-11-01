#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import subprocess
import os
import argparse
import json

import sys
#sys.path.append('../py-utils/')
sys.path.append('/home/loyal/work/git/qtum-test-suite/py-utils')
#sys.path.append('../global--env/')
import utils
#from envconfig import *

cs_inst = None
addr_dict = {}
contract_addr = ''
contract_addr_dict = {}

def dry_run() :
    cmds = [
        'wrp-qtum-cli getnewaddress',
        'wrp-qtum-cli sendtoaddress <address> <coin_value>',
        'wrp-qtum-cli gettransaction <txid>',
        'wrp-qtum-cli decoderawtxid <txid>',
        #'wrp-qtum-cli listunspent 0 50 <address-list>'
        'wrp-qtum-cli listunspent 0 50',
        '####!!!!#### at ctcoinjs-cli',
        'wrp-solar --qtum_sender=<creator_address> deploy --force <sol_file> [contract_constructor_args]',
        'wrp-solar status',
        '####!!!!#### at ctcoinjs-cli/',
        'node wrp-index.js deposit <caller> <coin_value>',
        'node wrp-index.js transport <caller> <to_addr> <value ["wei"]>',
        'node wrp-index.js refund <caller> <value ["wei"]>',
        'node wrp-index.js transferCCC <caller> <to_addr> <coin_value> <value ["wei"]>',
        'node wrp-index.js getbalance <caller> <contract_addr>'
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
    outputList = output.split('\n\n')
    for n in outputList :
        txid = n.split('\n')[1].split(':')[1].strip()
        global contract_addr
        contract_addr = n.split('\n')[2].split(':')[1].strip()
        ownerId = n.split('\n')[4].split(':')[1].strip()
        if ownerId == qhaX.getQa() :
            break
            
    __dump_tx_info(cs_inst, logger, txid)
    return (contract_addr)

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

def __qhaX_refund(cs_inst, logger, contract_addr, qhaX, value):
    cmd = utils.CmdBuiler.ctcoinjs_cli__refund(qhaX, value)
    output = cs_inst.check_output(cmd, shell=True)
    txid = output.split('\n')[0].split(':')[1].strip()
    __dump_tx_info(cs_inst, logger, txid)
    cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qhaX, contract_addr)
    cs_inst.check_output(cmd, shell=True)

def __qhaX_transferCCY_to_qhaY(cs_inst, logger, contract_addr, qhaX, qhaY, msg_value, value):
    cmd = utils.CmdBuiler.ctcoinjs_cli__transferCCY(qhaX, qhaY, msg_value, value)
    output = cs_inst.check_output(cmd, shell=True)
    txid = output.split('\n')[0].split(':')[1].strip()
    __dump_tx_info(cs_inst, logger, txid)
    cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qhaX, contract_addr)
    cs_inst.check_output(cmd, shell=True)

def __qhaX_transferCCC_to_qhaY_qhaZ(cs_inst, logger, contract_addra, contract_addrb, contract_addrc, qhaX, qhbX, qhcX, msg_value, value1, value2, refundValue):
    cmd = utils.CmdBuiler.ctcoinjs_cli__transferCCC(contract_addra, contract_addrb, contract_addrc, qhaX, qhbX, qhcX, msg_value, value1, value2, refundValue)
    output = cs_inst.check_output(cmd, shell=True)
    txid = output.split('\n')[0].split(':')[1].strip()
    __dump_tx_info(cs_inst, logger, txid)
    
    cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qhaX, contract_addra)
    cs_inst.check_output(cmd, shell=True)
    # cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qhaY, contract_addrb)
    # cs_inst.check_output(cmd, shell=True)
    # cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qhaZ, contract_addrc)
    # cs_inst.check_output(cmd, shell=True)

def list_all_unspent(cs_inst, logger):
    cmd = utils.CmdBuiler.qtum_cli__listunspent()
    cs_inst.check_output(cmd, shell=True)
    
def transfer_coin_to_a(cs_inst, logger):
    global addr_dict
    qha_a = addr_dict['a']
    __transfer_coin_to_qhaX(cs_inst, logger, qha_a, 10000000)

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

def a_create_contractA_contract(cs_inst, logger):
    global addr_dict
    global contract_addr_dict

    qha_a = addr_dict['a']

    contract_addra = __qhaX_create_contract(cs_inst, logger, qha_a, 
        'ctcoin-solidity/ContractA.sol', '')
    contract_addr_dict.update({'a' : contract_addra})

def a_create_contractB_contract(cs_inst, logger):
    global addr_dict
    global contract_addr_dict

    qha_b = addr_dict['b']

    contract_addrb = __qhaX_create_contract(cs_inst, logger, qha_b, 
        'ctcoin-solidity/ContractB.sol', '')
    contract_addr_dict.update({'b' : contract_addrb})

def a_create_contractC_contract(cs_inst, logger):
    global addr_dict
    global contract_addr_dict

    qha_c = addr_dict['c']

    contract_addrc = __qhaX_create_contract(cs_inst, logger, qha_c, 
        'ctcoin-solidity/ContractC.sol', '')
    contract_addr_dict.update({'c' : contract_addrc})

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

def c_call__transport_to_b(cs_inst, logger):
    global addr_dict
    global contract_addr
    qha_c = addr_dict['c']
    qha_b = addr_dict['b']
    __qhaX_transport_to_qhaY(cs_inst, logger, contract_addr, qha_c, qha_b, 20)

def a_call__refund(cs_inst, logger):
    global addr_dict
    global contract_addr
    qha_a = addr_dict['a']
    __qhaX_refund(cs_inst, logger, contract_addr, qha_a, 3)

def b_call__refund(cs_inst, logger):
    global addr_dict
    global contract_addr
    qha_b = addr_dict['b']
    __qhaX_refund(cs_inst, logger, contract_addr, qha_b, 2)

def a_call__getbalance(cs_inst, logger):
    global addr_dict
    global contract_addr_dict
    qha_a = addr_dict['a']
    contract_addr = contract_addr_dict['a']
    cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qha_a, contract_addr)
    cs_inst.check_output(cmd, shell=True)
    
def b_call__getbalance(cs_inst, logger):
    global addr_dict
    global contract_addr_dict
    qha_a = addr_dict['b']
    contract_addr = contract_addr_dict['b']
    cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qha_a, contract_addr)
    cs_inst.check_output(cmd, shell=True)

def c_call__getbalance(cs_inst, logger):
    global addr_dict
    global contract_addr_dict
    qha_a = addr_dict['c']
    cmd = utils.CmdBuiler.ctcoinjs_cli__getbalance(qha_a, contract_addr)
    cs_inst.check_output(cmd, shell=True)

def a_call__transferCCY_to_b(cs_inst, logger):
    global addr_dict
    global contract_addr
    qha_a = addr_dict['a']
    qha_b = addr_dict['b']
    __qhaX_transferCCY_to_qhaY(cs_inst, logger, contract_addr, qha_a, qha_b, 10, 7)

def b_call__transferCCY_to_c(cs_inst, logger):
    global addr_dict
    global contract_addr
    qha_b = addr_dict['b']
    qha_c = addr_dict['c']
    __qhaX_transferCCY_to_qhaY(cs_inst, logger, contract_addr, qha_b, qha_c, 13, 6)

def a_call__transferCCY_to_c(cs_inst, logger):
    global addr_dict
    global contract_addr
    qha_a = addr_dict['a']
    qha_c = addr_dict['c']
    __qhaX_transferCCY_to_qhaY(cs_inst, logger, contract_addr, qha_a, qha_c, 2, 2)

def a_call__transferCCC_to_b_c(cs_inst, logger):
    global addr_dict
    global contract_addr_dict

    contract_addra = contract_addr_dict['a']
    contract_addrb = contract_addr_dict['b']
    contract_addrc = contract_addr_dict['c']

    qha_a = addr_dict['a']
    qha_b = addr_dict['b']
    qha_c = addr_dict['c']
    __qhaX_transferCCC_to_qhaY_qhaZ(cs_inst, logger, contract_addra, contract_addrb, contract_addrc, qha_a, qha_b, qha_c, 300000, 999, 777, 222)

def go_step_by_step(cs_inst, logger):
    step_list = [
        list_all_unspent,
        transfer_coin_to_a, #10000000
        transfer_coin_to_b, #99
        transfer_coin_to_c, #98
        ####
        a_create_contractA_contract,
        a_create_contractB_contract,
        a_create_contractC_contract,
        # ####
        #a_call__deposit,        #a -> ct 80
        ####
        #a_call__transport_to_b, #ct -> b 30
        #c_call__transport_to_b, #ct -> b 20
        ####
        #a_call__refund,         #ct -> a 3
        #b_call__refund,         #ct -> b 2
        ####
        #a_call__transferCCY_to_b,   #a -> ct -> b, msg.value 10, value 7
        #b_call__transferCCY_to_c,   #b -> ct -> c, msg.value 13, value 6
        #a_call__transferCCY_to_c,   #a -> ct -> c, msg.value 2, value 2
        a_call__transferCCC_to_b_c,
        a_call__getbalance,
        b_call__getbalance,
        c_call__getbalance,
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
            description="qtum-test-suite -- s3__contract-transfer-coin",
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
