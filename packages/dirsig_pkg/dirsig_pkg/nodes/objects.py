
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

import logging
import anatools.lib.context as ctx
from anatools.lib.node import Node
from dirsig_pkg.lib.object import AnaDirsigObject, get_file_generator

logger = logging.getLogger(__name__)

class BenchNode(Node):
        """ A class to represent the Bench node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Bench"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Bench Object': glistGenerator}


class ConcreteBarrierNode(Node):
        """ A class to represent the Concrete Barrier node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Concrete Barrier"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Concrete Barrier Object': glistGenerator}


class ConcreteParkingBumperNode(Node):
        """ A class to represent the Concrete Parking Bumper node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Concrete Parking Bumper"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Concrete Parking Bumper Object': glistGenerator}


class DrainagePipeNode(Node):
        """ A class to represent the Drainage Pipe node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                
                objectType = self.inputs['Type'][0]
                
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Drainage Pipe Object': glistGenerator}


class ElectricalTransformerNode(Node):
        """ A class to represent the Electrical Transformer node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Electrical Transformer"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Electrical Transformer Object': glistGenerator}


class FirehydrantNode(Node):
        """ A class to represent the Firehydrant node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Firehydrant"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Firehydrant Object': glistGenerator}


class FuelTankNode(Node):
        """ A class to represent the Fuel Tank node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Fuel Tank"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Fuel Tank Object': glistGenerator}


class HobbleBushNode(Node):
        """ A class to represent the Hobble Bush node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Hobble Bush"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Hobble Bush Object': glistGenerator}


class House1Node(Node):
        """ A class to represent the House1 node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "House1"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'House Object': glistGenerator}


class House2Node(Node):
        """ A class to represent the House2 node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "House2"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'House Object': glistGenerator}


class LadderNode(Node):
        """ A class to represent the Ladder node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Ladder"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Ladder Object': glistGenerator}


class MacbethNode(Node):
        """ A class to represent the Macbeth node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Macbeth"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Color Chart Object': glistGenerator}


class PicnicTableNode(Node):
        """ A class to represent the Picnic Table node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Picnic Table"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Picnic Table Object': glistGenerator}


class ShippingContainerNode(Node):
        """ A class to represent the Shipping Container node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Shipping Container"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Shipping Container Object': glistGenerator}


class ShippingContainerNode(Node):
        """ A class to represent the Shipping Container node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Shipping Container"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Shipping Container Object': glistGenerator}


class ShrubsNode(Node):
        """ A class to represent the Shrubs node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"

                objectType = self.inputs['Shrub Choice'][0]
                if objectType == 'any':
                        objectType = ctx.random.choice(['Brush1', 'Brush2', 'Brush3', 'Brush4', 'Brush5'])
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Shrubs Object': glistGenerator}


class SteelDrumNode(Node):
        """ A class to represent the Steel Drum node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Steel Drum"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Steel Drum Object': glistGenerator}


class SteelGrateNode(Node):
        """ A class to represent the Steel Grate node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Steel Grate"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Steel Grate Object': glistGenerator}


class SteelWorkTableNode(Node):
        """ A class to represent the Steel Work Table node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Steel Work Table"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Steel Work Table Object': glistGenerator}


class SteppingStoneNode(Node):
        """ A class to represent the Stepping Stone node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Stepping Stone"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Stepping Stone Object': glistGenerator}


class StreetLightsNode(Node):
        """ A class to represent the Street Lights node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                objectType = self.inputs['Type'][0]
                if objectType == 'any':
                        objectType = ctx.random.choice(['3m_1bulb', '4m_2bulb', '15m_3bulb'])
                
                packageName = "dirsig_pkg"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Street Lights Object': glistGenerator}


class TireAndWheelNode(Node):
        """ A class to represent the Tire And Wheel node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Tire And Wheel"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Tire And Wheel Object': glistGenerator}


class TrafficConeNode(Node):
        """ A class to represent the Traffic Cone node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Traffic Cone"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Traffic Cone Object': glistGenerator}


class TreesNode(Node):
        """ A class to represent the Trees node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = self.inputs['Tree Choice'][0]
                if objectType == 'any':
                        objectType = ctx.random.choice(['Dogwood', 'Red Maple', 'Silver Maple'])
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Trees Object': glistGenerator}

class TribarNode(Node):
        """ A class to represent the Tribar node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Tribar"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Tri-bar Object': glistGenerator}


class VehiclesNode(Node):
        """ A class to represent the Vehicles node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Vehicles"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Vehicles Object': glistGenerator}


class VehiclesNode(Node):
        """ A class to represent the Vehicles node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Vehicles"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Vehicles Object': glistGenerator}


class VehiclesNode(Node):
        """ A class to represent the Vehicles node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Vehicles"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Vehicles Object': glistGenerator}


class VehiclesNode(Node):
        """ A class to represent the Vehicles node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Vehicles"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Vehicles Object': glistGenerator}


class WasteBinsNode(Node):
        """ A class to represent the Waste Bins node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Waste Bins"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Waste Bins Object': glistGenerator}


class WasteBinsNode(Node):
        """ A class to represent the Waste Bins node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Waste Bins"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Waste Bins Object': glistGenerator}


class WasteBinsNode(Node):
        """ A class to represent the Waste Bins node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Waste Bins"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Waste Bins Object': glistGenerator}


class WasteBinsNode(Node):
        """ A class to represent the Waste Bins node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Waste Bins"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Waste Bins Object': glistGenerator}


class WoodPalletNode(Node):
        """ A class to represent the Wood Pallet node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "Wood Pallet"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'Wood Pallet Object': glistGenerator}
  
  
class B737Node(Node):
        """ A class to represent the 737 node
        """
        def exec(self):
                logger.info("Executing {}".format(self.name))
                packageName = "dirsig_pkg"
                objectType = "B737"
                glistGenerator = get_file_generator(packageName, AnaDirsigObject, objectType)
                return {'B737 Object': glistGenerator}
