#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-


QTUM_PREFIX =   "/home/danx/std_workspace/qtum-package/"
QTUM_BIN    =   QTUM_PREFIX +  "bin/"
CMD_QTUMD   =   QTUM_BIN + "qtumd"
CMD_QTUMCLI =   QTUM_BIN + "qtum-cli"

########################################

QTUM_NODES  =   {
    'node1': {
        'NODEX__QTUM_DATADIR' : "/home/danx/std_workspace/qtum-data/node1/",
        'NODEX__PORT' : 13888,
        'NODEX__RCPPORT' : 13889,
        'NODEX__QTUM_RPC' : "http://test:test@localhost:%d" % 13889
    },
    'node2': {
        'NODEX__QTUM_DATADIR' : "/home/danx/std_workspace/qtum-data/node2/",
        'NODEX__PORT' : 14888,
        'NODEX__RCPPORT' : 14889,
        'NODEX__QTUM_RPC' : "http://test:test@localhost:%d" % 14889
    }
}

QTUM_DFT_NODE = 'node1'
