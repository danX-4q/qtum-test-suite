#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import subprocess
import argparse,sys

sys.path.append('../py-utils/')
import utils

cs_inst = None

def dry_run() :
    cmds = [
        'wrp-qtum-cli generate 800',
        'wrp-qtum-cli getnewaddress',
        'wrp-qtum-cli gethexaddress <new-address>',
        'wrp-qtum-cli getbalance'
    ]
    for c in cmds:
        print c

def run(cs_inst, logger):
    cs_inst.check_call('wrp-qtum-cli generate 10', shell=True)

    qa_ha = []
    for i in range(10) :
        cmd = 'wrp-qtum-cli getnewaddress'
        qa = cs_inst.check_output(cmd, shell=True)
        cmd = 'wrp-qtum-cli gethexaddress %s' % qa
        ha = cs_inst.check_output(cmd, shell=True)
        qa_ha.append((qa, ha))

    file_name = 'rt-data/qa_ha.txt'
    with open(file_name, 'w') as f:
        i = 0
        for qa, ha in qa_ha :
            line = 'QA_%d:%s HA_%d:%s\n' % (i, qa, i, ha)
            f.write(line)
            i += 1
    logger.info('dump addresses to file %s ' % file_name)
    cs_inst.check_output(
        'wrp-qtum-cli getbalance',
        shell=True
    )

def main() :
    global cs_inst
    parser = argparse.ArgumentParser(
            description="qtum-test-suite -- s0__genesis",
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
