import re

import numpy as np

import manim.utils.opengl as opengl
from manim.renderer.shader import Mesh
from manim.utils.color import color_to_rgb


class ThreeMesh(Mesh):
    def set_uniforms(self, renderer):
        from moderngl.program_members.uniform import Uniform

        for k, v in self.shader.shader_program._members.items():
            view_matrix = renderer.camera.get_view_matrix(format=False)
            if isinstance(v, Uniform):
                if k == "viewMatrix":
                    self.shader.set_uniform(
                        "viewMatrix", opengl.matrix_to_shader_input(view_matrix)
                    )
                if k == "projectionMatrix":
                    self.shader.set_uniform(
                        "projectionMatrix",
                        renderer.camera.projection_matrix,
                    )
                if k == "modelViewMatrix":
                    self.shader.set_uniform(
                        "modelViewMatrix",
                        opengl.matrix_to_shader_input(
                            view_matrix @ self.hierarchical_model_matrix()
                        ),
                    )
                if k == "normalMatrix":
                    self.shader.set_uniform(
                        "normalMatrix",
                        opengl.matrix_to_shader_input(
                            view_matrix[:3, :3] @ self.hierarchical_normal_matrix()
                        ),
                    )
                if k == "isOrthographic":
                    self.shader.set_uniform(
                        "isOrthographic", renderer.camera.orthographic
                    )
                point_lights_pattern = re.compile("pointLights\[(\d+)\]")
                point_lights_match = re.match(point_lights_pattern, k)
                if point_lights_match is not None:
                    point_light_index = int(point_lights_match.group(1))
                    # TODO: Use a while loop and warn if the shader can't contain all of
                    # the lights.
                    if len(renderer.scene.point_lights) > point_light_index:
                        point_light_config = renderer.scene.point_lights[
                            point_light_index
                        ]
                        camera_space_light_position = view_matrix @ np.array(
                            point_light_config["position"] + [1]
                        )
                        camera_space_light_position = camera_space_light_position[:3]

                        self.shader.set_uniform(
                            f"pointLights[{point_light_index}].position",
                            tuple(camera_space_light_position),
                        )
                        self.shader.set_uniform(
                            f"pointLights[{point_light_index}].color",
                            tuple(point_light_config["color"]),
                        )
                        self.shader.set_uniform(
                            f"pointLights[{point_light_index}].distance",
                            point_light_config["distance"],
                        )
                        self.shader.set_uniform(
                            f"pointLights[{point_light_index}].decay",
                            point_light_config["decay"],
                        )
                if (
                    k == "ambientLightColor"
                    and renderer.scene.ambient_light is not None
                ):
                    ambient_light_rgb = color_to_rgb(
                        renderer.scene.ambient_light["color"]
                    )
                    ambient_light_values = [
                        col * renderer.scene.ambient_light["intensity"]
                        for col in ambient_light_rgb
                    ]
                    self.shader.set_uniform(
                        "ambientLightColor",
                        tuple(ambient_light_values),
                    )
