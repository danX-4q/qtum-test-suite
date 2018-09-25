#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

from copy import deepcopy
import shutil, os

from envconfig import *

SRC_DIR = './src-files/'
DST_DIR = './dst-files/'

def eval_tmpl_prog (tmpl_file, dst_file, prog_env) :
    t = file(tmpl_file)
    d = file(dst_file, 'w')
    s = t.read()
    d.write(s % prog_env)

def eval_tmpl_node(tmpl_file, dst_file, prog_env, node_env) :
    t = file(tmpl_file)
    d = file(dst_file, 'w')
    s = t.read()
    env = deepcopy(prog_env)
    env.update(node_env)
    d.write(s % env)


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


    shutil.rmtree(DST_DIR)
    os.mkdir(DST_DIR)
    with open(os.path.join(DST_DIR, '.gitkeep'), 'w') as f:
        pass

    eval_tmpl_prog(
        os.path.join(SRC_DIR, 'qtum-path.sh.tmpl'), 
        os.path.join(DST_DIR, 'qtum-path.sh'), 
        prog_env
    )

    for node_name in sorted(nodes_env.keys()) :
        node_dir = os.path.join(DST_DIR, node_name)
        os.mkdir(node_dir)
        ####
        f_s = os.path.join(SRC_DIR, 'nodeX--qtum.conf.tmpl')
        f_d = os.path.join(node_dir, 'qtum.conf')
        node_env = nodes_env[node_name]     #not nodes_env
        eval_tmpl_node(f_s, f_d, prog_env, node_env)
        ####
        f_s = os.path.join(SRC_DIR, 'nodeX--wrp-qtumd.sh.tmpl')
        f_d = os.path.join(node_dir, node_name + '--' + 'wrp-qtumd.sh')
        node_env = nodes_env[node_name]     #not nodes_env
        eval_tmpl_node(f_s, f_d, prog_env, node_env)
        ####
        f_s = os.path.join(SRC_DIR, 'nodeX--wrp-qtum-cli.sh.tmpl')
        f_d = os.path.join(node_dir, node_name + '--' + 'wrp-qtum-cli.sh')
        node_env = nodes_env[node_name]     #not nodes_env
        eval_tmpl_node(f_s, f_d, prog_env, node_env)
        ####
        f_s = os.path.join(SRC_DIR, 'nodeX--wrp-solar.sh.tmpl')
        f_d = os.path.join(node_dir, node_name + '--' + 'wrp-solar.sh')
        node_env = nodes_env[node_name]     #not nodes_env
        eval_tmpl_node(f_s, f_d, prog_env, node_env)
        ####

if __name__ == '__main__' :
    main()
