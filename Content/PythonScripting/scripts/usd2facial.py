import pxr
import unreal
import os
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

EXAMPLE_ANIMATION_REFERENCE = "/Script/Engine.AnimSequence'/Game/Assets/Animations/anim_a2f_empty_60fps'"


def convert_usd_to_animation(anim_usd_file):
    anim_file = anim_usd_file

    audio_file = os.path.splitext(os.path.basename(anim_usd_file))[0]
    out_anim_path = f"/Game/Assets/Animations/{audio_file}_facial"

    logging.info(f'Starting conversion for {anim_file}.')

    # Open USD stage
    try:
        root_layer = pxr.Sdf.Layer.FindOrOpen(anim_file)
        usd_stage = pxr.Usd.Stage.Open(root_layer)
        default_prim = usd_stage.GetDefaultPrim()
        skel_anim = default_prim.GetChildren()[0]

        # Retrieve curve names and values
        curve_names_attr = skel_anim.GetPrim().GetAttribute("custom:mh_curveNames")
        curve_names = curve_names_attr.Get(pxr.Usd.TimeCode.Default())
        curve_values_attr = skel_anim.GetPrim().GetAttribute("custom:mh_curveValues")
        time_samples = curve_values_attr.GetTimeSamples()

        curve_values_time_samples = {}
        for time_code in time_samples:
            curve_values_time_samples[time_code] = curve_values_attr.Get(pxr.Usd.TimeCode(time_code))

        # Manage animation asset
        asset_lib = unreal.EditorAssetLibrary
        if asset_lib.does_asset_exist(out_anim_path):
            asset_lib.delete_asset(out_anim_path)
            logging.info(f'Deleted existing asset at {out_anim_path}.')

        asset_lib.duplicate_asset(EXAMPLE_ANIMATION_REFERENCE, out_anim_path)
        anim_sequence = asset_lib.load_asset(out_anim_path)

        # Set up animation parameters
        stage = skel_anim.GetPrim().GetStage()
        time_codes_per_second = stage.GetTimeCodesPerSecond() if stage.GetRootLayer().HasTimeCodesPerSecond() else 24.0
        start_time_code = stage.GetStartTimeCode() if stage.GetRootLayer().HasStartTimeCode() else 0.0
        end_time_code = stage.GetEndTimeCode() if stage.GetRootLayer().HasEndTimeCode() else 0.0

        controller = anim_sequence.controller
        controller.open_bracket("Import animation bracket", should_transact=False)
        controller.remove_all_bone_tracks(should_transact=False)
        controller.remove_all_curves_of_type(unreal.RawCurveTrackTypes.RCT_FLOAT, should_transact=False)
        controller.set_play_length((end_time_code - start_time_code + 0.5) / time_codes_per_second,
                                   should_transact=False)
        denominator = 1000
        controller.set_frame_rate(
            unreal.FrameRate(numerator=time_codes_per_second * denominator, denominator=denominator),
            should_transact=False)

        # Add curves to the controller
        for idx, curve_name in enumerate(curve_names):
            curve_id = anim_sequence.get_skeleton().find_curve_identifier(curve_name,
                                                                          unreal.RawCurveTrackTypes.RCT_FLOAT)
            controller.add_curve(curve_id, should_transact=False)
            rich_curve_keys = []
            for curve_time_sample in curve_values_time_samples:
                rich_curve_keys.append(unreal.RichCurveKey(curve_time_sample / time_codes_per_second,
                                                           curve_values_time_samples[curve_time_sample][idx]))
            controller.set_curve_keys(curve_id, rich_curve_keys, should_transact=False)

        controller.update_curve_names_from_skeleton(anim_sequence.get_skeleton(), unreal.RawCurveTrackTypes.RCT_FLOAT,
                                                    should_transact=False)
        controller.close_bracket(should_transact=False)

        # unreal.EditorAssetLibrary.save_loaded_asset(anim_sequence)
        logging.info(f'Successfully converted {anim_file} to {out_anim_path}.')
        return out_anim_path

    except Exception as e:
        logging.error(f'Error during conversion: {e}')

# Example usage
# convert_usd_to_animation("path/to/your/animation_file.usd")
