import collections

import dearpygui.core

import manim.utils.opengl as opengl
import manim.utils.space_ops as space_ops
import tutorial_utils
from manim import *
from manim.opengl import *
from manim.renderer.opengl_renderer import OpenGLCamera


class OpenGLPipeline(Scene):
    def construct(self):
        # self.skip_animation_preview = True
        diagrams = VGroup()
        vertices = VGroup(
            Dot().move_to(-1 * RIGHT + 2 * UP),
            Dot().move_to(-2 * RIGHT - 1 * UP),
            Dot().move_to(1 * RIGHT + 0 * UP),
        ).shift(0.5 * DOWN)

        vertices_label = Text("Vertices").next_to(vertices, UP, buff=0.5)
        self.add(vertices, vertices_label)

        # Vertices.
        self.play(FadeIn(vertices_label, shift=DOWN))
        self.interactive_embed()

        vertices_diagram = VGroup(vertices_label, vertices)
        diagrams.add(vertices_diagram.copy())

        # Vertex Shader.
        vertex_shader_label = Text("Vertex Shader").move_to(
            vertices_label.get_center()
        )
        self.play(FadeOut(vertices_label, shift=UP))
        self.play(FadeIn(vertex_shader_label, shift=DOWN))

        vertex_shader_diagram = VGroup(vertex_shader_label, vertices)
        diagrams.add(vertex_shader_diagram.copy())
        self.interactive_embed()

        # self.skip_animation_preview = False
        # Primitives Generation.
        primitives_generation_label = Text("Primitives Generation").move_to(
            vertex_shader_label.get_center()
        )
        self.play(FadeOut(vertex_shader_label, shift=UP))
        self.play(FadeIn(primitives_generation_label, shift=DOWN))
        triangle = Polygon(*[dot.get_center() for dot in vertices], color=WHITE)
        self.play(Create(triangle))
        self.play(FadeOut(vertices))

        primitives_generation_diagram = VGroup(
            primitives_generation_label, triangle
        )
        diagrams.add(primitives_generation_diagram.copy())
        self.interactive_embed()

        # Rasterization.
        rasterization_label = Text("Rasterization").move_to(
            primitives_generation_label.get_center()
        )
        self.play(FadeOut(primitives_generation_label, shift=UP))
        self.play(FadeIn(rasterization_label, shift=DOWN))

        top_left = Dot(
            triangle.get_left()[0] * RIGHT + triangle.get_top()[1] * UP
        )
        bottom_right = Dot(
            triangle.get_right()[0] * RIGHT + triangle.get_bottom()[1] * UP
        )
        grid_width = bottom_right.get_center()[0] - top_left.get_center()[0]
        grid_height = top_left.get_center()[1] - bottom_right.get_center()[1]

        triangle_points = triangle.get_vertices()
        triangle_normals = []
        for i in range(3):
            start = triangle_points[i]
            end = triangle_points[(i + 1) % 3]
            vec = end - start
            triangle_normals.append(normalize(rotate_vector(vec, PI / 2)))

        def point_inside_triangle(point: np.ndarray, triangle: Polygon):
            triangle_points = triangle.get_vertices()
            for i in range(3):
                translated_point = point - triangle_points[i]
                dot_product = np.dot(translated_point, triangle_normals[i])
                if dot_product < 0:
                    return False
            return True

        square_side_length = 0.18
        pixels = VGroup()
        outside_pixels = VGroup()
        inside_pixels = VGroup()
        for j in range(int(grid_height // square_side_length) + 1):
            for i in range(int(grid_width // square_side_length) + 1):
                # Place a square.
                dot_location = top_left.get_center().copy()
                dot_location += RIGHT * ((i + 0.5) * square_side_length)
                dot_location += DOWN * ((j + 0.5) * square_side_length)
                inside = point_inside_triangle(dot_location, triangle)
                if inside:
                    fill_color = WHITE
                else:
                    fill_color = BLACK
                pixel = Square(
                    side_length=0.15,
                    stroke_width=1,
                    fill_color=fill_color,
                    fill_opacity=1,
                ).move_to(dot_location)
                pixels.add(pixel)
                if inside:
                    inside_pixels.add(pixel)
                else:
                    outside_pixels.add(pixel)

        self.play(Create(pixels))
        self.play(FadeOut(triangle), FadeOut(outside_pixels))

        rasterization_diagram = VGroup(rasterization_label, inside_pixels)
        diagrams.add(rasterization_diagram.copy())
        self.interactive_embed()

        # Fragment Shader.
        fragment_shader_label = Text("Fragment Shader").move_to(
            rasterization_label.get_center()
        )
        self.play(FadeOut(rasterization_label, shift=UP))
        self.play(FadeIn(fragment_shader_label, shift=DOWN))
        self.play(inside_pixels.animate.set_color(RED))

        fragment_shader_diagram = VGroup(fragment_shader_label, inside_pixels)
        diagrams.add(fragment_shader_diagram.copy())
        self.interactive_embed()

        # Blending.
        blending_label = Text("Blending").move_to(
            fragment_shader_label.get_center()
        )
        self.play(FadeOut(fragment_shader_label, shift=UP))
        self.play(FadeIn(blending_label, shift=DOWN))
        self.play(inside_pixels.animate.set_opacity(0.7))

        blending_diagram = VGroup(blending_label, inside_pixels)
        diagrams.add(blending_diagram.copy())
        self.interactive_embed()

        # Frame Buffer.
        frame_buffer_label = Text("Frame Buffer").move_to(
            blending_label.get_center()
        )
        self.play(FadeOut(blending_label, shift=UP))
        self.play(FadeIn(frame_buffer_label, shift=DOWN))
        triangle.set_color(RED).set_opacity(0.7)
        self.play(FadeOut(inside_pixels), FadeIn(triangle), run_time=1)

        frame_buffer_diagram = VGroup(frame_buffer_label, triangle)
        diagrams.add(frame_buffer_diagram.copy())
        self.interactive_embed()

        # self.skip_animation_preview = False
        diagrams.scale(0.5)
        diagrams[0].move_to(-4.5 * RIGHT + 2.7 * UP)
        diagrams[1].move_to(0 * RIGHT + 2.7 * UP)
        diagrams[2].move_to(4.5 * RIGHT + 2.7 * UP)

        diagrams[3].move_to(-4.5 * RIGHT + 0 * UP)
        diagrams[4].move_to(0 * RIGHT + 0 * UP)
        diagrams[5].move_to(4.5 * RIGHT + 0 * UP)

        diagrams[6].move_to(0 * RIGHT - 2.7 * UP)

        triangle_with_label = VGroup(frame_buffer_label, triangle)
        triangle_with_label.generate_target()
        triangle_with_label.target.scale(0.5).move_to(diagrams[6].get_center())
        self.play(MoveToTarget(triangle_with_label))
        self.play(FadeIn(VGroup(diagrams[:-1])))

        self.interactive_embed()


class HalfScreenTriangle(Scene):
    def construct(self):
        shader = Shader(
            self.renderer.context,
            source=dict(
                vertex_shader="""
                    #version 330
                    in vec3 position;
                    void main() {
                        gl_Position = vec4(position, 1);
                    }
                """,
                fragment_shader="""
                    #version 330
                    out vec4 frag_color;
                    void main() {
                        frag_color = vec4(1, 0, 0, 1);
                    }
                """,
            ),
        )

        attributes = np.zeros(3, dtype=[("position", np.float32, (3,))])
        attributes["position"] = np.array(
            [
                [-1, -1, 0],
                [-1, 1, 0],
                [1, 1, 0],
            ]
        )

        mesh = Mesh(shader, attributes)
        self.add(mesh)

        orthographic_camera = OpenGLCamera(orthographic=True)
        self.renderer.camera = orthographic_camera

        # Add labels.
        labels = []
        dots = []
        offsets = [UP + RIGHT, DOWN + RIGHT, DOWN + LEFT]

        def update_label(index):
            point = mesh.attributes["position"][index][:3]
            ndc_location = (
                point
                * np.array([config["frame_x_radius"], config["frame_y_radius"], 1, 1])[
                    :3
                ]
            )
            dots[index].move_to(ndc_location)
            labels[index].next_to(dots[index], offsets[index])

        for i, point in enumerate(attributes["position"]):
            ndc_location = point * np.array(
                [config["frame_x_radius"], config["frame_y_radius"], 1]
            )
            dot = Dot().move_to(ndc_location)
            dots.append(dot)

            label = MathTex(f"P_{i}").next_to(dot, offsets[i])
            labels.append(label)
            self.add(label)

            def closure(idx):
                dot.add_updater(lambda mob: update_label(idx))

            closure(i)
            self.add(dot)

        def slider_callback(sender, data):
            point = dearpygui.core.get_value(sender)
            mesh.attributes["position"][data] = np.array(point)

        for i in range(3):
            self.widgets.append(
                {
                    "name": f"P{i}",
                    "widget": "slider_float3",
                    "callback": slider_callback,
                    "min_value": -2,
                    "max_value": 2,
                    "callback_data": i,
                    "default_value": mesh.attributes["position"][i],
                }
            )

        self.interactive_embed()


class ProjectionVisualization(Scene):
    def construct(self):
        shader = Shader(
            self.renderer.context,
            source=dict(
                vertex_shader="""
                    #version 330

                    in vec4 position;

                    void main() {
                        gl_Position = position;
                    }
                """,
                fragment_shader="""
                    #version 330

                    out vec4 frag_color;

                    void main() {
                      frag_color = vec4(1, 0, 0, 1);
                    }
                """,
            ),
        )

        attributes = np.zeros(3, dtype=[("position", np.float32, (4,))])
        attributes["position"] = np.array(
            [
                [-1, -1, 0, 1],
                [-1, 1, 0, 1],
                [1, 1, 0, 1],
            ]
        )

        untransformed_mesh = Mesh(shader, attributes)

        transformed_mesh = untransformed_mesh.copy()

        width = config["frame_width"]
        height = config["frame_height"]
        depth = 20
        projection = np.array(
            [
                [2 / width, 0, 0, 0],
                [0, 2 / height, 0, 0],
                [0, 0, 2 / depth, 0],
                [0, 0, 0, 1],
            ]
        )
        transformed_mesh.attributes["position"] = (
            projection @ transformed_mesh.attributes["position"].T
        ).T

        untransformed_points = untransformed_mesh.attributes["position"].copy()
        transformed_points = transformed_mesh.attributes["position"].copy()

        mesh = Mesh(shader, attributes)

        # t = 0

        # def update_mesh(mesh, dt):
        #     nonlocal t
        #     start = untransformed_points
        #     end = transformed_points
        #     v = 0.5 * np.sin(1.5 * t) + 0.5
        #     mesh.attributes["position"] = (1 - v) * start + v * end
        #     t += dt

        def slider_callback(sender, data):
            t = dearpygui.core.get_value(sender)
            start = untransformed_points
            end = transformed_points
            mesh.attributes["position"] = (1 - t) * start + t * end

        self.widgets.append(
            {
                "name": "scale",
                "widget": "slider_float",
                "callback": slider_callback,
                "min_value": 0,
                "max_value": 1,
                "default_value": 0,
            }
        )

        # mesh.add_updater(update_mesh)
        self.add(mesh)

        self.renderer.camera = OpenGLCamera(orthographic=True)
        grid = tutorial_utils.get_grid_lines(7, 5)

        def toggle_grid_lines():
            if grid in self.mobjects:
                self.remove(grid)
            else:
                self.add(grid)

        self.set_key_function(" ", toggle_grid_lines)

        self.interactive_embed()


class ModelVisualization(Scene):
    def construct(self):
        shader = Shader(
            self.renderer.context,
            source=dict(
                vertex_shader="""
                    #version 330

                    uniform mat4 projection;
                    uniform mat4 model;
                    in vec4 position;

                    void main() {
                        gl_Position = projection * model * position;
                    }
                """,
                fragment_shader="""
                    #version 330

                    out vec4 frag_color;

                    void main() {
                      frag_color = vec4(1, 0, 0, 1);
                    }
                """,
            ),
        )

        projection = opengl.orthographic_projection_matrix(near=-10, far=10)
        shader.shader_program["projection"] = projection

        model = tuple(np.eye(4).T.ravel())
        shader.shader_program["model"] = model

        attributes = np.zeros(3, dtype=[("position", np.float32, (4,))])
        attributes["position"] = np.array(
            [
                [-1, -1, 0, 1],
                [-1, 1, 0, 1],
                [1, 1, 0, 1],
            ]
        )

        mesh = Mesh(shader, attributes)
        self.add(mesh)

        translation_matrix = np.eye(4)
        rotation_matrix = np.eye(4)
        scale_matrix = np.eye(4)

        def update_mesh(mesh, dt):
            model_matrix = translation_matrix @ rotation_matrix @ scale_matrix
            mesh.shader.shader_program["model"] = tuple(model_matrix.T.ravel())

        def translation_callback(sender, data):
            nonlocal translation_matrix
            coords = dearpygui.core.get_value(sender)
            translation_matrix = opengl.translation_matrix(*coords)

        def rotation_callback(sender, data):
            nonlocal rotation_matrix
            coords = dearpygui.core.get_value(sender)
            rotation_matrix = opengl.rotation_matrix(*coords)

        def scale_callback(sender, data):
            nonlocal scale_matrix
            val = dearpygui.core.get_value(sender)
            scale_matrix = opengl.scale_matrix(val)

        self.widgets.extend(
            [
                {
                    "name": "translation",
                    "widget": "slider_float3",
                    "callback": translation_callback,
                    "min_value": -10,
                    "max_value": 10,
                },
                {
                    "name": "rotation",
                    "widget": "slider_float3",
                    "callback": rotation_callback,
                    "min_value": -PI,
                    "max_value": PI,
                },
                {
                    "name": "scale",
                    "widget": "slider_float",
                    "callback": scale_callback,
                    "min_value": -PI,
                    "max_value": PI,
                    "default_value": 1,
                },
            ]
        )

        mesh.add_updater(update_mesh)
        self.interactive_embed()


class ViewVisualization(Scene):
    def construct(self):
        self.grid_size = 5
        grid = VGroup()

        # Add x gridlines.
        for i in range(-self.grid_size, self.grid_size + 1):
            grid.add(
                Line(
                    UP * self.grid_size, DOWN * self.grid_size, stroke_opacity=0.5
                ).shift(RIGHT * i)
            )

        # Add y gridlines.
        for i in range(-self.grid_size, self.grid_size + 1):
            grid.add(
                Line(
                    LEFT * self.grid_size, RIGHT * self.grid_size, stroke_opacity=0.5
                ).shift(UP * i)
            )

        self.add(grid)

        # Add the axes.
        z_radius = self.grid_size * 0.55
        self.add(
            Line(LEFT * self.grid_size, RIGHT * self.grid_size),
            Line(UP * self.grid_size, DOWN * self.grid_size),
            Line(IN * z_radius, OUT * z_radius),
        )

        def look_at_camera(mob):
            tutorial_utils.look_at(mob, self.camera.get_position(), looking_axis="z")

        # Add axis labels.
        x_label_group = VGroup()
        x_label_group.model_matrix = opengl.translation_matrix(
            x=self.grid_size + 0.3
        ) @ opengl.scale_matrix(1.2)

        y_label_group = VGroup()
        y_label_group.model_matrix = opengl.translation_matrix(
            y=self.grid_size + 0.3
        ) @ opengl.scale_matrix(1.2)

        z_label_group = VGroup()
        z_label_group.model_matrix = opengl.translation_matrix(
            z=z_radius + 0.3
        ) @ opengl.scale_matrix(1.2)

        x_label = MathTex("x")
        y_label = MathTex("y")
        z_label = MathTex("z")

        x_label_group.add(x_label, update_parent=True)
        y_label_group.add(y_label, update_parent=True)
        z_label_group.add(z_label, update_parent=True)

        self.add_updater(lambda dt: look_at_camera(x_label))
        self.add_updater(lambda dt: look_at_camera(y_label))
        self.add_updater(lambda dt: look_at_camera(z_label))

        self.add(x_label)
        self.add(y_label)
        self.add(z_label)

        shader = Shader(self.renderer.context, name="default")
        shader.set_uniform("u_color", (1.0, 0.0, 0.0, 1.0))
        attributes = np.zeros(3, dtype=[("in_vert", np.float32, (3,))])
        attributes["in_vert"] = np.array(
            [
                [-1, -1, 0],
                [-1, 1, 0],
                [1, 1, 0],
            ]
        )
        mesh = Mesh(shader, attributes)
        self.add(mesh)

        camera_cone = tutorial_utils.get_three_mesh(
            self.renderer.context,
            geometry_config={
                "name": "ConeGeometry",
                "radius": 0.5,
                "height": 0.6,
                "radial_segments": 40,
            },
            material_config={"name": "StandardMaterial"},
        )
        camera_cone.model_matrix = (
            opengl.translation_matrix(z=-0.15)
            @ opengl.rotation_matrix(x=PI / 2)
            @ camera_cone.model_matrix
        )

        camera_body = tutorial_utils.get_three_mesh(
            self.renderer.context,
            geometry_config={"name": "BoxGeometry"},
            material_config={"name": "StandardMaterial"},
        )
        camera_body.model_matrix = (
            opengl.translation_matrix(z=0.5) @ camera_cone.model_matrix
        )
        camera_mesh = Object3D(
            camera_body,
            camera_cone,
        )
        camera_mesh.model_matrix = (
            opengl.scale_matrix(scale_factor=0.7) @ camera_mesh.model_matrix
        )
        self.camera_indicator = camera_mesh
        self.add(self.camera_indicator)

        self.point_lights.append(
            {
                "position": [0, 0, 0],
                "color": [5, 5, 5],
                "distance": 100,
                "decay": 1,
            }
        )
        self.ambient_light = {
            "color": BLUE_B,
            "intensity": 0.5,
        }

        self.camera_rotation_speed = 0.002
        self.pause_camera_rotation = False

        def update_rotating_camera(dt):
            if self.pause_camera_rotation:
                return
            nonlocal rotating_camera
            r, theta, phi = space_ops.cartesian_to_spherical(
                rotating_camera.get_position()
            )
            rotating_camera.set_position(
                space_ops.spherical_to_cartesian(
                    r, theta, phi + self.camera_rotation_speed
                )
            )
            tutorial_utils.look_at(rotating_camera, ORIGIN)

            self.camera_indicator.set_position(rotating_camera.get_position())
            tutorial_utils.look_at(self.camera_indicator, ORIGIN)

        self.add_updater(update_rotating_camera)

        def update_camera_indicator(dt):
            self.camera_indicator.set_position(rotating_camera.get_position())
            tutorial_utils.look_at(self.camera_indicator, ORIGIN)

        self.add_updater(update_camera_indicator)

        rotating_camera = self.camera
        self.camera.maximum_polar_angle = PI / 2
        self.camera.minimum_polar_angle = 0.0001
        self.camera.set_position(space_ops.spherical_to_cartesian(11, PI / 4, -PI / 2))
        tutorial_utils.look_at(self.camera, ORIGIN)
        self.camera.default_model_matrix = self.camera.model_matrix

        stationary_camera = OpenGLCamera()
        stationary_camera.maximum_polar_angle = PI / 2
        stationary_camera.minimum_polar_angle = 0.0001
        stationary_camera.set_position(
            space_ops.spherical_to_cartesian(30, PI / 3, -3 * PI / 4)
        )
        tutorial_utils.look_at(stationary_camera, ORIGIN)
        stationary_camera.default_model_matrix = stationary_camera.model_matrix

        # self.renderer.camera = stationary_camera
        self.renderer.camera = rotating_camera

        def switch_camera():
            if self.renderer.camera is rotating_camera:
                self.renderer.camera = stationary_camera
            else:
                self.renderer.camera = rotating_camera

        self.set_key_function(" ", switch_camera)

        camera_frame = VGroup()
        camera_frame.model_matrix = opengl.translation_matrix(
            z=-2
        ) @ opengl.scale_matrix(scale_factor=1 / 6)
        rotating_camera.add(camera_frame, update_parent=True)

        shader_code = Text(
            """
        // Vertex Shader
        in vec3 in_vert;
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        void main() {
            gl_Position = projection * view * model * vec4(in_vert, 1.0);
        }
        

        // Fragment Shader
        uniform vec4 u_color;
        out vec4 frag_color;
        
        void main() {
          frag_color = u_color;
        }
        """,
            font="monospace",
            t2c={"[117:121]": BLUE, "[122:127]": RED},
        )
        shader_code.model_matrix = (
            opengl.translation_matrix(x=-3.0, y=2.0)
            @ opengl.scale_matrix(scale_factor=0.3)
            @ shader_code.model_matrix
        )
        camera_frame.add(shader_code, update_parent=True)
        self.add(shader_code)

        projection_matrix = DecimalMatrix(
            np.linalg.inv(self.camera.model_matrix),
            element_to_mobject_config={"edge_to_fix": RIGHT, "num_decimal_places": 1},
        )
        projection_matrix.model_matrix = (
            opengl.scale_matrix(scale_factor=0.5) @ projection_matrix.model_matrix
        )

        decimal_number_cache = collections.defaultdict(list)

        def update_matrix(mob, matrix, color):
            nonlocal decimal_number_cache
            used_numbers = collections.defaultdict(int)
            for i in range(4):
                for j in range(4):
                    old_mob = mob.elements[4 * i + j]
                    number = matrix[i][j]
                    rounded_number = round(number, 1)
                    if round(old_mob.number, 1) == rounded_number:
                        continue
                    full_config = {}
                    full_config.update(old_mob.initial_config)
                    full_config.update(config)
                    cache_list = decimal_number_cache[rounded_number]
                    cache_list_index = used_numbers[rounded_number]
                    if len(cache_list) > cache_list_index:
                        new_decimal = cache_list[cache_list_index]
                    else:
                        new_decimal = DecimalNumber(number, **full_config)
                        decimal_number_cache[rounded_number].append(new_decimal)
                    used_numbers[rounded_number] += 1
                    new_decimal.scale(old_mob[-1].height / new_decimal[-1].height)

                    new_decimal.move_to(old_mob, old_mob.edge_to_fix)
                    old_mob.become(new_decimal)

                    old_mob.number = number
            brackets = mob.brackets
            mob.remove(*mob.brackets)
            brackets[0].next_to(mob, LEFT, mob.bracket_h_buff)
            brackets[1].next_to(mob, RIGHT, mob.bracket_h_buff)
            mob.brackets = VGroup(*brackets)
            mob.add(*brackets)
            mob.set_style(fill_color=color)

        projection_matrix.add_updater(
            lambda mob: update_matrix(
                mob, np.linalg.inv(self.camera.model_matrix), BLUE
            )
        )

        view_label = Text("View Matrix =", fill_color=BLUE)
        view_label.model_matrix = (
            opengl.translation_matrix(x=-2.7)
            @ opengl.scale_matrix(scale_factor=0.5)
            @ view_label.model_matrix
        )

        view_matrix_obj = VGroup()
        view_matrix_obj.add(projection_matrix, update_parent=True)
        view_matrix_obj.add(view_label, update_parent=True)

        view_matrix_obj.model_matrix = (
            opengl.translation_matrix(x=-3, y=-1) @ view_matrix_obj.model_matrix
        )

        camera_frame.add(view_matrix_obj, update_parent=True)
        self.add(view_matrix_obj)

        camera_button = tutorial_utils.get_button(self, "Pause Camera")
        camera_button.model_matrix = (
            opengl.translation_matrix(x=2, y=-2)
            @ opengl.scale_matrix(scale_factor=0.7)
            @ camera_button.model_matrix
        )
        camera_frame.add(camera_button, update_parent=True)

        def mouse_over_button(button):
            if tutorial_utils.mouse_over_camera_frame_mob(self, button):
                button.set_style(stroke_color=YELLOW, fill_color=YELLOW)
            else:
                button.set_style(stroke_color=WHITE, fill_color=WHITE)

        self.add_updater(lambda dt: mouse_over_button(camera_button))

        def click_camera_button():
            if tutorial_utils.mouse_over_camera_frame_mob(self, camera_button):
                self.pause_camera_rotation = not self.pause_camera_rotation

        self.mouse_press_callbacks.append(click_camera_button)

        self.model_rotation_speed = 0.012
        self.pause_model_rotation = False

        def rotate_triangle(dt):
            if self.pause_model_rotation:
                return
            mesh.model_matrix = (
                opengl.x_rotation_matrix(x=self.model_rotation_speed)
                @ mesh.model_matrix
            )

        self.add_updater(rotate_triangle)

        model_matrix = DecimalMatrix(
            np.linalg.inv(mesh.model_matrix),
            element_to_mobject_config={"edge_to_fix": RIGHT, "num_decimal_places": 1},
        )
        model_matrix.model_matrix = (
            opengl.scale_matrix(scale_factor=0.5) @ model_matrix.model_matrix
        )
        model_matrix.add_updater(lambda mob: update_matrix(mob, mesh.model_matrix, RED))

        model_matrix_obj = VGroup()
        model_matrix_obj.add(model_matrix, update_parent=True)

        model_label = Text("Model Matrix =", fill_color=RED)
        model_label.model_matrix = (
            opengl.translation_matrix(x=-2.7)
            @ opengl.scale_matrix(scale_factor=0.5)
            @ model_label.model_matrix
        )
        model_matrix_obj.add(model_label, update_parent=True)

        model_matrix_obj.model_matrix = (
            opengl.translation_matrix(x=-3, y=-3) @ model_matrix_obj.model_matrix
        )

        camera_frame.add(model_matrix_obj, update_parent=True)
        self.add(model_matrix_obj)

        model_button = tutorial_utils.get_button(self, "Pause Model")
        model_button.model_matrix = (
            opengl.translation_matrix(x=2, y=-3)
            @ opengl.scale_matrix(scale_factor=0.7)
            @ model_button.model_matrix
        )
        camera_frame.add(model_button, update_parent=True)
        self.add_updater(lambda dt: mouse_over_button(model_button))

        def click_model_button():
            if tutorial_utils.mouse_over_camera_frame_mob(self, model_button):
                self.pause_model_rotation = not self.pause_model_rotation

        self.mouse_press_callbacks.append(click_model_button)

        self.interactive_embed()
        # self.wait(10)


class BarycentricInterpolation(Scene):
    def construct(self):
        self.renderer.camera = OpenGLCamera(orthographic=True)
        self.skip_animation_preview = True
        # config["background_color"] = "#656565"
        self.triangle_corners = [
            np.array([-4, -3, 0]),
            np.array([5, -3, 0]),
            np.array([0, 1, 0]),
        ]
        self.triangle_corner_label_offsets = [
            np.array([-0.5, 0, 0]),
            np.array([0.5, 0, 0]),
            np.array([-0.5, 0, 0]),
        ]
        self.text_shift = OUT * 0.1
        shader = Shader(
            self.renderer.context,
            source=dict(
                vertex_shader="""
                    #version 330

                    in vec3 position;
                    in vec3 color;
                    out vec3 v_color;
                    uniform mat4 u_view_matrix;
                    uniform mat4 u_projection_matrix;

                    void main() {
                        v_color = color;
                        gl_Position = u_projection_matrix * u_view_matrix * vec4(position, 1);
                    }
                """,
                fragment_shader="""
                    #version 330

                    in vec3 v_color;
                    out vec4 frag_color;

                    void main() {
                      frag_color = vec4(v_color, 1);
                    }
                """,
            ),
        )
        attributes = np.zeros(
            3,
            dtype=[
                ("position", np.float32, (3,)),
                ("color", np.float32, (3,)),
            ],
        )
        attributes["position"] = np.array(self.triangle_corners)
        attributes["color"] = np.array(
            [
                [2, 0, 0],
                [0, 2, 0],
                [0, 0, 2],
            ]
        )
        mesh = Mesh(attributes=attributes, shader=shader)
        self.add(mesh)

        vertex_dots = VGroup(
            *[
                Dot(stroke_width=2.5, depth_test=True)
                .move_to(point)
                .shift(self.text_shift)
                for point in self.triangle_corners
            ]
        )
        for dot, color in zip(vertex_dots, np.array([2 * RIGHT, 2 * UP, 2 * OUT])):
            dot.data["fill_rgba"] = np.array([np.hstack((color, 1))])

        self.fragment_location = 1.5 * DOWN + LEFT
        vertex_fragment_lines = VGroup(
            *[
                Line(point, self.fragment_location, depth_test=True).shift(
                    self.text_shift
                )
                for point in self.triangle_corners
            ]
        )

        fragment_variables = VGroup(
            *[
                Tex(f"$f_{i+1}$", depth_test=True).shift(
                    self.triangle_corners[i]
                    + self.triangle_corner_label_offsets[i]
                    + self.text_shift
                )
                for i in range(3)
            ],
        )

        interpolated_fragment = (
            Tex("$f$", stroke_width=2.5, depth_test=True)
            .move_to(self.fragment_location)
            .shift(0.25 * RIGHT + 0.2 * UP + self.text_shift)
        )
        interpolated_dot = (
            Dot(stroke_width=2.5, depth_test=True)
            .move_to(self.fragment_location)
            .shift(self.text_shift)
        )

        # Draw lines.
        self.play(
            FadeIn(vertex_dots),
            Create(vertex_fragment_lines),
            Write(fragment_variables),
            Write(interpolated_fragment),
            FadeIn(interpolated_dot),
        )
        self.interactive_embed()

        self.triangle_label_locations = [
            RIGHT * 1 + UP * -1,
            RIGHT * -1.5 + UP * -1,
            RIGHT * -0.5 + UP * -2.5,
        ]
        triangle_labels = VGroup(
            *[
                Tex(f"$A_{i+1}$", depth_test=True).shift(
                    self.triangle_label_locations[i] + self.text_shift
                )
                for i in range(3)
            ],
        )
        self.play(Write(triangle_labels))
        self.interactive_embed()

        def update_mesh(mesh, dt):
            mesh.attributes["position"][:, 0] -= 1.8 * dt

        mesh.add_updater(update_mesh)
        self.play(
            VGroup(
                vertex_fragment_lines,
                vertex_dots,
                triangle_labels,
                fragment_variables,
                interpolated_dot,
                interpolated_fragment,
            ).animate.shift(1.8 * LEFT),
            rate_func=linear,
        )
        self.triangle_corners += 1.8 * LEFT
        self.fragment_location += 1.8 * LEFT
        mesh.clear_updaters()

        lambda_definition = (
            Tex("$\lambda_i = \\frac{A_i}{A_1+A_2+A_3}$", depth_test=True)
            .scale(1.2)
            .shift(RIGHT * 3.5 + self.text_shift)
        )
        self.play(Write(lambda_definition))

        barycentric_interpolation_description = Tex(
            "The Barycentric interpolation\\\\$f$ of a fragment $p$ is given by\\\\$f=\lambda_1f_1+\lambda_2f_2+\lambda_3f_3$"
        ).to_edge(UP)
        self.play(Write(barycentric_interpolation_description))

        def point_inside_triangle(point):
            triangle_vectors = np.array(
                [
                    self.triangle_corners[1] - self.triangle_corners[0],
                    self.triangle_corners[2] - self.triangle_corners[1],
                    self.triangle_corners[0] - self.triangle_corners[2],
                ]
            )
            point_vectors = np.array(
                [
                    point - self.triangle_corners[0],
                    point - self.triangle_corners[1],
                    point - self.triangle_corners[2],
                ]
            )
            crosses = np.cross(triangle_vectors, point_vectors)
            return np.all(crosses[:, 2] > 0)

        def triangle_area(p0, p1, p2):
            vectors = np.array([p1 - p0, p2 - p1, p0 - p2])
            norms = np.linalg.norm(vectors, axis=1)
            s = 0.5 * np.sum(norms)
            return np.sqrt(s * (s - norms[0]) * (s - norms[1]) * (s - norms[2]))

        def update_color(dt):
            mouse_point = self.mouse_point.get_center()
            if point_inside_triangle(mouse_point):
                update_triangle_mobjects(mouse_point)

        def update_triangle_mobjects(point):
            for i, line in enumerate(vertex_fragment_lines):
                line.put_start_and_end_on(point, self.triangle_corners[i])
                line.shift(self.text_shift)
            interpolated_dot.move_to(point + self.text_shift)
            interpolated_fragment.move_to(
                point + 0.25 * LEFT + 0.27 * UP + self.text_shift
            )
            triangle_areas = []
            for i, label in enumerate(triangle_labels):
                triangle_points = np.array(
                    [
                        point,
                        self.triangle_corners[(i + 1) % 3],
                        self.triangle_corners[(i + 2) % 3],
                    ],
                )
                location = np.sum(triangle_points, axis=0) / 3
                label.move_to(location + self.text_shift)
                triangle_areas.append(triangle_area(*triangle_points))

            total_triangle_area = np.sum(triangle_areas)
            lambdas = np.array([area / total_triangle_area for area in triangle_areas])
            colors = np.array([2 * RIGHT, 2 * UP, 2 * OUT])
            fragment_color_vec = np.sum(lambdas * colors, axis=0)
            interpolated_dot.data["fill_rgba"] = np.array(
                [np.hstack((fragment_color_vec, 1))]
            )
            interpolated_fragment[0][0].data["fill_rgba"] = np.array(
                [np.hstack((fragment_color_vec, 1))]
            )
            barycentric_interpolation_description[0][49].data["fill_rgba"] = np.array(
                [np.hstack((fragment_color_vec, 1))]
            )

        update_triangle_mobjects(self.fragment_location)
        barycentric_interpolation_description[0][53].data["fill_rgba"] = np.array(
            [[1, 0, 0, 1]]
        )
        barycentric_interpolation_description[0][54].data["fill_rgba"] = np.array(
            [[1, 0, 0, 1]]
        )
        barycentric_interpolation_description[0][58].data["fill_rgba"] = np.array(
            [[0, 1, 0, 1]]
        )
        barycentric_interpolation_description[0][59].data["fill_rgba"] = np.array(
            [[0, 1, 0, 1]]
        )
        barycentric_interpolation_description[0][63].data["fill_rgba"] = np.array(
            [[0, 0, 1, 1]]
        )
        barycentric_interpolation_description[0][64].data["fill_rgba"] = np.array(
            [[0, 0, 1, 1]]
        )
        for fragment_variable, color in zip(
            fragment_variables, np.array([2 * RIGHT, 2 * UP, 2 * OUT])
        ):
            for child in fragment_variable[0]:
                child.data["fill_rgba"] = np.array([np.hstack((color, 1))])

        self.add_updater(update_color)
        self.skip_animation_preview = False

        self.interactive_embed()


class HierarchicalModelMatrices(Scene):
    def construct(self):
        self.point_lights.append(
            {
                "position": [0, 0, 0],
                "color": [7, 7, 1],
                "distance": 100,
                "decay": 1,
            }
        )
        self.ambient_light = {
            "color": BLUE_B,
            "intensity": 0.5,
        }

        sun = tutorial_utils.get_three_mesh(
            self.renderer.context,
            geometry_config={
                "name": "SphereGeometry",
                "width_segments": 18,
                "height_segments": 18,
            },
            material_config={"name": "StandardMaterial", "emissive": (1, 1, 0)},
        )
        self.add(sun)

        earth = tutorial_utils.get_three_mesh(
            self.renderer.context,
            geometry_config={
                "name": "SphereGeometry",
                "width_segments": 18,
                "height_segments": 18,
            },
            material_config={"name": "PhongMaterial", "diffuse": (0.3, 0.3, 1)},
        )
        earth.model_matrix = (
            opengl.translation_matrix(x=5)
            @ opengl.scale_matrix(0.5)
            @ earth.model_matrix
        )
        sun.add(earth)

        moon = tutorial_utils.get_three_mesh(
            self.renderer.context,
            geometry_config={
                "name": "SphereGeometry",
                "width_segments": 18,
                "height_segments": 18,
            },
            material_config={"name": "PhongMaterial", "diffuse": (0.3, 0.3, 1)},
        )
        moon.model_matrix = (
            opengl.translation_matrix(x=3)
            @ opengl.scale_matrix(0.3)
            @ moon.model_matrix
        )
        earth.add(moon)

        def update_sun(mob, dt):
            sun.model_matrix = opengl.z_rotation_matrix(z=0.01) @ sun.model_matrix
            sun.normal_matrix = opengl.z_rotation_matrix(z=0.01) @ sun.normal_matrix

        sun.add_updater(update_sun)

        def update_earth(mob, dt):
            rotation_about_axis = (
                opengl.translation_matrix(x=5)
                @ opengl.z_rotation_matrix(z=0.05)
                @ opengl.translation_matrix(x=-5)
            )
            earth.model_matrix = rotation_about_axis @ earth.model_matrix
            earth.normal_matrix = rotation_about_axis @ earth.normal_matrix

        earth.add_updater(update_earth)

        self.interactive_embed()


class ThreeDLogo(Scene):
    def construct(self):
        config["background_color"] = "#ece6e2"
        self.renderer.camera = OpenGLCamera(orthographic=True)
        self.point_lights.append(
            {
                "position": [12, -12, 12],
                "color": [5, 5, 5],
                "distance": 100,
                "decay": 5,
            }
        )
        self.ambient_light = {
            "color": WHITE,
            "intensity": 0.5,
        }

        letter = MathTex("\\mathbb{M}").scale_to_fit_height(3)

        subpaths = letter[0][0].get_subpaths()
        num_points = 0
        path_indices = []
        for path in subpaths:
            path_indices.append(num_points)
            num_points += len(path)
        points = np.empty((num_points, 3))

        i = 0
        for path in subpaths:
            points[i : i + path.shape[0]] = path
            i += path.shape[0]

        extrude = tutorial_utils.get_three_mesh(
            self.renderer.context,
            geometry_config={
                "name": "ExtrudeGeometry",
                "points": points.ravel(),
                "path_indices": path_indices,
                "depth": 0.7,
            },
            material_config={
                "name": "PhongMaterial",
                "diffuse": (0.09, 0.09, 0.09),
            },
        )
        extrude.model_matrix = opengl.translation_matrix(x=-1) @ extrude.model_matrix

        circle_diffuse = np.array([95, 165, 95]) / 255
        square_diffuse = np.array([55, 55, 125]) / 255
        triangle_diffuse = np.array([180, 80, 30]) / 255

        circle = tutorial_utils.get_three_mesh(
            self.renderer.context,
            geometry_config={
                "name": "SphereGeometry",
                "width_segments": 30,
                "height_segments": 30,
            },
            material_config={"name": "StandardMaterial", "diffuse": circle_diffuse},
        )
        circle.model_matrix = (
            opengl.translation_matrix(x=0.5, y=-2, z=-1.35)
            @ opengl.scale_matrix(scale_factor=1.25)
            @ circle.model_matrix
        )

        square = tutorial_utils.get_three_mesh(
            self.renderer.context,
            geometry_config={
                "name": "BoxGeometry",
            },
            material_config={"name": "StandardMaterial", "diffuse": square_diffuse},
        )
        square.model_matrix = (
            opengl.translation_matrix(x=1.7, y=-0.8, z=-4)
            @ opengl.scale_matrix(scale_factor=2.4)
            @ square.model_matrix
        )

        triangle = tutorial_utils.get_three_mesh(
            self.renderer.context,
            geometry_config={
                "name": "ConeGeometry",
                "height": 0.75,
                "radius": 0.45,
                "radial_segments": 60,
            },
            material_config={"name": "StandardMaterial", "diffuse": triangle_diffuse},
        )
        triangle.model_matrix = (
            opengl.translation_matrix(x=2.9, y=-1.7, z=-6.2)
            @ opengl.scale_matrix(scale_factor=2.4)
            @ triangle.model_matrix
        )

        # # Circle updaters.
        # def circle_callback(sender, _):
        #     nonlocal circle_diffuse
        #     circle_diffuse = tuple(np.array(dearpygui.core.get_value(sender)[:3]) / 255)

        # def update_circle(mesh):
        #     mesh.shader.set_uniform("diffuse", circle_diffuse)

        # circle.add_updater(update_circle)

        # # Square updaters.
        # def square_callback(sender, _):
        #     nonlocal square_diffuse
        #     square_diffuse = tuple(np.array(dearpygui.core.get_value(sender)[:3]) / 255)

        # def update_square(mesh):
        #     mesh.shader.set_uniform("diffuse", square_diffuse)

        # square.add_updater(update_square)

        # # Triangle updaters.
        # def triangle_callback(sender, _):
        #     nonlocal triangle_diffuse
        #     triangle_diffuse = tuple(
        #         np.array(dearpygui.core.get_value(sender)[:3]) / 255
        #     )

        # def update_triangle(mesh):
        #     mesh.shader.set_uniform("diffuse", triangle_diffuse)

        # triangle.add_updater(update_triangle)

        # self.widgets.extend(
        #     [
        #         {
        #             "name": "Circle Color",
        #             "widget": "color_edit3",
        #             "callback": circle_callback,
        #             "default_value": (0.3 * 255, 1 * 255, 0.3 * 255, 1 * 255),
        #         },
        #         {
        #             "name": "Square Color",
        #             "widget": "color_edit3",
        #             "callback": square_callback,
        #             "default_value": (0.3 * 255, 0.3 * 255, 1 * 255, 1 * 255),
        #         },
        #         {
        #             "name": "Triangle Color",
        #             "widget": "color_edit3",
        #             "callback": triangle_callback,
        #             "default_value": (1 * 255, 0.5 * 255, 0.0 * 255, 1 * 255),
        #         },
        #     ]
        # )

        logo = Object3D()
        logo.add(extrude)
        logo.add(circle)
        logo.add(square)
        logo.add(triangle)
        logo.model_matrix = (
            opengl.translation_matrix(y=-2.5)
            @ opengl.x_rotation_matrix(x=PI / 2)
            @ logo.model_matrix
        )
        self.add(logo)

        self.camera.model_matrix = (
            opengl.x_rotation_matrix(PI / 2) @ self.camera.model_matrix
        )
        self.camera.default_model_matrix = self.camera.model_matrix

        camera_to_light = np.array([12, -12, 12]) - self.camera.get_position()

        def update_rotating_camera(dt):
            r, theta, phi = space_ops.cartesian_to_spherical(self.camera.get_position())
            self.camera.set_position(
                space_ops.spherical_to_cartesian(r, theta, phi + (1 / 8) * 2 * PI / 60)
            )
            self.point_lights[0]["position"] = list(
                self.camera.get_position() + camera_to_light
            )

            tutorial_utils.look_at(self.camera, ORIGIN)

        self.add_updater(update_rotating_camera)

        self.interactive_embed()
        # self.wait(16)
