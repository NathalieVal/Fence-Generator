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

        # Chain defaults:
        self.diamond_size = 0.2
        self.diamond_height = 0.2
        self.diamong_width = 0.2

    # NURBS curve input:

    def select_curve(self, curve):
        self.curve = curve

    # 1. when user clicks on chosen NURBS curve, and clicks "generate fence" program retrieves curve information    
    # 2. program checks if curve works for program function
    # 3. If yes, input can be used to generate fence.
    # 3.5 IF NOT, display warning.

    # Generate fence:
    # Curve info needed:
    # Curve length

    def get_curve_func(self):
        selection = om.MSelectionList()
        selection.add(self.curve)

        curve_obj = selection.getDagPath(0)

        return om.MFnNurbsCurve(curve_obj)

    def get_curve_length(self):
        curve_func = self.get_curve_func()
        return curve_func.length()

    # -- How many posts an fit within this length based on the spacing requested? (I just realized math will be required for this haha)
    # Retrieve selected curve
    # Calculate total length        
    # Return information

    # Post positions:
    def get_curve_positions(self):

        # -- For now, will be assuming that the user wants even spacing.
        # -- Fence MUST end with a post (pattern assignment already coming in to use)
        curve_func = self.get_curve_func()

        # Retrieve curve length
        curve_length = self.get_curve_length()

        # Retrieve requested spacing
        spacing = self.post_spacing
        
        # Calculate how many posts (intervals) fit within length
        # Round if needed ?
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
            # -- Posts & rails must follow curve direction.
            # Retrieve post positions
        post_directions = []

                # For every post:
                # Calculate tangent direction of curve (debating whether to do perpendicular direction instead depending on what the "front" of the post is)
                # Store direction
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

        rail_info = []

        # For each pair of post
        for i in range(len(positions) - 1):
            # Retrieve start and end position
            start = positions[i]
            end = positions[i + 1]

            # Calculate distace and direction between posts (may make these seperate functions like the post posiitons and directions)
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
            # Put it all together and generate (gulp)

    def create_posts(self):
        # 1. Get post positions
        positions = self.get_curve_positions()
    
        # 2. Empty list for posts
        posts = []

        # 3. For each positions: 
        for position in positions:

        # 3.1 Create geometry with height, width, depth.
            post = cmds.polyCube(
                width=self.post_width, 
                height=self.post_height, 
                depth=self.post_depth
                )[0]

        # 3.2 Translate geometry into position
            cmds.xform(
                post, 
                worldSpace=True, 
                translation=(
                position[0], 
                (position[1] + (self.post_height / 2)), 
                position[2]
                ))
            
        # 3.3 add cobe to post list
            posts.append(post)

        # 4. Return post list
        return posts

    def create_rails(self):
        # 1. Get rail information
        rail_info = self.get_rail_info()

        # 2. Empty list for rails
        rails = []

        # 3. For each rail:
        for info in rail_info:

            direction, distance, midpoint, rotation = info

            # 3.1 Calculate direction
            direction_x = direction.x / distance
            direction_z = direction.z / distance

            # 3.2 Calculate length
            
            rail_length = distance 

            # Create rails based on rail_count
            for i in range(self.rail_count):
                position_y = (
                    midpoint[1] 
                    + self.rail_height_offset 
                    + (( i - (self.rail_count - 1) / 2)
                        * self.rail_spacing))

                # 3.3 Actually create the polyCube
                rail = cmds.polyCube(
                    width=rail_length, 
                    height=self.rail_height, 
                    depth=self.rail_depth
                    )[0]
                
                # Calculate vertical position
                # position_y = midpoint[1] + self.rail_height_offset

                # Translate geomtry into position
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

    def create_test_diamond(self):
        mesh_width = 4.0
        mesh_height = 2.0

        diamond_count = math.ceil(mesh_width / self.diamond_size)
        row_count = math.ceil(mesh_height / (self.diamond_size / 2))

        for row in range(row_count):
            offset_y = row * (self.diamond_size / 2)
            row_offset_x = (row % 2) * (self.diamond_size / 2)

            for i in range(diamond_count):
                offset_x = (i * self.diamond_size) + row_offset_x

                top = (offset_x, offset_y + self.diamond_size / 2, 0)
                bottom = (offset_x, offset_y - self.diamond_size / 2, 0)
                right = (offset_x + self.diamond_size / 2, offset_y, 0)
                left = (offset_x - self.diamond_size / 2, offset_y, 0)

                cmds.curve(
                    degree=1,
                    point=[top, right, bottom]
                )

                cmds.curve(
                    degree=1,
                    point=[bottom, left, top]
                )

    def generate_fence(self):
            self.create_posts()
            self.create_rails()

class FenceGeneratorGUI(QtWidgets.QDialog):

    # Initialize 
    def __init__(self):

        # Super initialize
        super().__init__()

        self.fence_generator = FenceGenerator()

        # Window properties
        self.setWindowTitle("FenceGenerator")

        self.create_layout()
        self.update_fence_style()
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
        self.fence_style_combobox = QtWidgets.QComboBox()
        self.fence_style_combobox.addItems([
            "Post & Rail",
            "Chain Link"
        ])

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.fence_style_combobox)

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

    def update_fence_style(self):
        fence_style = self.fence_style_combobox.currentText()

        if fence_style == "Post & Rail":
            self.post_settings_group.show()
            self.rail_settings_group.show()

        else:
            self.post_settings_group.hide()
            self.rail_settings_group.hide()

    def create_connections(self):
        self.generate_button.clicked.connect(self.generate_fence)
        self.fence_style_combobox.currentIndexChanged.connect(
            self.update_fence_style
        )
        
    def update_settings(self):

        # Rails:
        self.fence_generator.rail_count = self.rail_count_spinbox.value()
        self.fence_generator.rail_spacing = self.rail_spacing_spinbox.value()
        self.fence_generator.rail_height_offset = self.rail_height_offset_spinbox.value()
        self.fence_generator.rail_width_spinbox = self.rail_width_spinbox.value()

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

    fence_generator_window = FenceGeneratorGUI()
    fence_generator_window.show()