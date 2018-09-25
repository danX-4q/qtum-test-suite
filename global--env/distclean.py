#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

from copy import deepcopy
import shutil, os, sys, argparse

from envconfig import *

DST_DIR = './dst-files/'

def load_env_kv() :    #return [prog_env, nodes_env]
    prog = {
        'QTUM_PREFIX' : QTUM_PREFIX,
        'QTUM_BIN' : QTUM_BIN,
        'CMD_QTUMD': CMD_QTUMD,
        'CMD_QTUMCLI': CMD_QTUMCLI
    }

    return [
        deepcopy(prog),
        deepcopy(QTUM_NODES)
    ]

def do(prog_args):

    env_kv = load_env_kv()
    prog_env = env_kv[0]
    nodes_env = env_kv[1]

    cmd = []
    #stop service
    for node_name in sorted(nodes_env.keys()) :
        cmd_wrp_qtum_cli = os.path.join(
            prog_env['QTUM_BIN'],
            node_name + '--' + 'wrp-qtum-cli.sh',
        )
        cmd.append(cmd_wrp_qtum_cli + ' stop')

    cmd += [
        'rm -rf %s' % os.path.join(prog_env['QTUM_BIN'], 'wrp-qtum-cli'),
        'rm -rf %s' % os.path.join(prog_env['QTUM_BIN'], 'wrp-qtumd'),
        'rm -rf %s' % os.path.join(prog_env['QTUM_BIN'], 'wrp-solar'),
        'rm -rf %s' % os.path.join(prog_env['QTUM_BIN'], '*wrp-qtum-cli.sh'),
        'rm -rf %s' % os.path.join(prog_env['QTUM_BIN'], '*wrp-qtumd.sh'),
        'rm -rf %s' % os.path.join(prog_env['QTUM_BIN'], '*wrp-solar.sh'),
    ]

    for node_name in sorted(nodes_env.keys()) :
        node_datadir = nodes_env[node_name]['NODEX__QTUM_DATADIR']
        cmd.append('rm -rf %s' % node_datadir)

    print 'to distclean, all commands followed: '
    print '#' * 40
    for c in cmd:
        print c
    print '#' * 40
    if prog_args.execute :
        print 'start executing commands'
        print '>' * 40
        for c in cmd :
            print c
            os.system(c)
            print '-' * 8
        print '<' * 40
        print 'over.'
    
    else :
        print 'add -e|--execute to really execute commands.'

def main() :

    parser = argparse.ArgumentParser(
            description="qtum-test-suite -- distclean",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-e', '--execute', action='store_true',
                        dest='execute', help='really execute commands!')
    prog_args = parser.parse_args()
    #print prog_args
    do(prog_args)

if __name__ == '__main__' :
    main()
