from zoneinfo import available_timezones

import unreal


available_metahumans = ["Aoi", "Stephane", "Payton", "Glenda"]

class MetaHuman:

    name = "Aoi"
    position = "middle"
    rotation = 0

    def __init__(self, name, position, rotation):
        if name not in available_metahumans:
            unreal.log_error(f"Unable to find metahuman actor with this name '{self.name}'")
        else:
            self.name = name
            self.position = position
            self.rotation = rotation


    def add_to_scene(self, plane_actor):
        # Load the Metahuman asset
        metahuman_class = unreal.EditorAssetLibrary.load_asset(f"/Game/MetaHumans/{self.name}/BP_{self.name}")

        #check if not metahuman class
        # todo

        #default location and rotation
        location_in_scene = unreal.Vector(0.0, 0.0, 0.0)
        rotation_in_scene = unreal.Rotator(0.0, self.rotation, 0.0)

        #Create the metahuman Actor
        metahuman_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(metahuman_class, location_in_scene, rotation_in_scene)
        if not metahuman_actor:
            unreal.log_error(f"Failed to create MetaHuman actor '{self.name}'")

        metahuman_actor.set_actor_label(self.name)

        # Retrieve the plane's location and scale
        plane_location = plane_actor.get_actor_location()
        plane_scale = plane_actor.get_actor_scale3d()

        # Calculate the height of the plane (assuming uniform scaling)
        plane_width = 100.0 * plane_scale.x
        plane_height = 100.0 * plane_scale.y

        # Calculate Metahuman position relative to the plane
        metahuman_location = unreal.Vector()
        if self.position == 'left':
            metahuman_location = unreal.Vector(plane_location.x - (plane_scale.x * 20.0),
                                               plane_location.y + (plane_height / 1.4),
                                               plane_location.z + (plane_height / 1.6))
        elif self.position == 'right':
            metahuman_location = unreal.Vector(plane_location.x + (plane_scale.x * 20.0),
                                               plane_location.y + (plane_height / 1.4),
                                               plane_location.z + (plane_height / 1.6))
        elif self.position == 'far_right':
            metahuman_location = unreal.Vector(plane_location.x + (plane_scale.x * 30.0),
                                               plane_location.y + (plane_height / 1.6),
                                               plane_location.z + (plane_height / 2))
        elif self.position == 'far_left':
            metahuman_location = unreal.Vector(plane_location.x - (plane_scale.x * 30.0),
                                               plane_location.y + (plane_height / 1.6),
                                               plane_location.z + (plane_height / 2))
        elif self.position == 'middle':
            metahuman_location = unreal.Vector(plane_location.x, plane_location.y + (plane_height / 1.4),
                                               plane_location.z + (plane_height / 1.4))

        metahuman_location = unreal.Vector(metahuman_location.x, metahuman_location.y, metahuman_location.z - 300)

        # Set MetaHuman position
        metahuman_actor.set_actor_location(metahuman_location, False, True)

        # Calculate MetaHuman scale based on plane height
        desired_height_ratio = 0.4  # MetaHuman height should be 50% of the plane's height
        scale_factor = (plane_height * desired_height_ratio) / 100.0  # Scale factor for height

        # Apply the scale to MetaHuman
        metahuman_actor.set_actor_scale3d(unreal.Vector(scale_factor, scale_factor, scale_factor))

        unreal.log(
            f"MetaHuman '{self.name}' created, positioned at {metahuman_location}, and scaled with factor {scale_factor}.")

        return metahuman_actor





