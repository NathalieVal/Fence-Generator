# Will be using class exercise as reference.

# import
import math
import maya.api.OpenMaya as om

# Fence Generator Class
class FenceGenerator:

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

    def get_curve_length(self):
        # Selection list & adding selected curve
        selection = om.MSelectionList()
        selection.add(self.curve)

        curve_obj = selection.getDagPath(0)
        curve_func = om.MFnNurbsCurve(curve_obj)

        return curve_func.length()


            # -- How many posts an fit within this length based on the spacing requested? (I just realized math will be required for this haha)
                # Retrieve selected curve
                # Calculate total length        
                # Return information

            # Post positions:
    def get_curve_positions(self):

            # -- For now, will be assuming that the user wants even spacing.
            # -- Fence MUST end with a post (pattern assignment already coming in to use)
        selection = om.MSelectionList()
        selection.add(self.curve)

        curve_obj = selection.getDagPath(0)
        curve_func = om.MFnNurbsCurve(curve_obj)


                # Retrieve curve length
        curve_len = self.get_curve_length()

                # Retrieve requested spacing
        spacing = self.post_spacing
        
                # Calculate how many posts (intervals) fit within length
                    # Round if needed ?
        interval_count = math.ceil(curve_len / spacing)

        post_positions = []

                # For every post:
        for i in range(interval_count + 1):
            distance = min(i * spacing, curve_len)
            parameter = curve_func.findParamFromLength(distance)

            point = curve_func.getPointAtParam(parameter, om.MSpace.kWorld)

                    # Store position information
            post_positions.append((point.x, point.y, point.z))

                # Return information
        return post_positions

            # Curve direction:
            # -- Posts & rails must follow curve direction.
                # Retrieve post positions
                # For every post:
                    # Calculate tangent direction of curve (debating whether to do perpendicular direction instead depending on what the "front" of the post is)
                    # Store direction
                # Return information

            # Rails:
            # -- Almost forgot these
                # Retrieve post posiitons
                # For each pair of post
                    # Retrieve start and end position
                    # Calculate distace and direction between posts (may make these seperate functions like the post posiitons and directions)

            # Put it all together and generate (gulp)

# GUI Class
    # GUI 
    # Display