import unreal
import math

# Create an instance of the Editor Level Library
editor_level_lib = unreal.EditorLevelLibrary()

def create_background(plane_name, material_path, new_material_name, texture_name, aspect_ratio, position, scale_factor):
    # Create a Plane
    plane_actor = editor_level_lib.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
    plane_actor.set_actor_label(plane_name)

    # Set the Plane Static Mesh
    static_mesh_comp = plane_actor.static_mesh_component
    plane_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Plane')
    static_mesh_comp.set_static_mesh(plane_mesh)

    # Load the Base Material (ensure this is a material, not a texture)
    base_material = unreal.EditorAssetLibrary.load_asset(material_path)

    if not base_material or not isinstance(base_material, unreal.MaterialInterface):
        unreal.log_error("Failed to load the base material. Ensure the asset path is correct and the asset is a Material or MaterialInstance.")
    else:
        # Create a Material Instance from the base material
        material_factory = unreal.MaterialInstanceConstantFactoryNew()
        material_instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(new_material_name, '/Game/Materials', unreal.MaterialInstanceConstant, material_factory)

        # Set the parent of the material instance to the base material
        material_instance.set_editor_property('parent', base_material)

        # Load the 2D Background Texture
        #texture = unreal.EditorAssetLibrary.load_asset(material_path.replace('Material', 'Texture'))
        texture = unreal.EditorAssetLibrary.load_asset(f'/Game/Assets/Backgrounds/{texture_name}')

        # Ensure the texture is properly loaded and set in the material instance
        if texture and isinstance(texture, unreal.Texture):
            # The texture node must be converted to parameter in the material node
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'Image', texture)

        # Assign the Material Instance to the Plane
        static_mesh_comp.set_material(0, material_instance)

        # Calculate the Plane Size Based on Aspect Ratio
        base_width = 100.0  # Base width (adjust as needed)
        base_height = base_width / aspect_ratio  # Compute height based on the aspect ratio

        # Adjust the plane size by scaling
        plane_scale = unreal.Vector(scale_factor * base_width / 100.0, scale_factor * base_height / 100.0, 1)
        plane_actor.set_actor_scale3d(plane_scale)

        # Set the position of the Plane
        plane_actor.set_actor_location(position, False, True)  # False for sweep, True for teleport
        plane_actor.set_actor_rotation(unreal.Rotator(90,0,0), True)

        unreal.log(f"Plane '{plane_name}' created with aspect ratio {aspect_ratio} and scaled to {plane_scale}.")

        return plane_actor
