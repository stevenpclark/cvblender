import sys
import os
import random
from random import uniform
from math import pi, radians
import subprocess
from glob import glob
import json
import argparse


def render(cfg_path):
    import bpy

    with open(cfg_path, 'r') as cfg_file:
        cfg = json.load(cfg_file)

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
    object = bpy.data.objects['TargetOrigin']

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
        target_x_pos = uniform(-jitter_range/2.0, jitter_range/2.0)
        target_y_pos = uniform(-jitter_range/2.0, jitter_range/2.0)
        target_z_pos = 0.0

        emission_node.inputs[1].default_value = uniform(cfg['min_sun_strength'], cfg['max_sun_strength'])
        blur_node.inputs[1].default_value = uniform(0.0, cfg['max_blur'])

        cam.rotation_euler = (radians(90-cam_el_deg), 0.0, radians(180.0 - cam_az_deg))
        sun.rotation_euler = (radians(90-sun_el_deg), 0.0, radians(180.0 - sun_az_deg))
        object.location = (target_x_pos, target_y_pos, target_z_pos)

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

    if not inside_blender:
        args = parser.parse_args()

        script_name = os.path.basename(__file__)
        subprocess.check_call(['blender', 'test.blend', '-b', '-P', script_name, '--', args.cfg_path])
    else:
        args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
        render(args.cfg_path)


