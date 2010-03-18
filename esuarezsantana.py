#!/usr/bin/python
# -*- coding: utf-8

##########################################################
#
#   Author:  Eduardo Suarez-Santana
#            http://e.suarezsantana.com/
#
#     Date:  2010 03 18
#
#  License:  GPL-v3
#

import ConfigParser, os;

def getConfig():
    ftf_config = ConfigParser.ConfigParser();
    ftf_config.read(['/usr/share/esuarezsantana/esuarezsantanarc',os.path.expanduser('~/.esuarezsantanarc')]);
    return ftf_config;

