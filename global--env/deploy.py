#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

from copy import deepcopy
import shutil, os, sys

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


def main() :

    env_kv = load_env_kv()
    prog_env = env_kv[0]
    nodes_env = env_kv[1]

    for node_name in sorted(nodes_env.keys()) :

        node_datadir = nodes_env[node_name]['NODEX__QTUM_DATADIR']
        try:
            os.makedirs(node_datadir)
        except (OSError) as e :
            if e.errno == 17 :
                print 'node_datadir(%s) seems not empty, please check it artificially. prog exit now.' % node_datadir
                sys.exit(1)
            else :
                raise

        f = os.listdir(node_datadir)
        if len(f) != 0:
            print 'node_datadir(%s) seems not empty, please check it artificially. prog exit now.'
            sys.exit(1)
        ####
        node_dir = os.path.join(DST_DIR, node_name)
        ####
        f_s = os.path.join(node_dir, 'qtum.conf')
        f_d = os.path.join(node_datadir, 'qtum.conf')
        shutil.copy(f_s, f_d)
        ####
        filename = node_name + '--' + 'wrp-qtumd.sh'
        f_s = os.path.join(node_dir, filename)
        f_d = os.path.join(QTUM_BIN, filename)
        shutil.copy(f_s, f_d)
        os.system('chmod +x %s ' % f_d)
        ####
        filename = node_name + '--' + 'wrp-qtum-cli.sh'
        f_s = os.path.join(node_dir, filename)
        f_d = os.path.join(QTUM_BIN, filename)
        shutil.copy(f_s, f_d)
        os.system('chmod +x %s ' % f_d)
        ####
        filename = node_name + '--' + 'wrp-solar.sh'
        f_s = os.path.join(node_dir, filename)
        f_d = os.path.join(QTUM_BIN, filename)
        shutil.copy(f_s, f_d)
        os.system('chmod +x %s ' % f_d)

    ####
    f_s = os.path.join(DST_DIR, 'qtum-path.sh')
    f_d = os.path.join('/etc/profile.d', 'qtum-path.sh')
    cmd = "sudo cp -rf %s %s" % (f_s, f_d)
    print "cmd(%s) to set PATH, sudo, need root's password" % cmd
    os.system(cmd)

if __name__ == '__main__' :
    main()
