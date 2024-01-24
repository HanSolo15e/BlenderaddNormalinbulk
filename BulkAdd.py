import bpy
import os


# Iterate through all materials in the scene
for material in bpy.data.materials:
    # Check if the material has a node tree (using nodes in Shader Editor)
    if material.use_nodes:
        # Get the material node tree
        node_tree = material.node_tree

        # Check if there is an existing image texture node
        image_texture_node = None
        for node in node_tree.nodes:
            if node.type == 'TEX_IMAGE' and "_nrm" not in node.image.name:
                image_texture_node = node
                break

        if image_texture_node:
            # Create a new texture node for the normal map
            normal_map_node = node_tree.nodes.new(type='ShaderNodeTexImage')

            # Create the name of the corresponding normal map based on the albedo texture name
            albedo_texture_name = os.path.splitext(image_texture_node.image.name)[0]  # remove extension
            normal_map_name = albedo_texture_name + "_nrm.png"

            # Check if the normal map image exists in Blender data
            normal_map = bpy.data.images.get(normal_map_name)
            if not normal_map:
                # If normal map doesn't exist, create a new image and assign it
                normal_map = bpy.data.images.new(normal_map_name, width=1, height=1)
                normal_map_node.image = normal_map
            else:
                normal_map_node.image = normal_map

            # Set color space to Non-Color for the normal map texture node
            normal_map_node.image.colorspace_settings.name = 'Non-Color'

            # Create and connect a Normal Map node
            normal_map_shader_node = node_tree.nodes.new(type='ShaderNodeNormalMap')
            material.node_tree.links.new(normal_map_node.outputs['Color'], normal_map_shader_node.inputs['Color'])

            # Find the Principled BSDF shader node
            principled_bsdf_node = None
            for node in node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled_bsdf_node = node
                    break
            
            if principled_bsdf_node:
                # Connect the Normal Map node to the Normal input of the Principled BSDF shader node
                material.node_tree.links.new(normal_map_shader_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
