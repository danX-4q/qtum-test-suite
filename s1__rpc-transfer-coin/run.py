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
        'wrp-qtum-cli decoderawtxid <txid>'
    ]
    for c in cmds:
        print c

def run(cs_inst, logger):

    cmd = 'wrp-qtum-cli getnewaddress'
    address = cs_inst.check_output(cmd, shell=True)
    txid = cs_inst.check_output('wrp-qtum-cli sendtoaddress %s 100' % address, shell=True)
    txinfo = cs_inst.check_output('wrp-qtum-cli gettransaction %s' % txid, shell=True)
    cs_inst.check_output('wrp-qtum-cli decoderawtxid %s' % txid, shell=True)

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
