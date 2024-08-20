import bpy
import os

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
output_folder = os.path.join(desktop_path, "cool_mats")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

default_normal_value = "[0.501961 0.501961 1.000000 0.000000]" # we are using a value because the default texture has a pattern on it
default_roughness_value = "[0.501961 0.501961 0.501961 0.000000]" # we are using a value because the default texture has a pattern on it
default_metalness = "default/default_metal.tga"
default_ao = "default/default_ao.tga"
default_height = "default/default_height.tga"
default_mask = "default/default_mask.tga"

for material in bpy.data.materials:
    # skip materials that don't use nodes or don't have a Principled BSDF
    if not material.use_nodes:
        continue

    # find the Principled BSDF node
    principled_bsdf = None
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled_bsdf = node
            break

    if not principled_bsdf:
        continue

    # find the image connected to the base color input of the Principled BSDF
    base_color_image = None
    base_color_input = principled_bsdf.inputs['Base Color']
    if base_color_input.is_linked:
        link = base_color_input.links[0]
        if link.from_node.type == 'TEX_IMAGE':
            base_color_image = link.from_node.image

    # if no image is connected, skip this material
    if not base_color_image:
        continue

    # extract the image file name
    image_name = os.path.basename(base_color_image.filepath)

    # get alpha image from color
    # this is a specific use case where the node is using the alpha channel of the color image
    # and you would extract that alpha channel into a new image with another script adding "_alpha" to its name
    # if you dont want to use this just uncomment alpha_image_name below and comment out the one above
    base_name, _ = os.path.splitext(image_name)
    alpha_image_name = f"{base_name}_alpha.jpg"
    # alpha_image_name = "default/default_trans.tga"

    # find other connected textures or use default ones
    def get_texture_name(texture_name, default):
        """Returns the file path of the connected texture or a default if not connected."""
        texture_input = principled_bsdf.inputs[texture_name]
        if texture_input.is_linked:
            link = texture_input.links[0]
            if link.from_node.type == 'TEX_IMAGE':
                return os.path.basename(link.from_node.image.filepath)
        return default

    normal_texture = get_texture_name('Normal', default_normal_value)
    roughness_texture = get_texture_name('Roughness', default_roughness_value)
    metalness_texture = get_texture_name('Metallic', default_metalness)

    # make .vmat file
    vmat_content = f'''Layer0
{{
    shader "csgo_environment.vfx"

    //---- Translucent ----
    F_ALPHA_TEST 1

    //---- Color ----
    g_flModelTintAmount "1.000"
    g_nScaleTexCoordUByModelScaleAxis "0" // None
    g_nScaleTexCoordVByModelScaleAxis "0" // None
    g_vColorTint "[1.000000 1.000000 1.000000 0.000000]"

    //---- Fog ----
    g_bFogEnabled "1"

    //---- Material1 ----
    g_flAlphaTestReference1 "0.010"
    g_flAntiAliasedEdgeStrength1 "0.000"
    g_flTexCoordRotation1 "0.000"
    g_vTexCoordCenter1 "[0.500 0.500]"
    g_vTexCoordOffset1 "[0.000 0.000]"
    g_vTexCoordScale1 "[1.000 1.000]"
    TextureAmbientOcclusion1 "materials/{default_ao}"
    TextureColor1 "materials/{image_name}"
    TextureHeight1 "materials/{default_height}"
    TextureMetalness1 "materials/{metalness_texture}"
    TextureNormal1 "{normal_texture}"
    TextureRoughness1 "{roughness_texture}"
    TextureTintMask1 "materials/{default_mask}"
    TextureTranslucency1 "materials/{alpha_image_name}"

    //---- Texture Address Mode ----
    g_nTextureAddressModeU "0" // Wrap
    g_nTextureAddressModeV "0" // Wrap

    //---- Translucent ----
    g_flAlphaTestReference "0.500"
    g_flAntiAliasedEdgeStrength "1.000"

    VariableState
    {{
        "Color"
        {{
        }}
        "Fog"
        {{
        }}
        "Material1"
        {{
            "Color" 0
            "Tint Mask" 0
            "Translucent" 0
            "Lighting" 0
            "Height" 0
            "Texture Transform" 1
        }}
        "Texture Address Mode"
        {{
        }}
        "Translucent"
        {{
        }}
    }}
}}
'''

    vmat_file_path = os.path.join(output_folder, material.name + ".vmat")

    with open(vmat_file_path, 'w') as vmat_file:
        vmat_file.write(vmat_content)
