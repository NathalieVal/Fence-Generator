import math
import maya.cmds as cmds
import maya.api.OpenMaya as om
from PySide6 import QtWidgets, QtCore

# Fence Generator Class
class FenceGenerator:

    def __init__(self):
        # Selected curve:
        self.curve = None

        # Post defaults:
        self.post_spacing = 2
        self.post_width = 0.2
        self.post_height = 2
        self.post_depth = 0.2

        # Rail defaults:
        self.rail_count = 2
        self.rail_spacing = 0.5
        self.rail_height = 0.2
        self.rail_height_offset = 1
        self.rail_depth = 0.2


    # NURBS curve input:

    def select_curve(self, curve):
        self.curve = curve

    def get_curve_func(self):
        selection = om.MSelectionList()
        selection.add(self.curve)

        curve_obj = selection.getDagPath(0)

        return om.MFnNurbsCurve(curve_obj)

    def get_curve_length(self):
        curve_func = self.get_curve_func()
        return curve_func.length()

    # Post positions:
    def get_curve_positions(self):
        curve_func = self.get_curve_func()

        # Retrieve curve length
        curve_length = self.get_curve_length()

        # Retrieve requested spacing
        spacing = self.post_spacing

        # Round if needed 
        interval_count = math.ceil(curve_length / spacing)

        post_positions = []

        # For every post:
        for i in range(interval_count + 1):
            distance = min(i * spacing, curve_length)
            parameter = curve_func.findParamFromLength(distance)

            point = curve_func.getPointAtParam(parameter, om.MSpace.kWorld)

            # Store position information
            post_positions.append((point.x, point.y, point.z))

        # Return information
        return post_positions

    # Curve direction:
    def get_curve_directions(self):
        curve_func = self.get_curve_func()

        curve_length = self.get_curve_length()
        spacing = self.post_spacing

        interval_count = math.ceil(curve_length / spacing)

        post_directions = []

        for i in range(interval_count + 1):
            distance = min(i * spacing, curve_length)
            parameter = curve_func.findParamFromLength(distance)

            direction = curve_func.tangent(parameter, om.MSpace.kWorld)
            direction.normalize()
            post_directions.append((direction.x, direction.y, direction.z))

        # Return information
        return post_directions

    # Rails:
    def get_rail_info(self):
        positions = self.get_curve_positions()

        # Rail info list:
        rail_info = []

        for i in range(len(positions) - 1):
            # Retrieve start and end position
            start = positions[i]
            end = positions[i + 1]

            # Calculate distace and direction between posts
            direction = om.MVector(
                end[0] - start[0], 
                end[1] - start[1], 
                end[2] - start[2],
                )

            rotation = math.degrees(
                math.atan2(direction.z, direction.x))

            distance = direction.length()

            midpooint = (
                (start[0] + end[0]) / 2,
                (start[1] + end[1]) / 2,
                (start[2] + end[2]) / 2,
            )

            rail_info.append((direction, distance, midpooint, rotation))

        return rail_info

    def create_posts(self):
        positions = self.get_curve_positions()
    
        posts = []

        for position in positions:

            post = cmds.polyCube(
                width=self.post_width, 
                height=self.post_height, 
                depth=self.post_depth
                )[0]

            cmds.xform(
                post, 
                worldSpace=True, 
                translation=(
                position[0], 
                (position[1] + (self.post_height / 2)), 
                position[2]
                ))
            
            posts.append(post)

        return posts

    def create_rails(self):
        rail_info = self.get_rail_info()

        rails = []

        for info in rail_info:

            direction, distance, midpoint, rotation = info

            direction_x = direction.x / distance
            direction_z = direction.z / distance
            
            rail_length = distance 

            for i in range(self.rail_count):
                position_y = (
                    midpoint[1] 
                    + self.rail_height_offset 
                    + (( i - (self.rail_count - 1) / 2)
                        * self.rail_spacing))

                rail = cmds.polyCube(
                    width=rail_length, 
                    height=self.rail_height, 
                    depth=self.rail_depth
                    )[0]
                
                cmds.xform(
                    rail, 
                    worldSpace=True, 
                    translation=(midpoint[0], position_y, midpoint[2]),
                    # rotation=(0, -rotation, 0)
                    )

                cmds.xform(
                    rail,
                    worldSpace=True, 
                    rotation=(0, -rotation, 0)
                )

                rails.append(rail)

        return rails

    def generate_fence(self):
        curve_name = self.curve.split("|")[-1]

        fence_name = f"fenceGenerator_{curve_name}"

        if cmds.objExists(fence_name):
            cmds.delete(fence_name)
        
        posts = self.create_posts()
        rails = self.create_rails()

        # Fence group
        fence_parts = posts + rails

        fence_group = cmds.group(
            fence_parts,
            name=fence_name
        )

        return fence_group

