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
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#MA  02110-1301, USA.

import os
import os.path
import struct


class WadObject(object):
    """Represents an object inside a WAD file"""
    def __init__(self, name, srcname=None, version=None, size=None, offset=None):
        self.name = name
        self.srcname = srcname
        self.version = version
        self.size = size
        self.offset = offset
        self._data = None
        self.is_loaded = False

    def __repr__(self):
        return "WadObject(%s)" % self.name

    def unload(self):
        """Unload data from memory"""
        self._data = None
        self.is_loaded = None

    def get_data(self):
        # If data is already loaded, return it
        if self.is_loaded:
            return self._data
        else:
            # Right, are we reading the data out of a wad file?
            if '.wad' in self.srcname.lower() and self.size and self.offset:
                f = None
                try:
                    f = open(self.srcname, 'rb')
                    f.seek(self.offset)
                    self._data = f.read(self.size)
                    self.is_loaded = True
                    return self._data
                finally:
                    if f is not None:
                        f.close()
            else:
                # Data is from a standalone file in the filesystem
                f = None
                try:
                    f = open(self.srcname, 'rb')
                    self._data = f.read()
                    self.size = len(self._data)
                    self.is_loaded = True
                    return self._data
                finally:
                    if f is not None:
                        f.close()

    def set_data(self, data):
        self._data = data
        self.is_loaded = True
        self.size = len(self._data)
        self.offset = None

    data = property(get_data, set_data)


class WadFile(object):
    """Represents a WAD file"""
    def __init__(self):
        self._objects = {}

    def __iter__(self):
        return self._objects.__iter__()

    def add(self, wadobj):
        """Add a wad object to the container"""
        self._objects[wadobj.name] = wadobj

    def get(self, name):
        """Return a specified object"""
        return self._objects[name]

    def load(self, filename):
        """Load a wad file"""
        ## Generator function for reading null terminated strings.
        def _readcstring(fil):
            x = fil.read(1)
            while x != '\0':
                yield x
                x = fil.read(1)

        f = None
        try:
            f = open(filename, 'rb')
            # Read and verify wad signature
            sig = f.read(4)
            if sig == "WWAD":
                # Read the number of files that the wad contains
                numfiles = struct.unpack("=L", f.read(4))[0]
                # Then read the names and source names
                reldirs = [''.join(_readcstring(f)) for x in range(numfiles)]
                absdirs = [''.join(_readcstring(f)) for x in range(numfiles)]
                # Then we unpack and read the file attributes
                filedata = [struct.unpack('=4L', f.read(16)) for x in range(numfiles)]
                for i in range(numfiles):
                    self.add(WadObject(reldirs[i], filename, filedata[i][0], filedata[i][1], filedata[i][3]))
            else:
                raise IOError("Not a WAD file")
        except IOError, msg:
            raise IOError(msg)
        finally:
            if f is not None:
                f.close()

    def extract(self, dirname):
        """ Extract contents to a directory """
        if not os.path.exists(dirname):
            raise IOError("Target directory does not exist")
        for ob in self._objects:
            obj = self._objects[ob]
            name = obj.name.replace('\\','/')
            print name
            dir, name = os.path.split(name)
            dir = os.path.join(dirname, dir)
            if not os.path.exists(dir):
                os.makedirs(dir)
            f = open(os.path.join(dir, name), 'wb')
            f.write(obj.data)
            f.close()
            obj.unload()

    def save(self, wadname):
        """ Save to a wadfile """
        f = open(wadname, 'wb')
        # Write header and number of files
        f.write('WWAD')
        f.write(struct.pack('=L', len(self._objects)))
        # Generate a sorted list of objects
        objs = sorted(self._objects, key=str.lower)
        # Write file names
        for ob in objs:
            obj = self._objects[ob]
            f.write(struct.pack('%ds' % (len(obj.name) + 1), obj.name))
        # Write file source names
        for ob in objs:
            obj = self._objects[ob]
            f.write(struct.pack('%ds' % (len(obj.srcname) + 1), obj.srcname.replace('/', '\\')))
        # Calculate file data offset starting point
        offs = f.tell() + (16 * len(self._objects))
        # Write file offset and size table
        for ob in objs:
            obj = self._objects[ob]
            f.write(struct.pack('=4L', obj.version, obj.size, obj.size, offs))
            offs += obj.size
        # Write the actual file data
        for ob in objs:
            obj = self._objects[ob]
            f.write(obj.data)
            # Unload file data from memory again, don't be a hog
            obj.unload()
        f.close()


##
## Utility functions
##
def load(filename):
    """Load wadfile and return WadFile object"""
    try:
        wad = WadFile()
        wad.load(filename)
    except IOError, err:
        raise IOError(err)
    return wad


def fromdirectory(dirname):
    """Create WadFile object from directory of files"""
    if not os.path.exists(dirname):
        raise IOError("Source directory does not exist")
    wad = WadFile()
    for root, dirs, files in os.walk(dirname):
        # Walk the files
        for obj_file in [os.path.join(root, filename) for filename in files]:
            size = os.path.getsize(obj_file)
            # Generate archive name
            archive_file = os.path.relpath(obj_file, dirname)
            obj = WadObject(archive_file, srcname=obj_file, version=1, size=size)
            wad.add(obj)
    return wad
