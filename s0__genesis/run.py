#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import subprocess
import argparse,sys

def dry_run() :
    cmds = [
        'wrp-qtum-cli generate 800',
        'wrp-qtum-cli getnewaddress',
        'wrp-qtum-cli gethexaddress <new-address>',
        'wrp-qtum-cli getbalance'
    ]
    for c in cmds:
        print c

def run():
    subprocess.check_call(
        'wrp-qtum-cli generate 800',
        shell=True
    )

    qa_ha = []
    for i in range(10) :
        cmd = 'wrp-qtum-cli getnewaddress'
        qa = subprocess.check_output(cmd, shell=True) #end with \n
        cmd = 'wrp-qtum-cli gethexaddress %s' % qa
        ha = subprocess.check_output(cmd, shell=True) #end with \n
        qa_ha.append((qa, ha))

    file_name = 'rt-data/qa_ha.txt'
    with open(file_name, 'w') as f:
        i = 0
        for qa, ha in qa_ha :
            line = 'QA_%d:%sHA_%d:%s' % (i, qa, i, ha)
            f.write(line)
            i += 1
    print 'dump addresses to file %s ' % file_name
    print '-' * 20

    print 'show total balance:'
    subprocess.check_call(
        'wrp-qtum-cli getbalance',
        shell=True
    )

def main() :

    parser = argparse.ArgumentParser(
            description="qtum-test-suite -- s0__genesis",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-d', '--dry-run', action='store_true',
                        dest='dry_run', help='enable dry-run')
    prog_args = parser.parse_args()
    #print prog_args

    if prog_args.dry_run :
        dry_run()
    else :
        run()

if __name__ == '__main__' :
    main()
