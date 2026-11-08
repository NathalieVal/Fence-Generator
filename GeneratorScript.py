import sys
import importlib
import maya.cmds as cmds

script_path = r"C:\Users\Natha\OneDrive\2020\Documents\University\F26\Scripting\Fence-Generator"
sys.path.append(script_path)

import FenceGenerator
importlib.reload(FenceGenerator)

selected = cmds.ls(selection=True, long=True)

shapes = cmds.listRelatives(selected[0], shapes=True, fullPath=True)

curve_shape = cmds.ls(shapes, type="nurbsCurve")[0]

generator = FenceGenerator.FenceGenerator()
generator.select_curve(curve_shape)
length = generator.get_curve_length()

generator.post_spacing = 2.0
positions = generator.get_curve_positions()
directions = generator.get_curve_directions()

# Printing tests
print(f"Length: {length}")
print(f"Number of posts: {len(positions)}")
print(f"Post positions:")
for i, position in enumerate(positions):
    print(i, position)

print(f"Number of directions:{len(directions)}")
print(f"Post directions:")
for i, direction in enumerate(directions):
    print(i, direction)