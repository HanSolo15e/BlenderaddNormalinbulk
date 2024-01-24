import bpy
import os

# Set the render engine to CYCLES


def create_normal_map_node(material, albedo_texture_node):
    # Create a new texture node for the normal map
    normal_map_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')

    # Create the name of the corresponding normal map based on the albedo texture name
    albedo_texture_name, ext = os.path.splitext(albedo_texture_node.image.name)  # separate filename and extension
    normal_map_name = albedo_texture_name.split('.')[0] + "_nrm.png"  # remove additional suffixes

    # Check if the normal map image exists in Blender data
    normal_map = bpy.data.images.get(normal_map_name)
    if not normal_map:
        # If normal map doesn't exist, create a new image and assign it
        normal_map = bpy.data.images.new(normal_map_name, width=1, height=1)
    normal_map_node.image = normal_map

    # Check and correct the file extension if needed
    if not normal_map_name.lower().endswith('.png'):
        normal_map_name += '.png'

    # Set color space to Non-Color for the normal map texture node
    normal_map_node.image.colorspace_settings.name = 'Non-Color'

    return normal_map_node

# Iterate through all materials in the scene
for material in bpy.data.materials:
    # Check if the material has a node tree (using nodes in Shader Editor)
    if material.use_nodes:
        # Get the material node tree
        node_tree = material.node_tree

        # Check if there is an existing image texture node
        image_texture_node = next((node for node in node_tree.nodes if node.type == 'TEX_IMAGE' and "_nrm" not in node.image.name), None)

        if image_texture_node:
            # Create and connect a Normal Map node
            normal_map_node = create_normal_map_node(material, image_texture_node)
            normal_map_shader_node = node_tree.nodes.new(type='ShaderNodeNormalMap')
            material.node_tree.links.new(normal_map_node.outputs['Color'], normal_map_shader_node.inputs['Color'])

            # Find the Principled BSDF shader node
            principled_bsdf_node = next((node for node in node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)

            if principled_bsdf_node:
                # Connect the Normal Map node to the Normal input of the Principled BSDF shader node
                material.node_tree.links.new(normal_map_shader_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
