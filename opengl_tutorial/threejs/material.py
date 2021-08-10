from manim.renderer.shader import Shader


# Move the #extension directive earlier in the file.
def move_extension_to_start(shader):
    return shader
    # shader_lines = shader.split("\n")
    # extension_line = None
    # for i, line in enumerate(shader_lines):
    #     # if line.startswith("#extension"):
    #     #     extension_line = shader_lines.pop(i)
    #     if "extension" in line:
    #         print(line)
    # new_shader_lines = shader_lines
    # new_shader_lines.insert(1, extension_line)
    # return "\n".join(new_shader_lines)


class Material(Shader):
    def __init__(self, context, vertex_shader, fragment_shader):
        super().__init__(
            context,
            source={
                "vertex_shader": vertex_shader,
                "fragment_shader": fragment_shader,
            },
        )


class BasicMaterial(Material):
    def __init__(self, context, vertex_shader, fragment_shader, config):
        super().__init__(context, vertex_shader, fragment_shader)
        defaults = {
            "diffuse": (1, 1, 1),
            "opacity": 1,
        }
        self.set_uniform("diffuse", tuple(config.get("diffuse", defaults["diffuse"])))
        self.set_uniform("opacity", config.get("opacity", defaults["opacity"]))


class PhongMaterial(Material):
    def __init__(self, context, vertex_shader, fragment_shader, config):
        fragment_shader = move_extension_to_start(fragment_shader)
        super().__init__(context, vertex_shader, fragment_shader)

        defaults = {
            "diffuse": (1, 1, 1),
            "emissive": (0, 0, 0),
            "specular": (1 / 15, 1 / 15, 1 / 15),
            "shininess": 30,
            "opacity": 1,
        }
        self.set_uniform("diffuse", tuple(config.get("diffuse", defaults["diffuse"])))
        self.set_uniform(
            "emissive", tuple(config.get("emissive", defaults["emissive"]))
        )
        self.set_uniform(
            "specular", tuple(config.get("specular", defaults["specular"]))
        )
        self.set_uniform("shininess", config.get("shininess", defaults["shininess"]))
        self.set_uniform("opacity", config.get("opacity", defaults["opacity"]))


class StandardMaterial(Material):
    def __init__(self, context, vertex_shader, fragment_shader, config):
        fragment_shader = move_extension_to_start(fragment_shader)
        super().__init__(context, vertex_shader, fragment_shader)

        defaults = {
            "diffuse": (1, 1, 1),
            "emissive": (0, 0, 0),
            "roughness": 1,
            "metalness": 0,
            "opacity": 1,
        }
        self.set_uniform("diffuse", tuple(config.get("diffuse", defaults["diffuse"])))
        self.set_uniform(
            "emissive", tuple(config.get("emissive", defaults["emissive"]))
        )
        self.set_uniform("roughness", config.get("roughness", defaults["roughness"]))
        self.set_uniform("metalness", config.get("metalness", defaults["metalness"]))
        self.set_uniform("opacity", config.get("opacity", defaults["opacity"]))
