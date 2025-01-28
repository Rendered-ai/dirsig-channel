
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

import pdb
from pathlib import Path
import lxml.etree as et
from dirfm import glist
import anatools.lib.context as ctx

class Cluster:
    """ A cluster of objects """
    next_instance = 0

    def __init__(self, cluster_type, locations):
        self.instance = Cluster.next_instance
        self.locations_filepath =  Path("/tmp") / f"parcel{self.instance}.bin"
        Cluster.next_instance += 1
        self.type = cluster_type
        
        #Write binary file of locations
        sib = glist.StaticInstanceBinary(fname=str(self.locations_filepath))
        for loc in locations:
            sib.add_instance(translation=loc, rotation=[0, 0, ctx.random.random() * 360])
        root = et.Element("geometrylist", enabled="true")
        sib.write(root, {"geometry": Path.cwd()})
        