# Will be using class exercise as reference.

# import
import math
import maya.api.OpenMaya as om

# Fence Generator Class
class FenceGenerator:

    def __init__(self):
        self.curve = None
        self.post_spacing = 2
        
        self.post_width = 0.2
        self.post_height = 2
        self.post_depth = 0.2

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
            # -- Almost forgot these
                # Retrieve post posiitons
                # For each pair of post
                    # Retrieve start and end position
                    # Calculate distace and direction between posts (may make these seperate functions like the post posiitons and directions)

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
                position[1], 
                position[2]
                ))
            
        # 3.3 add cobe to post list
            posts.append(post)

        # 4. Return post list
        return posts

# GUI Class
    # GUI 
    # Display