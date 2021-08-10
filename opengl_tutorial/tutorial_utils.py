import grpc

import manim.utils.opengl as opengl
import threejs
from manim import *
from _grpc.gen import threejs_pb2, threejs_pb2_grpc
from manim.opengl import *
from manim.utils import space_ops
from threejs import *

channel = grpc.insecure_channel(
    "localhost:50051", options=[("grpc.max_receive_message_length", 8 * 1024 * 1024)]
)
geometry_stub = threejs_pb2_grpc.GeometryServiceStub(channel)
material_stub = threejs_pb2_grpc.MaterialServiceStub(channel)


def grpc_again():
    geometry_response = getattr(geometry_stub, f"Hello")(
        getattr(threejs_pb2, f"HelloRequest")()
    )
    print(geometry_response.response)


def get_geometry(name, config=None, wireframe=False):
    if config is None:
        config = {}
    geometry_response = getattr(geometry_stub, f"{name}")(
        getattr(threejs_pb2, f"{name}Request")(**config, wireframe=wireframe)
    )
    geometry = Geometry(
        geometry_response.position,
        geometry_response.normal,
        geometry_response.index,
    )
    return geometry


def get_material(context, name, config=None):
    if config is None:
        config = {}
    material_response = getattr(material_stub, f"{name}")(
        getattr(threejs_pb2, f"{name}Request")()
    )
    material = getattr(threejs, name)(
        context,
        material_response.vertex_shader,
        material_response.fragment_shader,
        config,
    )
    return material


def get_three_mesh(context, geometry_config=None, material_config=None):
    geometry_name = geometry_config["name"]
    material_name = material_config["name"]
    del geometry_config["name"]
    del material_config["name"]
    geometry = get_geometry(geometry_name, config=geometry_config)
    material = get_material(context, material_name, config=material_config)
    return ThreeMesh(material, geometry.attributes, indices=geometry.index)


def get_2d_box(width, height, material, radius):
    height_geometry = get_geometry(
        "CylinderGeometry",
        {
            "radius_top": radius,
            "radius_bottom": radius,
            "height": width,
        },
    )
    width_geometry = get_geometry(
        "CylinderGeometry",
        {
            "radius_top": radius,
            "radius_bottom": radius,
            "height": height,
        },
    )

    line = Mesh(geometry=width_geometry, material=material)
    line2 = Mesh(geometry=width_geometry, material=material)
    line3 = Mesh(geometry=height_geometry, material=material)
    line4 = Mesh(geometry=height_geometry, material=material)

    line.model_matrix = opengl.translation_matrix(x=width / 2) @ line.model_matrix
    line2.model_matrix = opengl.translation_matrix(x=-width / 2) @ line2.model_matrix
    line3.model_matrix = (
        opengl.translation_matrix(y=height / 2)
        @ opengl.rotation_matrix(z=PI / 2)
        @ line3.model_matrix
    )
    line4.model_matrix = (
        opengl.translation_matrix(y=-height / 2)
        @ opengl.rotation_matrix(z=PI / 2)
        @ line4.model_matrix
    )

    line3.normal_matrix = opengl.rotation_matrix(z=PI / 2) @ line3.normal_matrix
    line4.normal_matrix = opengl.rotation_matrix(z=PI / 2) @ line4.normal_matrix

    return Object3D(line, line2, line3, line4)


def get_3d_box(width, height, depth, material, radius):
    # Top.
    manim_space_top = get_2d_box(width, depth, material, radius)
    manim_space_top.model_matrix = (
        opengl.translation_matrix(y=height / 2)
        @ opengl.rotation_matrix(x=PI / 2)
        @ manim_space_top.model_matrix
    )
    manim_space_top.normal_matrix = (
        opengl.translation_matrix(y=height / 2)
        @ opengl.rotation_matrix(x=PI / 2)
        @ manim_space_top.normal_matrix
    )

    # Bottom.
    manim_space_bottom = get_2d_box(width, depth, material, radius)
    manim_space_bottom.model_matrix = (
        opengl.translation_matrix(y=-height / 2)
        @ opengl.rotation_matrix(x=PI / 2)
        @ manim_space_bottom.model_matrix
    )
    manim_space_bottom.normal_matrix = (
        opengl.translation_matrix(y=-height / 2)
        @ opengl.rotation_matrix(x=PI / 2)
        @ manim_space_bottom.normal_matrix
    )

    # Front.
    manim_space_front = get_2d_box(width, height, material, radius)
    manim_space_front.model_matrix = (
        opengl.translation_matrix(z=depth / 2) @ manim_space_front.model_matrix
    )
    manim_space_front.normal_matrix = (
        opengl.translation_matrix(z=depth / 2) @ manim_space_front.normal_matrix
    )

    # Back.
    manim_space_back = get_2d_box(width, height, material, radius)
    manim_space_back.model_matrix = (
        opengl.translation_matrix(z=-depth / 2) @ manim_space_back.model_matrix
    )
    manim_space_back.normal_matrix = (
        opengl.translation_matrix(z=-depth / 2) @ manim_space_back.normal_matrix
    )

    return Object3D(
        manim_space_top,
        manim_space_bottom,
        manim_space_front,
        manim_space_back,
    )


