#! /usr/bin/python

#Copyright (C) 2009 Johan Grip
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys

import wad

def usage():
    print """
Usage:
    e <wadfile> <destination>
       Unpacks wadfile into destination directory.
    p <wadfile> <source>
       Creates a new wadfile from a source directory.
"""

def main():
    print "WAD Tool 0.1"
    if len(sys.argv) != 4:
        usage()
        exit()

    if sys.argv[1] == 'e':
        print "Reading wad file %s" % (sys.argv[2])
        try:
            wadfile = wad.load(sys.argv[2])
        except IOError, err:
            print err
            exit()
        print "Extracting into %s" % (sys.argv[3])
        try:
            wadfile.extract(sys.argv[3])
        except IOError, err:
            print err
    
    if sys.argv[1] == 'p':
        print "Reading directory %s" % (sys.argv[3])
        try:
            wadfile = wad.fromdirectory(sys.argv[3])
        except IOError, err:
            print err
            exit()
        print "Saving WAD file %s" % (sys.argv[2])
        try:
            wadfile.save(sys.argv[2])
        except IOError, err:
            print err

if __name__ == "__main__":
    main()
    