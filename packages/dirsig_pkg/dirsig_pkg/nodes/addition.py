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
from anatools.lib.node import Node

logger = logging.getLogger(__name__)


class Addition(Node):
    """A simple node that adds two numbers together.
    
    Inputs can be strings, numbers, or links from other nodes.
    String inputs are converted to numbers if possible.
    """

    def exec(self):
        logger.info(f"Executing {self.name}")
        
        # Get inputs
        input_a = self.inputs.get('Input A', [0])[0]
        input_b = self.inputs.get('Input B', [0])[0]
        
        # Convert inputs to numbers
        try:
            # Handle linked node outputs (dictionaries)
            if isinstance(input_a, dict):
                # Try to extract a numeric value from the linked output
                if 'value' in input_a:
                    num_a = float(input_a['value'])
                elif 'result' in input_a:
                    num_a = float(input_a['result'])
                else:
                    # Take the first numeric value found in the dict
                    for key, value in input_a.items():
                        try:
                            num_a = float(value)
                            break
                        except (ValueError, TypeError):
                            continue
                    else:
                        raise ValueError(f"Could not extract numeric value from linked input A: {input_a}")
            else:
                # Direct string or numeric input
                num_a = float(input_a)
                
            if isinstance(input_b, dict):
                # Try to extract a numeric value from the linked output
                if 'value' in input_b:
                    num_b = float(input_b['value'])
                elif 'result' in input_b:
                    num_b = float(input_b['result'])
                else:
                    # Take the first numeric value found in the dict
                    for key, value in input_b.items():
                        try:
                            num_b = float(value)
                            break
                        except (ValueError, TypeError):
                            continue
                    else:
                        raise ValueError(f"Could not extract numeric value from linked input B: {input_b}")
            else:
                # Direct string or numeric input
                num_b = float(input_b)
                
        except (ValueError, TypeError) as e:
            logger.error(f"Could not convert inputs to numbers: A={input_a}, B={input_b}. Error: {e}")
            raise ValueError(f"Addition node requires numeric inputs. Got A={input_a}, B={input_b}")
        
        # Perform addition
        result = num_a + num_b
        
        logger.info(f"Addition: {num_a} + {num_b} = {result}")
        
        # Return the result in a simple format like other anatools nodes
        return {"Sum": result}
