
#---------------------------------------
# Copyright 2019-2025 DADoES, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the root directory in the "LICENSE" file or at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#---------------------------------------

import os
import logging
import subprocess
import json
from lxml.etree import parse
from pathlib import Path
from anatools.lib.ana_object import AnaBaseObject
from anatools.lib.generator import Generator
import anatools.lib.context as ctx
from anatools.lib.package_utils import get_volume_path
from anatools.lib.file_object import FileObject
from anatools.lib.directory_object import DirectoryObject
from dirfm import glist

logger = logging.getLogger(__name__)


def get_file_generator(package, object_class, object_type):
    """
    Helper function that creates a generator from an object
    definition in the package.yml file
    """
    rel_path = ctx.packages[package]["objects"][object_type]["filename"]
    generator = ObjectDirsigGenerator(
        object_class,
        object_type,
        file_path=get_volume_path(package, rel_path),
        config=ctx.packages[package]["objects"][object_type])
    return generator


class ObjectDirsigGenerator(Generator):
    """
    Object Generator
    """
    def __init__(self, object_class, object_type, **kwargs):
        """ Note: kwargs are for the loader """
        super().__init__(children=[], **kwargs)
        self.object_class = object_class
        self.object_type = object_type

    def exec(self, *args, **kwargs):
        """ Return a new instance of the specified object """
        # instantiate the object class
        obj = self.object_class(self.object_type)
        # load the object into the scene
        kwargs.update(**self.kwargs)
        obj.load(**kwargs)
        # return the object
        return obj

    def __repr__(self):
        return json.dumps({
            "class": self.__class__.__name__,
            "id": self.id,
            "object_class": self.object_class.__name__,
            "object_type": self.object_type,
            "kwargs": self.kwargs
        })


class AnaDirsigObject(AnaBaseObject):
    """ A class to represent an Ana DIRSIG object.
    """
    
    def __init__(self, object_type):
        super().__init__(object_type)
        self._size = []
        self.name = "{}_{}".format(self.object_type.replace(" ", ""), self.instance)
        self.match_slope = False
    
    def __repr__(self):
        if self.loaded:
            return f"AnaDirsigObject for {self.object_type}"
    
    def load(self, **kwargs):
        """ Load the object and store it as .root
        """
        if "file_path" in kwargs:
            filePath = Path(kwargs["file_path"])
            glistObject = glist.Object(glist.GlistBaseGeometry(filePath))
        else:
            glistObject = glist.Object(self.object_type)

        self.root = glistObject
        
        self.add_static_instance(name=self.name)

        # save object config if it was provided
        if "config" in kwargs:
            self.config = kwargs.pop("config")
    
    def move(self, trans_vector=[0,0,0], rot_vector=[0,0,0], match_slope=False):
        # Update the translation by a vector (meters) of 3 floats
        # Update the rotation by a vector (degrees) of 3 floats
        assert all([isinstance(x, (float, int)) for x in trans_vector])
        assert all([isinstance(x, (float, int)) for x in rot_vector])
        for objInstance in self.root.get_instances():
            objInstance.set_translation([objInstance.get_translation()[i]+trans_vector[i] for i in range(3)])
            objInstance.set_rotation([objInstance.get_rotation()[i]+rot_vector[i] for i in range(3)])
        
        self.match_slope = match_slope

    def scale(self, scale_factors):
        # Update the scale factors if all this glist object's instances by the input array of 3 floats
        assert all([isinstance(x, (float, int)) for x in scale_factors])
        for objInstance in self.root.get_instances():
            objInstance.set_scale([objInstance.get_scale()[i]*scale_factors[i] for i in range(3)])
        
        #Collect metadata
        self.modifiers.append({
            "Scale_N": {
                "Scale Factors": scale_factors
            }
        })
    
    def get_size(self):
        # Return the dimensions of the raw OBJ
        if self._size == []:
            #Parse glist file
            glist_fPath = self.root.get_base_geometry()[0]._glist
            
            glistTree = parse(str(glist_fPath))
            objFilename = [e for e in glistTree.getroot().iter('filename')][0].text
            objFilePath = glist_fPath.parents[0] / objFilename
            
            result = subprocess.run(
                ["object_tool", "--geometry", f"--input_filename={objFilePath}", "--input_format=obj"],
                capture_output=True,
                text=True,
                env=os.environ,
            )
            
            sizeLine = [l for l in result.stdout.splitlines() if "Size = " in l][0]
            for value in sizeLine.split():
                try:
                    self._size.append(float(value))
                except ValueError:
                    pass
            
        return self._size

    def add_static_instance(self, name=None, anchor=None):
        # Add a DIRSIG Static Instance to this object
        staticInstance = glist.StaticInstance(
            name=name,
            anchor=anchor,
        )
        self.root.add_instance(staticInstance)

    def set_dynamic_instance(self, motion, name=None):
        # Set this object to have a DIRSIG Dynamic Instance
        if name == None:
            name = self.name
        self.root._instance = []
        dynamicInstance = glist.DynamicInstance(
            name=self.name,
            motion=motion
        )
        self.root.add_instance(dynamicInstance)
    
    def set_binfile_instance(self, locations_filepath, name=None, anchor_name=None):
        # Set this object to have a DIRSIG Static Instance Binary File
        if name == None:
            name = self.name
        self.root._instance = []
        sib = glist.StaticInstanceBinaryFile(locations_filepath, name=name, anchor=anchor_name)
        self.root.add_instance(sib)


def filename_to_generator(filename, object_class):
    # create an object generator that uses filename as its source
    _, ext = os.path.splitext(filename)
    if ext != ".glist":
        logger.info(f"File type of '{ext}' not supported")
        return
    object_type = 'GlistBundle'
    
    wrapped_generator = ObjectDirsigGenerator(
        object_class,
        object_type,
        file_path=filename)
    return wrapped_generator


def file_to_objgen(generators, object_class):
    """
    Process a mixed list of generators, FileObjects, and DirectoryObjects
    For any FileObject in the list, wrap it in an ObjectGenerator. The object type returned by the
    generator will be 'object_class'. The loader method will be replaced with one appropriate
    to the file type specified in the FileObject (currently only Blender is supported).
    For any DirectoryObject in the list, loop through all files in the directory (excluding
    subdirectories and files ending in .anameta) and make them object generators as above.
    """

    # return generators
    wrapped_generators = []
    for generator in generators:
        if isinstance(generator, FileObject):
            gen = filename_to_generator(generator.filename, object_class)
            if gen is not None:
                wrapped_generators.append(filename_to_generator(generator.filename, object_class))
        elif isinstance(generator, DirectoryObject):
            files = generator.get_files()
            for filename in files:
                gen = filename_to_generator(filename, object_class)
                if gen is not None:
                    wrapped_generators.append(filename_to_generator(filename, object_class))
        else:
            wrapped_generators.append(generator)

    return wrapped_generators