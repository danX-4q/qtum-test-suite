#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import subprocess
import os
import argparse

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
        'wrp-qtum-cli sendtoaddress <new-address> <value>',
        'wrp-qtum-cli gettransaction <txid>',
        'wrp-qtum-cli decoderawtxid <txid>',
        #'wrp-qtum-cli listunspent 0 50 <address-list>'
        'wrp-qtum-cli listunspent 0 50'
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
        
def transfer_coin_to_a(cs_inst, logger):
    global addr_dict
    qha_a = addr_dict['a']
    cmd = utils.CmdBuiler.qtum_cli__sendtoaddress(qha_a.getQa(), 100)
    txid = cs_inst.check_output(cmd, shell=True)
    cmd = utils.CmdBuiler.qtum_cli__gettransaction(txid)
    cs_inst.check_output(cmd, shell=True)
    cmd = utils.CmdBuiler.qtum_cli__decoderawtxid(txid)
    cs_inst.check_output(cmd, shell=True)
    cmd = utils.CmdBuiler.qtum_cli__listunspent()
    cs_inst.check_output(cmd, shell=True)

def a_create_erc20contract(cs_inst, logger):
    pass

def a_mint_token(cs_inst, logger):
    pass

def step4_a_transfer_token_to_b(cs_inst, logger):
    pass

def step5_b_transfer_token_to_c(cs_inst, logger):
    pass

def go_step_by_step(cs_inst, logger):
    step_list = [
        transfer_coin_to_a,
        a_create_erc20contract,
        #a_deploy_contract,
        #a_mint_token,
        #a_transfer_token_to_b,
        #b_transfer_token_to_c
    ]
    for i in range(len(step_list)):
        step_name = 'step' + str(i)
        logger.info(step_name + '--' + step_list[i].__name__ + ' begin:')
        step_list[i](cs_inst, logger)
        logger.info(step_name + '--' + step_list[i].__name__ + ' end.')

def run(cs_inst, logger):

    step0_prepare(cs_inst, logger)
    go_step_by_step(cs_inst, logger)

    #address = cs_inst.check_output('wrp-qtum-cli getnewaddress', shell=True)
    #txid = cs_inst.check_output('wrp-qtum-cli sendtoaddress %s 100' % address, shell=True)
    #txinfo = cs_inst.check_output('wrp-qtum-cli gettransaction %s' % txid, shell=True)
    #cs_inst.check_output('wrp-qtum-cli decoderawtxid %s' % txid, shell=True)
    ##cmd = 'wrp-qtum-cli listunspent 0 50 "[\\"%s\\"]"' % address
    #cmd = 'wrp-qtum-cli listunspent 0 50'
    #cs_inst.check_output(cmd, shell=True)

def main() :
    global cs_inst
    parser = argparse.ArgumentParser(
            description="qtum-test-suite -- s1__rpc-transfer-coin",
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