class FenceGeneratorGUI(QtWidgets.QDialog):

    # Initialize 
    def __init__(self):

        # Super initialize
        super().__init__()

        self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )

        self.fence_generator = FenceGenerator()

        # Window properties
        self.setWindowTitle("FenceGenerator")

        self.create_layout()
        self.create_connections()
        self.update_settings()

    def create_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self._form_ui()

        self.generate_button = QtWidgets.QPushButton("Generate Fence")
        self.main_layout.addWidget(self.generate_button)

        self.setLayout(self.main_layout)

    def _form_ui(self):
        self.title_label = QtWidgets.QLabel("FenceGenerator")
        self.main_layout.addWidget(self.title_label)

        # Rail SETTINGS:
        self.rail_settings_group = QtWidgets.QGroupBox("Rail Settings")
        self.main_layout.addWidget(self.rail_settings_group)

        self.rail_settings_layout = QtWidgets.QFormLayout()
        self.rail_settings_group.setLayout(self.rail_settings_layout)

        # Rail Count:
        self.rail_count_spinbox = QtWidgets.QSpinBox()    
        self.rail_count_spinbox.setValue(2.0)

        self.rail_settings_layout.addRow(
            "Rail Count",
            self.rail_count_spinbox
        )

        # Rail SPACING:
        self.rail_spacing_spinbox = QtWidgets.QDoubleSpinBox()
        self.rail_spacing_spinbox.setDecimals(1)        
        self.rail_spacing_spinbox.setSingleStep(0.1)
        self.rail_spacing_spinbox.setValue(0.5)

        self.rail_settings_layout.addRow(
            "Rails Spacing",
            self.rail_spacing_spinbox
        )

        # Rail HEIGHT OFFSET:
        self.rail_height_offset_spinbox = QtWidgets.QDoubleSpinBox()
        self.rail_height_offset_spinbox.setDecimals(1)
        self.rail_height_offset_spinbox.setSingleStep(0.1)
        self.rail_height_offset_spinbox.setValue(1)

        self.rail_settings_layout.addRow(
            "Rail Height Offset",
            self.rail_height_offset_spinbox
        )

        # Rail WIDTH:
        self.rail_width_spinbox = QtWidgets.QDoubleSpinBox()
        self.rail_width_spinbox.setDecimals(1)
        self.rail_width_spinbox.setSingleStep(0.1)
        self.rail_width_spinbox.setValue(0.2)

        self.rail_settings_layout.addRow(
            "Rail Width",
            self.rail_width_spinbox
        )

        # Post SETTINGS:
        self.post_settings_group = QtWidgets.QGroupBox("Post Settings")
        self.main_layout.addWidget(self.post_settings_group)

        self.post_settings_layout = QtWidgets.QFormLayout()
        self.post_settings_group.setLayout(self.post_settings_layout)

        # Post SPACING:
        self.post_spacing_spinbox = QtWidgets.QDoubleSpinBox()
        self.post_spacing_spinbox.setDecimals(1)        
        self.post_spacing_spinbox.setSingleStep(0.1)
        self.post_spacing_spinbox.setValue(2)

        self.post_settings_layout.addRow(
            "Post Spacing",
            self.post_spacing_spinbox
        )

        # Post HEIGHT:
        self.post_height_spinbox = QtWidgets.QDoubleSpinBox()
        self.post_height_spinbox.setDecimals(1)   
        self.post_height_spinbox.setSingleStep(0.1)
        self.post_height_spinbox.setValue(2)

        self.post_settings_layout.addRow(
            "Post Height",
            self.post_height_spinbox
        )

        # Post WIDTH:
        self.post_width_spinbox = QtWidgets.QDoubleSpinBox()
        self.post_width_spinbox.setDecimals(1)  
        self.post_width_spinbox.setSingleStep(0.1)
        self.post_width_spinbox.setValue(0.2)

        self.post_settings_layout.addRow(
            "Post Width",
            self.post_width_spinbox
        )

        # Post DEPTH:
        self.post_depth_spinbox = QtWidgets.QDoubleSpinBox()
        self.post_depth_spinbox.setDecimals(1)  
        self.post_depth_spinbox.setSingleStep(0.1)
        self.post_depth_spinbox.setValue(0.2)

        self.post_settings_layout.addRow(
            "Post Depth",
            self.post_depth_spinbox
        )

    def create_connections(self):
        self.generate_button.clicked.connect(self.generate_fence)
        
    def update_settings(self):

        # Rails:
        self.fence_generator.rail_count = self.rail_count_spinbox.value()
        self.fence_generator.rail_spacing = self.rail_spacing_spinbox.value()
        self.fence_generator.rail_height_offset = self.rail_height_offset_spinbox.value()
        self.fence_generator.rail_height = self.rail_width_spinbox.value()
        self.fence_generator.rail_depth = self.rail_width_spinbox.value()

        # Posts:
        self.fence_generator.post_spacing = self.post_spacing_spinbox.value()
        self.fence_generator.post_height = self.post_height_spinbox.value()
        self.fence_generator.post_width = self.post_width_spinbox.value()
        self.fence_generator.post_depth = self.post_depth_spinbox.value()



    @QtCore.Slot()
    def generate_fence(self):
        selected_curve = cmds.ls(selection=True)[0]
        self.fence_generator.select_curve(selected_curve)
        self.update_settings()
        self.fence_generator.generate_fence()

fence_generator_window = None

def show_gui():
    global fence_generator_window

    if fence_generator_window is None:
        fence_generator_window = FenceGeneratorGUI()

    fence_generator_window.show()
    fence_generator_window.raise_()
    fence_generator_window.activateWindow()