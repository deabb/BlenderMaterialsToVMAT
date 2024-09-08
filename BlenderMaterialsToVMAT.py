bl_info = {
    "name": "Convert Materials to Vmat",
    "blender": (2, 80, 0),
    "category": "Material",
    "description": "Converts Blender materials to VMAT files.",
    "author": "Deana @dea_bb",
    "version": (1, 0),
    "social_links": {
        "twitter": "https://x.com/dea_bb",
    }
}

import bpy
import os
import webbrowser

bpy.types.Scene.only_selected_materials = bpy.props.BoolProperty(
    name="Only Convert Selected Objects Materials",
    description="If checked, only convert materials of selected objects",
    default=False
)

bpy.types.Scene.output_folder_path = bpy.props.StringProperty(
    name="Output Folder",
    description="Folder to save VMAT files",
    default=os.path.join(os.path.expanduser("~"), "Desktop", "cool_mats"),
    subtype='DIR_PATH'
)

def convert_materials_to_vmat(only_selected=False, output_folder=None):
    if not output_folder:
        output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "cool_mats")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    default_normal_value = "[0.501961 0.501961 1.000000 0.000000]"
    default_roughness_value = "[0.501961 0.501961 0.501961 0.000000]"
    default_metalness = "default/default_metal.tga"
    default_ao = "default/default_ao.tga"
    default_height = "default/default_height.tga"
    default_mask = "default/default_mask.tga"
    default_alpha = "default/default_trans.tga"
    default_color = "default/default_metal.tga"

    def get_image_for_input(input_name, default_image, principled_bsdf):
        input_node = principled_bsdf.inputs.get(input_name)
        if input_node and input_node.is_linked:
            link = input_node.links[0]
            if link.from_node.type == 'TEX_IMAGE':
                texture_path = "materials/" + os.path.basename(link.from_node.image.filepath)
                print(f"Found {input_name} texture: {texture_path}")
                return texture_path
        print(f"Using default {input_name} texture: {default_image}")
        return default_image

    def convert_material(material):
        if not material.use_nodes:
            return

        principled_bsdf = None
        for node in material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled_bsdf = node
                break

        if not principled_bsdf:
            return

        base_color_image = get_image_for_input('Base Color', "materials/" + os.path.basename(default_color), principled_bsdf)
        normal_texture = get_image_for_input('Normal', default_normal_value, principled_bsdf)
        roughness_texture = get_image_for_input('Roughness', default_roughness_value, principled_bsdf)
        metalness_texture = get_image_for_input('Metallic', "materials/" + os.path.basename(default_metalness), principled_bsdf)
        ao_texture = get_image_for_input('Ambient Occlusion', "materials/" + os.path.basename(default_ao), principled_bsdf)
        alpha_image_name = get_image_for_input('Alpha', "materials/" + os.path.basename(default_alpha), principled_bsdf)
        
        height_texture = "materials/" + os.path.basename(default_height)
        mask_texture = "materials/" + os.path.basename(default_mask)

        print(f"Converting material: {material.name}")
        print(f"Base Color: {base_color_image}")
        print(f"Normal: {normal_texture}")
        print(f"Roughness: {roughness_texture}")
        print(f"Metalness: {metalness_texture}")
        print(f"Ambient Occlusion: {ao_texture}")
        print(f"Alpha: {alpha_image_name}")
        print(f"Height: {height_texture}")
        print(f"Mask: {mask_texture}")

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
    TextureAmbientOcclusion1 "{ao_texture}"
    TextureColor1 "{base_color_image}"
    TextureHeight1 "{height_texture}"
    TextureMetalness1 "{metalness_texture}"
    TextureNormal1 "{normal_texture}"
    TextureRoughness1 "{roughness_texture}"
    TextureTintMask1 "{mask_texture}"
    TextureTranslucency1 "{alpha_image_name}"

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

        print(f"Written VMAT file: {vmat_file_path}")

    if only_selected:
        selected_objects = bpy.context.selected_objects
        materials_to_convert = set()
        for obj in selected_objects:
            if obj.type == 'MESH':
                for mat_slot in obj.material_slots:
                    if mat_slot.material:
                        materials_to_convert.add(mat_slot.material)
    else:
        materials_to_convert = bpy.data.materials

    for material in materials_to_convert:
        convert_material(material)

class ConvertMaterialsToVmatOperator(bpy.types.Operator):
    """CONVERT MATERIALS TO VMATS"""
    bl_idname = "material.convert_materials_to_vmat"
    bl_label = "CONVERT MATERIALS TO VMATS"

    def execute(self, context):
        only_selected = context.scene.only_selected_materials
        output_folder = context.scene.output_folder_path
        convert_materials_to_vmat(only_selected, output_folder)
        self.report({'INFO'}, "MATERIALS CONVERTED TO VMATS!")
        return {'FINISHED'}

class OpenLinkOperator(bpy.types.Operator):
    """x.com/dea_bb"""
    bl_idname = "wm.open_link"
    bl_label = "x.com/dea_bb"

    def execute(self, context):
        url = "https://www.x.com/dea_bb"
        webbrowser.open(url)
        self.report({'INFO'}, f"Opened link: {url}")
        return {'FINISHED'}

class ConvertMaterialsToVmatPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "DEANAS VMAT CONVERTER"
    bl_idname = "MATERIAL_PT_convert_vmat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DEANAS VMAT CONVERTER'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "only_selected_materials")
        layout.prop(scene, "output_folder_path")
        layout.operator("material.convert_materials_to_vmat")
        layout.operator("wm.open_link")

def register():
    bpy.utils.register_class(ConvertMaterialsToVmatOperator)
    bpy.utils.register_class(OpenLinkOperator)
    bpy.utils.register_class(ConvertMaterialsToVmatPanel)

def unregister():
    bpy.utils.unregister_class(ConvertMaterialsToVmatOperator)
    bpy.utils.unregister_class(OpenLinkOperator)
    bpy.utils.unregister_class(ConvertMaterialsToVmatPanel)

if __name__ == "__main__":
    register()