def get_axes(context, length):
    # x axis.
    x_axis_material = get_material(
        context,
        "PhongMaterial",
        {
            "diffuse": [1.0, 0, 0],
            "emissive": [0, 0, 0],
            "specular": [1 / 3.0, 1 / 3.0, 1 / 3.0],
            "shininess": 5.0,
            "opacity": 1,
        },
    )
    x_axis = Mesh(
        geometry=get_geometry(
            "CylinderGeometry",
            {
                "radius_top": 0.05,
                "radius_bottom": 0.05,
                "height": length,
            },
        ),
        material=x_axis_material,
    )
    x_axis.model_matrix = (
        opengl.translation_matrix(x=length / 2)
        @ opengl.rotation_matrix(z=PI / 2)
        @ x_axis.model_matrix
    )
    x_axis.normal_matrix = opengl.rotation_matrix(z=PI / 2) @ x_axis.normal_matrix

    # y axis.
    y_axis_material = get_material(
        context,
        "PhongMaterial",
        {
            "diffuse": [0, 1.0, 0],
            "emissive": [0, 0, 0],
            "specular": [1 / 3.0, 1 / 3.0, 1 / 3.0],
            "shininess": 5.0,
            "opacity": 1,
        },
    )
    y_axis = Mesh(
        geometry=get_geometry(
            "CylinderGeometry",
            {
                "radius_top": 0.05,
                "radius_bottom": 0.05,
                "height": length,
            },
        ),
        material=y_axis_material,
    )
    y_axis.model_matrix = (
        opengl.rotation_matrix(z=PI / 2)
        @ opengl.translation_matrix(x=length / 2)
        @ opengl.rotation_matrix(z=PI / 2)
        @ y_axis.model_matrix
    )
    y_axis.normal_matrix = opengl.rotation_matrix(z=PI / 2) @ y_axis.normal_matrix

    # z axis.
    z_axis_material = get_material(
        context,
        "PhongMaterial",
        {
            "diffuse": [0, 0, 1.0],
            "emissive": [0, 0, 0],
            "specular": [1 / 3.0, 1 / 3.0, 1 / 3.0],
            "shininess": 5.0,
            "opacity": 1,
        },
    )
    z_axis = Mesh(
        geometry=get_geometry(
            "CylinderGeometry",
            {
                "radius_top": 0.05,
                "radius_bottom": 0.05,
                "height": length,
            },
        ),
        material=z_axis_material,
    )
    z_axis.model_matrix = (
        opengl.rotation_matrix(x=PI / 2)
        @ opengl.rotation_matrix(z=PI / 2)
        @ opengl.translation_matrix(x=length / 2)
        @ opengl.rotation_matrix(z=PI / 2)
        @ z_axis.model_matrix
    )
    z_axis.normal_matrix = opengl.rotation_matrix(z=PI / 2) @ z_axis.normal_matrix

    return Object3D(x_axis, y_axis, z_axis)


def get_camera(context):
    camera_width = 1.5
    lens_height = 0.6
    phong_material = get_material(
        context,
        "PhongMaterial",
        {
            "diffuse": [0.3, 0.3, 0.3],
            "emissive": [0, 0, 0],
            "specular": [1 / 3.0, 1 / 3.0, 1 / 3.0],
            "shininess": 1.0,
            "opacity": 1,
        },
    )
    camera_body = ThreeMesh(
        geometry=get_geometry("BoxGeometry", {"width": camera_width}),
        material=phong_material,
    )
    camera_lens = ThreeMesh(
        geometry=get_geometry("ConeGeometry", {"radius": 0.5, "height": lens_height}),
        material=phong_material,
    )
    camera_lens.model_matrix = (
        opengl.translation_matrix(x=camera_width / 2 + lens_height / 2)
        @ opengl.rotation_matrix(z=PI / 2)
        @ camera_lens.model_matrix
    )
    return Object3D(camera_body, camera_lens)


