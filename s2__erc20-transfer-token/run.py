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

def dry_run() :
    cmds = [
        'wrp-qtum-cli getnewaddress',
        'wrp-qtum-cli sendtoaddress <address> <coin_value>',
        'wrp-qtum-cli gettransaction <txid>',
        'wrp-qtum-cli decoderawtxid <txid>',
        #'wrp-qtum-cli listunspent 0 50 <address-list>'
        'wrp-qtum-cli listunspent 0 50',
        '####!!!!#### at qtumjs-cli/',
        'wrp-solar --qtum_sender=<creator_address> deploy --force <sol_file> [contract_constructor_args]',
        'wrp-solar status',
        '####!!!!#### at qtumjs-cli/',
        'node wrp-index.js mint <owner> <value>',
        'node wrp-index.js transfer <from_addr> <to_addr> <value>',
        'node wrp-index.js balance <caller>',
        'node wrp-index.js totalSupply'
    ]
    for c in cmds:
        print c

def step0_prepare(cs_inst, logger):
    global addr_dict
    qa = cs_inst.check_output(utils.CmdBuiler.qtum_cli__getnewaddress(), shell=True)
    qha = utils.CQHAddress(cs_inst)
    qha.setQa(qa)
    addr_dict.update({'a' : qha})

    qa = cs_inst.check_output(utils.CmdBuiler.qtum_cli__getnewaddress(), shell=True)
    qha = utils.CQHAddress(cs_inst)
    qha.setQa(qa)
    addr_dict.update({'b' : qha})

    qa = cs_inst.check_output(utils.CmdBuiler.qtum_cli__getnewaddress(), shell=True)
    qha = utils.CQHAddress(cs_inst)
    qha.setQa(qa)
    addr_dict.update({'c' : qha})

    logger.info(addr_dict)

    if not os.path.exists('qtumjs-cli'):
        cs_inst.check_call('git clone https://github.com/danX-4q/qtumbook-mytoken-qtumjs-cli qtumjs-cli', shell=True)
        cs_inst.check_call('git clone https://github.com/OpenZeppelin/zeppelin-solidity.git qtumjs-cli/zeppelin-solidity', shell=True)
        
        os.chdir('qtumjs-cli')
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
        os.chdir('qtumjs-cli')

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
    __dump_tx_info(cs_inst, logger, txid)

def __qhaX_mint_token(cs_inst, logger, qhaX, value):

    b_get_events = False
    if b_get_events:
        cmd = utils.CmdBuiler.qtumjs_cli__events()
        p = cs_inst.popen(cmd, shell=True)

    cmd = utils.CmdBuiler.qtumjs_cli__mint(qhaX, value)
    mint_tx = cs_inst.check_output(cmd, shell=True)

    if b_get_events:
        cs_inst.popen_stdout(p, lambda x: x[-5:]==' } }\n')
        p.terminate()
        p.wait()

    cmd = utils.CmdBuiler.qtumjs_cli__balance(qhaX)
    cs_inst.check_output(cmd, shell=True)

    '''
    mint tx: b76f444b8e80bb79edbbf7fd9a75fb0a99384ee228b992efc7f391b2c87ca5fd
    { amount: 0,
      fee: -0.0812,
      confirmations: 0,
      ...
    '''
    txid = mint_tx.split('\n')[0].split(' ')[2]
    __dump_tx_info(cs_inst, logger, txid)


def __qhaX_transfer_token_to_qhaY(cs_inst, logger, qhaX, qhaY, value):

    b_get_events = False
    if b_get_events:
        cmd = utils.CmdBuiler.qtumjs_cli__events()
        p = cs_inst.popen(cmd, shell=True)

    cmd = utils.CmdBuiler.qtumjs_cli__transfer(qhaX, qhaY, value)
    mint_tx = cs_inst.check_output(cmd, shell=True)

    if b_get_events:
        cs_inst.popen_stdout(p, lambda x: x[-5:]==' } }\n')
        p.terminate()
        p.wait()

    cmd = utils.CmdBuiler.qtumjs_cli__balance(qhaX)
    cs_inst.check_output(cmd, shell=True)

    cmd = utils.CmdBuiler.qtumjs_cli__balance(qhaY)
    cs_inst.check_output(cmd, shell=True)

    '''
    mint tx: b76f444b8e80bb79edbbf7fd9a75fb0a99384ee228b992efc7f391b2c87ca5fd
    { amount: 0,
      fee: -0.0812,
      confirmations: 0,
      ...
    '''
    txid = mint_tx.split('\n')[0].split(' ')[2]
    __dump_tx_info(cs_inst, logger, txid)

def transfer_coin_to_a(cs_inst, logger):
    global addr_dict
    qha_a = addr_dict['a']
    __transfer_coin_to_qhaX(cs_inst, logger, qha_a, 100)

def transfer_coin_to_b(cs_inst, logger):
    global addr_dict
    qha_b = addr_dict['b']
    __transfer_coin_to_qhaX(cs_inst, logger, qha_b, 99)

def a_create_erc20contract(cs_inst, logger):
    global addr_dict
    qha_a = addr_dict['a']

    __qhaX_create_contract(cs_inst, logger, qha_a, 
        'zeppelin-solidity/contracts/token/ERC20/ERC20Capped.sol',
        '[21000000]'    
    )

def a_mint_token(cs_inst, logger):
    global addr_dict
    qha_a = addr_dict['a']
    __qhaX_mint_token(cs_inst, logger, qha_a, 100)

def a_transfer_token_to_b(cs_inst, logger):
    global addr_dict
    qha_a = addr_dict['a']
    qha_b = addr_dict['b']
    __qhaX_transfer_token_to_qhaY(
        cs_inst, logger, qha_a, qha_b, 40
    )

def b_transfer_token_to_c(cs_inst, logger):
    global addr_dict
    qha_b = addr_dict['b']
    qha_c = addr_dict['c']
    __qhaX_transfer_token_to_qhaY(
        cs_inst, logger, qha_b, qha_c, 15
    )

def go_step_by_step(cs_inst, logger):
    step_list = [
        transfer_coin_to_a,
        a_create_erc20contract,
        a_mint_token,
        a_transfer_token_to_b,
        transfer_coin_to_b,     #b调用合约转token给c，需要少量coin(token)作为gas
        b_transfer_token_to_c
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
