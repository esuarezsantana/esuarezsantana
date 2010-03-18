#!/usr/bin/python
# -*- coding: utf-8

#####################################################################
#
#   Copyright 2010 Eduardo Suarez-Santana
#                  http://e.suarezsantana.com/
#
#   This file is part of esuarezsantana utilities.
#
#   esuarezsantana utilities are free software: you can redistribute
#   them and/or modify them under the terms of the GNU General
#   Public License as published by the Free Software Foundation,
#   either version 3 of the License, or any later version.
#
#   esuarezsantana utilities are distributed in the hope that it 
#   will be useful, but WITHOUT ANY WARRANTY; without even the 
#   implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#


import ConfigParser, os;

def getConfig():
    config = ConfigParser.ConfigParser();
    config.read(['/usr/share/esuarezsantana/esuarezsantanarc',os.path.expanduser('~/.esuarezsantanarc')]);
    return config;

