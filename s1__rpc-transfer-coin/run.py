#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import subprocess
import argparse,sys

sys.path.append('../py-utils/')
import utils

cs_inst = None

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

def transfer_coin_to_a(cs_inst, logger):

    cmd = utils.CmdBuiler.qtum_cli__getnewaddress()
    address = cs_inst.check_output(cmd, shell=True)
    cmd = utils.CmdBuiler.qtum_cli__sendtoaddress(address, 100)
    txid = cs_inst.check_output(cmd, shell=True)
    cmd = utils.CmdBuiler.qtum_cli__gettransaction(txid)
    cs_inst.check_output(cmd, shell=True)
    cmd = utils.CmdBuiler.qtum_cli__decoderawtxid(txid)
    cs_inst.check_output(cmd, shell=True)
    cmd = utils.CmdBuiler.qtum_cli__listunspent()
    cs_inst.check_output(cmd, shell=True)

def go_step_by_step(cs_inst, logger):
    step_list = [
        transfer_coin_to_a,
    ]
    for i in range(len(step_list)):
        step_name = 'step' + str(i)
        logger.info(step_name + '--' + step_list[i].__name__ + ' begin:')
        step_list[i](cs_inst, logger)
        logger.info(step_name + '--' + step_list[i].__name__ + ' end.')

def run(cs_inst, logger):

    go_step_by_step(cs_inst, logger)

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
