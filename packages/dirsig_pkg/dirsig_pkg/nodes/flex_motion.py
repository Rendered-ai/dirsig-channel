
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

import ast
import logging
from anatools.lib.node import Node

import dirfm.flexible_motion as fm

logger = logging.getLogger(__name__)

class TimeEntry(Node):
    """ TimeEntry node """

    def exec(self):
        logger.info("Executing {}".format(self.name))

        time = float(self.inputs["Time"][0])
        entry = ast.literal_eval(self.inputs["Entry"][0])

        return {"Entry": (time,entry)} 

class WaypointLocationEngine(Node):
    """ """
    def exec(self):
        logger.info("Executing {}".format(self.name))
        # order of entries doesn't matter as they are sorted inside WaypointsLocationEngine
        le = fm.WaypointsLocationEngine(self.inputs["Frame"][0])
        for entry in self.inputs["Position(s)"]:
            le.add_point(entry[0],entry[1])

        # This engine requires at least two inputs so if one is provided the add a copy 100 seconds later
        if len(self.inputs["Position(s)"])==1:
            entry = self.inputs["Position(s)"][0]
            le.add_point(entry[0]+100,entry[1])

        return {"LocationEngine": le}

class StraightLineLocationEngine(Node):
    """ """
    def exec(self):
        logger.info("Executing {}".format(self.name))
        # order of entries doesn't matter as they are sorted inside WaypointsLocationEngine
        pos = ast.literal_eval(self.inputs["Position"][0])
        heading =float(self.inputs['Heading'][0])
        velocity=float(self.inputs['Speed'][0])
        frame = self.inputs["Frame"][0]
        if frame=="scene":
           p = fm.ENUFrame(pos[0],pos[1],pos[2])
        elif frame=="ecef":
           p = fm.ECEFFrame(pos[0],pos[1],pos[2])
        elif frame=="geodetic":
           p = fm.GeodeticFrame(pos[0],pos[1],pos[2])

        le = fm.StraightLightLocationEngine(p,heading,velocity)

        return {"LocationEngine": le}

class FixedLocationEngine(Node):
    """ """
    def exec(self):
        logger.info("Executing {}".format(self.name))
        # order of entries doesn't matter as they are sorted inside WaypointsLocationEngine
        pos = ast.literal_eval(self.inputs["Position"][0])
        frame = self.inputs["Frame"][0]
        if frame=="scene":
           p = fm.ENUFrame(pos[0],pos[1],pos[2])
        elif frame=="ecef":
           p = fm.ECEFFrame(pos[0],pos[1],pos[2])
        elif frame=="geodetic":
           p = fm.GeodeticFrame(pos[0],pos[1],pos[2])
        le = fm.FixedLocationEngine(p)

        return {"LocationEngine": le}

class VelocityOrientationEngine(Node):
    """ """
    def exec(self):
        logger.info("Executing {}".format(self.name))

        oe = fm.VelocityOrientationEngine(frame=self.inputs["Frame"][0])

        return {"OrientationEngine": oe}

class EulerOrientationEngine(Node):
    """ """
    def exec(self):
        logger.info("Executing {}".format(self.name))

        rot_order = self.inputs["Rotation Order"][0]
        frame = self.inputs["Frame"][0]

        # order of entries doesn't matter as they are sorted inside WaypointsLocationEngine
        oe = fm.EulerOrientationEngine(order=rot_order,frame=frame)
        for entry in self.inputs["Orientation(s)"]:
            oe.add_entry(entry[0],entry[1][0],entry[1][1],entry[1][2])

        # This engine requires at least two inputs so if one is provided the add a copy 100 seconds later
        if len(self.inputs["Orientation(s)"])==1:
            entry = self.inputs["Orientation(s)"][0]
            oe.add_entry(entry[0]+100,entry[1][0],entry[1][1],entry[1][2])

        return {"OrientationEngine": oe}

class LookAtOrientationEngine(Node):
    """ """
    def exec(self):
        logger.info("Executing {}".format(self.name))
        # order of entries doesn't matter as they are sorted inside WaypointsLocationEngine
        up = ast.literal_eval(self.inputs["Up Vector"][0])
        oe = fm.LookAtOrientationEngine(self.inputs["LocationEngine"][0],up=up)

        return {"OrientationEngine": oe}

# BUG: Velocity will cause an error if task start and stop are both 0 as the object never moves so it never gets a velocity
class VelocityOrientationEngine(Node):
    """ """
    def exec(self):
        logger.info("Executing {}".format(self.name))
        oe = fm.VelocityOrientationEngine()
        return {"OrientationEngine": oe}

#TODO: FlexMotion could be used to place/move objects in the scene as well
class FlexMotion(Node):
    """ Flexible Motion node """

    def exec(self):
        logger.info("Executing {}".format(self.name))

        if len(self.inputs["LocationEngine"])==1:
            le = self.inputs["LocationEngine"][0]
        else:
            le = fm.FixedLocationEngine(fm.ENUFrame(0,0,0))

        if len(self.inputs["OrientationEngine"])==1:
            oe = self.inputs["OrientationEngine"][0]
        else:
            oe = fm.LookAtOrientationEngine(
                fm.FixedLocationEngine(
                    fm.ENUFrame(0,0.1,0)),up=[0,0,1])
        motion = fm.FlexMotion(le,oe)

        return {"Motion": motion}
