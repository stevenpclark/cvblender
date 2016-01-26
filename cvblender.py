import os
import random
from random import uniform
from math import pi, radians
import subprocess
from glob import glob

def run():
    num_images_per_class = 10
    render_size = 128

    bg_image_paths = glob('test_bg*')
    output_dir = os.path.join(os.path.dirname(__file__), 'output')

    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = render_size
    scene.render.resolution_y = render_size
    scene.render.resolution_percentage = 100
    tree = scene.node_tree
    bg_node = tree.nodes['Image']
    blur_node = tree.nodes['Blur']

    print(bg_node.image.filepath)

    cam = bpy.data.objects['CameraTarget']
    light = bpy.data.objects['SunTarget']
    object = bpy.data.objects['TargetOrigin']

    cam_az_min_deg = 0.0
    cam_az_max_deg = 360.0
    cam_el_min_deg = 30.0
    cam_el_max_deg = 90.0

    light_az_min_deg = 0.0
    light_az_max_deg = 360.0
    light_el_min_deg = 30.0
    light_el_max_deg = 90.0

    target_jitter_range = 10.0
    max_blur = 1.0
    max_light_strength = 2.0


    for i in range(num_images_per_class):
        bg_node.image.filepath = random.choice(bg_image_paths)

        cam_az_deg = uniform(cam_az_min_deg, cam_az_max_deg)
        cam_el_deg = uniform(cam_el_min_deg, cam_el_max_deg)

        light_az_deg = uniform(light_az_min_deg, light_az_max_deg)
        light_el_deg = uniform(light_el_min_deg, light_el_max_deg)

        target_x_pos = uniform(-target_jitter_range/2.0, target_jitter_range/2.0)
        target_y_pos = uniform(-target_jitter_range/2.0, target_jitter_range/2.0)
        target_z_pos = 0.0

        bpy.data.lamps['Lamp'].node_tree.nodes['Emission'].inputs[1].default_value = uniform(0.0, max_light_strength)
        blur_node.inputs[1].default_value = uniform(0.0, max_blur)

        cam.rotation_euler = (radians(90-cam_el_deg), 0.0, radians(180.0 - cam_az_deg))
        light.rotation_euler = (radians(90-light_el_deg), 0.0, radians(180.0 - light_az_deg))
        object.location = (target_x_pos, target_y_pos, target_z_pos)

        scene.render.filepath = os.path.join(output_dir, 'test%05d.png'%i)
        bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    try:
        import bpy
        run()
    except ImportError:
        #not running inside blender, let's call it
        script_name = os.path.basename(__file__)
        subprocess.check_call(['blender', 'test.blend', '-b', '-P', script_name])

