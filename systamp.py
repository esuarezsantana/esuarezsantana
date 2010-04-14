#!/usr/bin/python
# -*- coding: utf-8

#####################################################################
#
#   This file is part of esuarezsantana utilities.
#   Module:      systamp.py
#   Description: tool for local backup of small text files
#
#   Copyright (C) 2010 Eduardo Suarez-Santana
#                      http://e.suarezsantana.com/
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
#   along with esuarezsantana utilities.  If not, see
#   <http://www.gnu.org/licenses/>.
#


import ConfigParser;
import sys,re
from optparse import OptionParser
import socket;
import os
from os.path import *;

import esuarezsantana;

config=esuarezsantana.getConfig();
# fake another distro
fakedistro   = config.get('systamp','fakedistro');
# fake another hostname
fakehostname = config.get('systamp','fakehostname');
# where the root (/) system is mounted. Blank for /
prefix       = config.get('systamp','prefix');
# where bonsai dir is
basepath     = config.get('systamp','basepath');



def unprefix(localpath, prefix):
    # check whether it starts with prefix
    
    if re.search('^'+prefix, localpath):
        
	if re.search('/$',prefix):
	    prefix = prefix[:-1];
	
	return localpath[len(prefix):];

    else:
        print "Path does not belong to systamp tree"
	sys.exit(1);