def look_at(camera, target, up_vector=OUT, looking_axis="-z"):
    # Rotate the camera so that it points toward the target.
    if looking_axis == "-z":
        camera_front_dir = -camera.model_matrix[:3, 2]
    elif looking_axis == "z":
        camera_front_dir = camera.model_matrix[:3, 2]
    else:
        raise RuntimeError(f"Unknown looking axis {looking_axis}")

    camera_to_target = normalize(target - camera.model_matrix[:, 3][:3])
    rotation_axis = np.cross(camera_to_target, camera_front_dir)
    angle = 2 * np.arctan2(
        np.linalg.norm(camera_to_target - normalize(camera_front_dir)),
        np.linalg.norm(camera_to_target + normalize(camera_front_dir)),
    )
    rotation_matrix = space_ops.rotation_matrix(
        -angle,
        rotation_axis,
        homogeneous=True,
    )

    camera_position = camera.model_matrix[:, 3][:3]
    camera.model_matrix = (
        opengl.translation_matrix(*camera_position)
        @ rotation_matrix
        @ opengl.translation_matrix(*-camera_position)
        @ camera.model_matrix
    )
    if isinstance(camera, Mesh):
        camera.normal_matrix = rotation_matrix @ camera.normal_matrix

    # Rotate the camera so that it's right-side-up.
    # Project the z-axis onto the plane defined by the camera->target vector.
    projected_z_axis = normalize(
        up_vector - np.dot(up_vector, camera_to_target) * camera_to_target
    )

    # Rotate the camera so that its y-axis is aligned with the z-axis.
    camera_y_vec = camera.model_matrix[:3, 1]
    rotation_axis = np.cross(projected_z_axis, camera_y_vec)
    angle = 2 * np.arctan2(
        np.linalg.norm(projected_z_axis - normalize(camera_y_vec)),
        np.linalg.norm(projected_z_axis + normalize(camera_y_vec)),
    )
    rotation_matrix = space_ops.rotation_matrix(
        -angle,
        rotation_axis,
        homogeneous=True,
    )

    camera.model_matrix = (
        opengl.translation_matrix(*-camera_position)
        @ rotation_matrix
        @ opengl.translation_matrix(*camera_position)
        @ camera.model_matrix
    )
    if isinstance(camera, Mesh):
        camera.normal_matrix = rotation_matrix @ camera.normal_matrix


def mouse_over_camera_frame_mob(scene, mob):
    model = mob.hierarchical_model_matrix()
    model_inv = np.linalg.inv(model)

    near = 2
    camera_x = scene.camera.model_matrix[:3, 0]
    camera_y = scene.camera.model_matrix[:3, 1]
    camera_z = scene.camera.model_matrix[:3, 2]
    point = scene.mouse_point.get_center()
    world_space_point = (
        scene.camera.get_position()
        - camera_z * near
        + camera_x
        * (point[0] / config["frame_x_radius"])
        * (config["frame_x_radius"] / 6)
        + camera_y
        * (point[1] / config["frame_y_radius"])
        * (config["frame_y_radius"] / 6)
    )

    homogeneous_point = np.hstack((world_space_point, 1))
    model_space_point = model_inv @ homogeneous_point

    bounding_box = mob.get_bounding_box()
    x_condition = bounding_box[0][0] <= model_space_point[0] <= bounding_box[2][0]
    y_condition = bounding_box[0][1] <= model_space_point[1] <= bounding_box[2][1]
    return x_condition and y_condition


def get_button(scene, text):
    # Add a button.
    camera_button = OpenGLVGroup()

    camera_button_text = OpenGLText(text, font="Sans Serif")
    camera_button.add(camera_button_text, update_parent=True)
    scene.add(camera_button_text)

    text_bounding_box = camera_button_text.get_bounding_box()
    text_width = text_bounding_box[2][0] - text_bounding_box[0][0]
    text_height = text_bounding_box[2][1] - text_bounding_box[0][1]

    padding = 0.2
    padded_width = text_width + 2 * padding
    padded_height = text_height + 2 * padding

    camera_button_border = OpenGLVMobject(stroke_width=8)
    camera_button_border.data["points"] = [
        LEFT * padded_width / 2 + UP * padded_height / 2
    ]
    camera_button_border.add_line_to(RIGHT * padded_width / 2 + UP * padded_height / 2)
    camera_button_border.add_line_to(
        RIGHT * padded_width / 2 + DOWN * padded_height / 2
    )
    camera_button_border.add_line_to(LEFT * padded_width / 2 + DOWN * padded_height / 2)
    camera_button_border.add_line_to(LEFT * padded_width / 2 + UP * padded_height / 2)
    camera_button.add(camera_button_border, update_parent=True)
    scene.add(camera_button_border)
    return camera_button


def get_grid_lines(x_size, y_size):
    grid = OpenGLVGroup()

    # Add vertical gridlines.
    for i in range(-x_size, x_size + 1):
        grid.add(
            OpenGLLine(UP * y_size, DOWN * y_size, stroke_opacity=0.5).shift(RIGHT * i)
        )

    # Add horizontal gridlines.
    for i in range(-y_size, y_size + 1):
        grid.add(
            OpenGLLine(LEFT * x_size, RIGHT * x_size, stroke_opacity=0.5).shift(UP * i)
        )
    return grid
