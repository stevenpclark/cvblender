import sys
import os
import random
from random import uniform
from math import pi, radians
import subprocess
from glob import glob
import json
import argparse


def render(cfg):
    import bpy

    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = cfg['x_dim']
    scene.render.resolution_y = cfg['y_dim']
    scene.render.resolution_percentage = 100
    tree = scene.node_tree
    bg_node = tree.nodes['Image']
    blur_node = tree.nodes['Blur']
    emission_node = bpy.data.lamps['Lamp'].node_tree.nodes['Emission']

    cam = bpy.data.objects['CameraTarget']
    sun = bpy.data.objects['SunTarget']
    obj = bpy.data.objects['TargetOrigin']

    for i in range(cfg['num_images']):
        output_filename = os.path.join(cfg['output_dir'], '%s%05d.png'%(cfg['filename_base'], i))
        #randomly pick a background
        bg_image_pattern = cfg['bg_image_pattern']
        bg_image_paths = glob(bg_image_pattern)
        bg_node.image.filepath = random.choice(bg_image_paths)

        cam_az_deg = uniform(cfg['cam_az_min'], cfg['cam_az_max'])
        cam_el_deg = uniform(cfg['cam_el_min'], cfg['cam_el_max'])

        sun_az_deg = uniform(cfg['sun_az_min'], cfg['sun_az_max'])
        sun_el_deg = uniform(cfg['sun_el_min'], cfg['sun_el_max'])

        jitter_range = cfg['pos_jitter_range']
        obj_x_pos = uniform(-jitter_range/2.0, jitter_range/2.0)
        obj_y_pos = uniform(-jitter_range/2.0, jitter_range/2.0)
        obj_z_pos = 0.0
        obj_roll_deg = uniform(cfg['roll_min'], cfg['roll_max'])
        obj_pitch_deg = uniform(cfg['pitch_min'], cfg['pitch_max'])
        obj_yaw_deg = uniform(cfg['yaw_min'], cfg['yaw_max'])

        emission_node.inputs[1].default_value = uniform(cfg['min_sun_strength'], cfg['max_sun_strength'])
        blur_node.inputs[1].default_value = uniform(0.0, cfg['max_blur'])

        cam.rotation_euler = (radians(90-cam_el_deg), 0.0, radians(180.0 - cam_az_deg))
        sun.rotation_euler = (radians(90-sun_el_deg), 0.0, radians(180.0 - sun_az_deg))
        obj.location = (obj_x_pos, obj_y_pos, obj_z_pos)
        #TODO: verify this actually behaves as expected:
        obj.rotation_euler = (radians(obj_pitch_deg), radians(obj_roll_deg), radians(obj_yaw_deg))

        scene.render.filepath = output_filename
        bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Uses blender to render a bunch of variations of a scene.')
    parser.add_argument('cfg_path', help='path to json config file')

    try:
        import bpy
        inside_blender = True
    except ImportError:
        inside_blender = False

    if inside_blender:
        args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    else:
        args = parser.parse_args()

    with open(args.cfg_path, 'r') as cfg_file:
        cfg = json.load(cfg_file)

    if not inside_blender:
        script_name = os.path.basename(__file__)
        subprocess.check_call(['blender', cfg['blender_file'], '-b', '-P', script_name, '--', args.cfg_path])
    else:
        render(cfg)