def main():

    ########################################################################
    #
    # 1. Getopt
    #

    usage = "%prog -h|-o|-p\n\
       %prog [-p|-i|-s|-l|-d N|-r N] etcfile"

    parser = OptionParser(usage=usage)

    parser.add_option("-o", "--overlay", dest="action_overlay",
                      default="False",
                      action="store_true", help="System overlay file")

    parser.add_option("-p", "--path", dest="action_path",
                      default="False",
                      action="store_true", help="Path to root dir")

    parser.add_option("-i", "--info", dest="action_info",
                      default="False",
                      action="store_true", help="File info")

    parser.add_option("-s", "--stamp", dest="action_stamp",
                      default="False",
                      action="store_true", help="Stamp file")

    parser.add_option("-l", "--last", dest="action_last", action="store_true",
                      default="False",
                      help="Show diff with last version (equals -d 0)");

    parser.add_option("-d", "--diff", dest="diff_version", metavar="VERSION",
                      type="int", default=-1, 
                      help="Show diff with version VERSION (0 for last)");

    parser.add_option("-r", "--recover", dest="recover_version", metavar="VERSION",
                      type="int", default=-1,
                      help="Recover version VERSION (0 for last)");

    (options, args) = parser.parse_args()

    # for debugging
    #print options
    #print args

    ########################################################################
    #
    # 2. Parsing
    #

    # Only one modifier

    n_args = len(args);

    n_modifier=0;
    action = "none";
    arg_file = "none";

    no_argument_valid_actions = ["path", "overlay"];
    one_argument_valid_actions = ["path", "info", "stamp", "last", "diff",
                                  "recover"];

    executable_name = basename(sys.argv[0]);

    if options.action_path==True    :
        n_modifier = n_modifier + 1;
        action = "path";

    if options.action_overlay==True :
        n_modifier = n_modifier + 1;
        action = "overlay";

    if options.action_stamp==True   :
        n_modifier = n_modifier + 1;
        action = "stamp";

    if options.action_info==True    :
        n_modifier = n_modifier + 1;
        action = "info";
        
    if options.action_last==True    :
        n_modifier = n_modifier + 1;
        action = "last";

    if options.diff_version!=-1     :
        n_modifier = n_modifier + 1;
        action = "diff";

    if options.recover_version!=-1  :
        n_modifier = n_modifier + 1;
        action = "recover";


    if n_modifier > 1 :
        print "%s: Only one modifier allowed\n" % executable_name
        parser.print_help();
        sys.exit(1);


    if n_args == 0:
        if not (action in no_argument_valid_actions):
            print "%s: Action %s needs an argument\n" % (executable_name, action)
            parser.print_help();
            sys.exit(1);


    if n_modifier == 0 and n_args != 1:
        print "%s: At least one modifier needed\n" % executable_name
        parser.print_help();
        sys.exit(1);

    if n_modifier == 0 and n_args == 1:
        action = "info";

    if n_args == 1:
        if not (action in one_argument_valid_actions):
            print "%s: Action %s does not need an argument\n" % (executable_name, action)
            parser.print_help();
            sys.exit(1);

        arg_file = args[0];
	# p_: prefix
        p_abs_filename = abspath( arg_file );
        u_abs_filename = unprefix( p_abs_filename, prefix );

        if not(os.access(p_abs_filename, os.F_OK)):
            print "Object does not exist: %s\n" % p_abs_filename
            sys.exit(1);

    elif n_args >= 2:
        print "%s: Only one file argument allowed\n" % executable_name
        parser.print_help();
        sys.exit(1);


    ########################################################################
    #
    # 3. Global variables
    #

    if fakehostname == '':
        hostname = socket.gethostname();
    else:
        hostname = fakehostname;

    if fakedistro == '':
        if isfile(prefix + '/etc/debian_version'):
            distro = 'debian';
        elif isfile(prefix + '/etc/gentoo-release'):
            distro = 'gentoo';
        else:
            print "Unknown distro"
            sys.exit(1)
    else:
        distro = fakedistro;


    # output path
    path_systamp  = join(basepath, distro, hostname );
    path_bonsai   = join(path_systamp, 'bonsai' );

    # does it exist?
    if not isdir( path_bonsai ):
        print "Directory does not exist: %s\n" % path_bonsai;
        sys.exit(1);


 
    ########################################################################
    #
    # 4. Actions
    #

    ############################################################### PATH
    if action == "path" :
        
        # no args, then local path
        if n_args == 0 :
            print path_bonsai
            sys.exit(0);

        # object is a dir, we take it
        if isdir(p_abs_filename):

            # take out slash at the end
            if re.search("/$", u_abs_filename):
                u_abs_filename = u_abs_filename[:-1];

            u_basedir = u_abs_filename;

        # else, we take parent directory
        else:
            u_basedir = dirname(u_abs_filename);

        bonsai_basedir = path_bonsai + u_basedir;

        if not exists(bonsai_basedir):
            print "Warning: the directory doesn't exist:"

        print bonsai_basedir

        sys.exit(0);

    ############################################################ OVERLAY
    elif action == "overlay" :

        # overlay/overlay.txt for now
        path_overlay   = join(path_systamp, 'overlay/overlay.txt' );

        if isfile(path_overlay) and not islink(path_overlay):
            print path_overlay
            sys.exit(0)
        else:
            print "%s: Does not exists or it is not a file\n" % executable_name
            print path_overlay
            sys.exit(1)

    ############################################################## STAMP
    elif action == "stamp":

        filename_bonsai = path_bonsai + u_abs_filename;

        # original is a file
        if isfile(p_abs_filename) and not islink(p_abs_filename):

            # is a direct path
            [p_abs_dirname, nombrebase] = split(p_abs_filename);
            if realpath(p_abs_dirname) != p_abs_dirname:
                print "%s: la ruta contiene enlaces:" % executable_name
                print p_abs_dirname
                sys.exit(1);

            # there is no mirror
            if not exists(filename_bonsai):
                # we just copy
                [bonsai_dirname, filename] = split(filename_bonsai);
                os.environ['bonsai_dirname']=bonsai_dirname;
                os.system('mkdir -p "$bonsai_dirname"');
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai']=filename_bonsai;
                os.system('echo cp -pv "$p_abs_filename" "$filename_bonsai"');
                os.system('cp -pv "$p_abs_filename" "$filename_bonsai"');
                sys.exit(0)

            # mirror is a file
            elif isfile(filename_bonsai) and not islink(filename_bonsai):

                f_slash = open( p_abs_filename );
                f_slash_content = f_slash.readlines();
                f_slash.close();

                f_bonsai = open( filename_bonsai );
                f_bonsai_content = f_bonsai.readlines();
                f_bonsai.close();

                # same content
                if f_slash_content == f_bonsai_content:
                    # do not stamp
                    print "%s: Same content:\n" % executable_name
                    os.environ['p_abs_filename']=p_abs_filename;
                    os.environ['filename_bonsai']=filename_bonsai;
                    os.system('ls -la "$p_abs_filename"'); 
                    os.system('ls -la "$filename_bonsai"'); 
                    print "%s: no stamp done\n" % executable_name
                    sys.exit(1)

                else:
                    # copy with version
                    [bonsai_dirname, filename] = split(filename_bonsai);
                    os.environ['bonsai_dirname']=bonsai_dirname;
                    os.system('mkdir -p "$bonsai_dirname"');
                    os.environ['p_abs_filename']=p_abs_filename;
                    os.environ['filename_bonsai']=filename_bonsai;
                    os.system('echo cp -pv --backup=numbered "$p_abs_filename" "$filename_bonsai"');
                    os.system('cp -pv --backup=numbered "$p_abs_filename" "$filename_bonsai"');
                    sys.exit(0)

            else:
                # error different types
                print "%s: objects of different types" % executable_name
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai']=filename_bonsai;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai"'); 
                sys.exit(1);

        # original is a link
        elif islink(p_abs_filename):

            # check for a direct path
            [p_abs_dirname, nombrebase] = split(p_abs_filename);
            if realpath(p_abs_dirname) != p_abs_dirname:
                print "%s: path contains links" % executable_name
                print p_abs_dirname
                sys.exit(1);

            u_abs_obj = os.readlink(p_abs_filename);

            # mirror does not exist
            if not exists(filename_bonsai):
                # just copy
                [bonsai_dirname, filename] = split(filename_bonsai);
                os.environ['bonsai_dirname'] = bonsai_dirname;
                os.system('mkdir -p "$bonsai_dirname"');
                os.environ['u_abs_obj'] = u_abs_obj;
                os.environ['filename_bonsai'] = filename_bonsai;
                # created with shell
                os.system('echo ln -s "$u_abs_obj" "$filename_bonsai"');
                os.system('ln -s "$u_abs_obj" "$filename_bonsai"');
                sys.exit(0)

            # mirror is a link
            elif islink(filename_bonsai):

                u_bonsai_obj = os.readlink(filename_bonsai);

                # same objectives
                if u_abs_obj == u_bonsai_obj:
                    # does not stamp
                    print "%s: same link target:\n" % executable_name
                    os.environ['p_abs_filename']=p_abs_filename;
                    os.environ['filename_bonsai']=filename_bonsai;
                    os.system('ls -la "$p_abs_filename"'); 
                    os.system('ls -la "$filename_bonsai"'); 
                    print "%s: no stamp done\n" % executable_name
                    sys.exit(1)

                # else
                else:
                    # copy with version
                    [bonsai_dirname, filename] = split(filename_bonsai);
                    os.environ['bonsai_dirname']=bonsai_dirname;
                    os.system('mkdir -p "$bonsai_dirname"');
                    os.environ['p_abs_filename']=p_abs_filename;
                    os.environ['filename_bonsai']=filename_bonsai;
                    os.system('echo cp -pdv --backup=numbered "$p_abs_filename" "$filename_bonsai"');
                    os.system('cp -pdv --backup=numbered "$p_abs_filename" "$filename_bonsai"');
                    sys.exit(0)

            # else
            else:
                # different types
                print "%s: objects of different types" % executable_name
                print p_abs_filename
                print filename_bonsai
                sys.exit(1);

        # else
        else:
            # nothing to do
            print "%s: does not exists or it is neither a file nor a link:\n" % executable_name
            print p_abs_filename
            sys.exit(1)

        print "Internal error! Check source!\n"

    ############################################################### INFO
    elif action == "info" :
        
        filename_bonsai = path_bonsai + u_abs_filename;

        if isfile(p_abs_filename) and not islink(p_abs_filename):

            if isfile(filename_bonsai) and not islink(filename_bonsai):

                # list of versions
                os.environ['path_bonsai']=path_bonsai;
		# take out slash
                os.environ['short_filename_bonsai']=u_abs_filename[1:];
                print "%s: Versions available:" % executable_name
                os.system('cd "$path_bonsai";ls -la "$short_filename_bonsai"*');

                # is there any stamp?
                f_slash = open( p_abs_filename );
                f_slash_content = f_slash.readlines();
                f_slash.close();

                f_bonsai = open( filename_bonsai );
                f_bonsai_content = f_bonsai.readlines();
                f_bonsai.close();

                if f_slash_content == f_bonsai_content:
                    print "\n%s: root file is already stamped" % executable_name
                else:
                    print "\n%s: root file is NOT stamped" % executable_name

                sys.exit(0);

            elif exists(filename_bonsai):

                # error different types
                print "%s: objects of different type:" % executable_name
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai']=filename_bonsai;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai"'); 
                sys.exit(1);

            else:
                print "%s: bonsai object does not exist:" % executable_name
                print filename_bonsai
                sys.exit(0)

        elif islink(p_abs_filename):
            if islink(filename_bonsai):

                # list of versions
                os.environ['path_bonsai']=path_bonsai;
                os.environ['short_filename_bonsai']=u_abs_filename[1:];
                print "%s: Versions available:" % executable_name
                os.system('cd "$path_bonsai";ls -la "$short_filename_bonsai"*');

                # stamp?
                f_slash_content  = os.readlink( p_abs_filename );
                f_bonsai_content = os.readlink( filename_bonsai );

                if f_slash_content == f_bonsai_content:
                    print "\n%s: root file is already stamped" % executable_name
                else:
                    print "\n%s: root file is NOT stamped" % executable_name

                sys.exit(0);

            elif exists(filename_bonsai):

                # error different types
                print "%s: objects of different type:" % executable_name
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai']=filename_bonsai;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai"'); 
                sys.exit(1);

            else:
                print "%s: bonsai object does not exist:" % executable_name
                print filename_bonsai
                sys.exit(1)

        else:
            print "%s: bonsai object does not exist:\n" % executable_name
            print p_abs_filename
            sys.exit(1)


    ############################################################### LAST
    elif action == "last" :

        filename_bonsai = path_bonsai + u_abs_filename;

        if isfile(p_abs_filename) and not islink(p_abs_filename):

            if isfile(filename_bonsai) and not islink(filename_bonsai):

                # check differences
                f_slash = open( p_abs_filename );
                f_slash_content = f_slash.readlines();
                f_slash.close();

                f_bonsai = open( filename_bonsai );
                f_bonsai_content = f_bonsai.readlines();
                f_bonsai.close();

                if f_slash_content == f_bonsai_content:
                    print "%s: same content:" % executable_name
                    print p_abs_filename
                    print filename_bonsai

                else:
                    os.environ['filename_bonsai']=filename_bonsai;
                    os.environ['p_abs_filename']=p_abs_filename;
                    os.system('diff -u "$filename_bonsai" "$p_abs_filename"');

            elif exists(filename_bonsai):

                # error different types
                print "%s: objects of different type" % executable_name
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai']=filename_bonsai;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai"'); 
                sys.exit(1);

            else:
                print "%s: bonsai object does not exist:" % executable_name
                print filename_bonsai
                sys.exit(0)

        elif islink(p_abs_filename):
            if islink(filename_bonsai):

                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai']=filename_bonsai;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai"'); 
                sys.exit(0);

            elif exists(filename_bonsai):

                # error different types
                print "%s: objects of different type:" % executable_name
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai']=filename_bonsai;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai"'); 
                sys.exit(1);

            else:
                print "%s: bonsai object does not exist:" % executable_name
                print filename_bonsai
                sys.exit(1)

        else:
            print "%s: bonsai object does not exist:\n" % executable_name
            print p_abs_filename
            sys.exit(1)


    ############################################################### DIFF
    elif action == "diff" :

        if options.diff_version==0:
            filename_bonsai_ver = path_bonsai + u_abs_filename;
        else:
            filename_bonsai_ver = path_bonsai + u_abs_filename + \
                ".~" + str(options.diff_version) + "~";

        if isfile(p_abs_filename) and not islink(p_abs_filename):

            if isfile(filename_bonsai_ver) and not islink(filename_bonsai_ver):

                # check differences
                f_slash = open( p_abs_filename );
                f_slash_content = f_slash.readlines();
                f_slash.close();

                f_bonsai = open( filename_bonsai_ver );
                f_bonsai_content = f_bonsai.readlines();
                f_bonsai.close();

                if f_slash_content == f_bonsai_content:
                    print "%s: same content:" % executable_name
                    print p_abs_filename
                    print filename_bonsai_ver

                else:
                    os.environ['filename_bonsai_ver']=filename_bonsai_ver;
                    os.environ['p_abs_filename']=p_abs_filename;
                    os.system('diff -u "$filename_bonsai_ver" "$p_abs_filename"');

            elif exists(filename_bonsai_ver):

                # error different types
                print "%s: objects of different type:" % executable_name
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai_ver']=filename_bonsai_ver;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai_ver"'); 
                sys.exit(1);

            else:
                print "%s: bonsai object does not exist:" % executable_name
                print filename_bonsai_ver
                sys.exit(0)

        elif islink(p_abs_filename):
            if islink(filename_bonsai_ver):

                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai_ver']=filename_bonsai_ver;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai_ver"'); 
                sys.exit(0);

            elif exists(filename_bonsai_ver):

                # error tipos distintos
                print "%s: objects of different type:" % executable_name
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai_ver']=filename_bonsai_ver;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai_ver"'); 
                sys.exit(1);

            else:
                print "%s: bonsai object does not exist:" % executable_name
                print filename_bonsai_ver
                sys.exit(1)

        else:
            print "%s: root object does not exist:\n" % executable_name
            print p_abs_filename
            sys.exit(1)


    ############################################################ RECOVER
    elif action == "recover" :

        if options.recover_version==0:
            filename_bonsai_ver = path_bonsai + u_abs_filename;
        else:
            filename_bonsai_ver = path_bonsai + u_abs_filename + \
                ".~" + str(options.recover_version) + "~";

        if isfile(p_abs_filename) and not islink(p_abs_filename):

            if isfile(filename_bonsai_ver) and not islink(filename_bonsai_ver):

                # check differences
                f_slash = open( p_abs_filename );
                f_slash_content = f_slash.readlines();
                f_slash.close();

                f_bonsai = open( filename_bonsai_ver );
                f_bonsai_content = f_bonsai.readlines();
                f_bonsai.close();

                if f_slash_content == f_bonsai_content:
                    print "%s: same content" % executable_name
                    print p_abs_filename
                    print filename_bonsai_ver
                    print "%s: no recover done" % executable_name

                else:
                    os.environ['filename_bonsai_ver']=filename_bonsai_ver;
                    os.environ['p_abs_filename']=p_abs_filename;
                    print "%s: command to recover:" % executable_name
                    os.system('echo \# cp -p "$filename_bonsai_ver" "$p_abs_filename"');
                    answ = raw_input('Recover (y/N)? ');
                    if answ == 'y':
                        os.system('cp -p "$filename_bonsai_ver" "$p_abs_filename"');

                    sys.exit(0);


            elif exists(filename_bonsai_ver):

                # error different types
                print "%s: objects of different type" % executable_name
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai_ver']=filename_bonsai_ver;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai_ver"'); 
                sys.exit(1);

            else:
                print "%s: bonsai object does not exist:" % executable_name
                print filename_bonsai_ver
                sys.exit(0)

        elif islink(p_abs_filename):
            if islink(filename_bonsai_ver):

                # stamp?
                f_slash_content = os.readlink( p_abs_filename );
                f_bonsai_content = os.readlink( filename_bonsai );

                if f_slash_content == f_bonsai_content:
                    os.environ['p_abs_filename']=p_abs_filename;
                    os.environ['filename_bonsai_ver']=filename_bonsai_ver;
                    os.system('ls -la "$p_abs_filename"'); 
                    os.system('ls -la "$filename_bonsai_ver"'); 
                    sys.exit(0);

                else:

                    os.environ['filename_bonsai_ver'] = filename_bonsai_ver;
                    os.environ['p_abs_filename'] = p_abs_filename;
                    print "%s: Command to recover:" % executable_name
                    os.system('echo \# cp -pd "$filename_bonsai_ver" "$p_abs_filename"');
                    answ = raw_input('Recover (y/N)? ');
                    if answ == 'y':
                        os.system('cp -pd "$filename_bonsai_ver" "$p_abs_filename"'); 
                    sys.exit(0);


            elif exists(filename_bonsai_ver):

                # error different types
                print "%s: objects of different type" % executable_name
                os.environ['p_abs_filename']=p_abs_filename;
                os.environ['filename_bonsai_ver']=filename_bonsai_ver;
                os.system('ls -la "$p_abs_filename"'); 
                os.system('ls -la "$filename_bonsai_ver"'); 
                sys.exit(1);

            else:
                print "%s: bonsai object does not exist:" % executable_name
                print filename_bonsai_ver
                sys.exit(1)

        else:
            print "%s: root file does not exist:\n" % executable_name
            print p_abs_filename
            sys.exit(1)

    else:
        print "Internal error! Check source"
        parser.print_help();
        sys.exit(1);



if __name__ == "__main__":
    main()

