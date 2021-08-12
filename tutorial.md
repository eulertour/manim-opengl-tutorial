* OpenGL pipeline
* HalfScreenTriangle
* Projection matrix
* Model matrix
* View matrix
* Barycentric Interpolation
* Hierarchical Model Matrices
* Attributes, varyings, and uniforms
* Fullscreen fragment shader example

# Somewhat beyond manim
* Rendering Geometries
  * Geometries and materials
* Lighting
  * Normal matrices
* Textures
* Putting it together

TODO: Add a FullScreenQuad example.

## Vocabulary
* **Shader** - A shader is a program that runs on a GPU.

* **Homogeneous Coordinates** - The coordinate system that OpenGL draws in is constrained to
  a 2x2x2 cube with the x, y, and z axes ranging from -1 to +1.

* **Normalized Device Coordinates** - The coordinate system that OpenGL draws in is constrained to
  a 2x2x2 cube with the x, y, and z axes ranging from -1 to +1.

* **Fragment** - A pixel-sized piece of a primitive.

* **Frame Buffer** - A collection of buffers that can be used as a target for rendering.

* **Geometry** - A list of vertices representing the shape of an object.

* **Material** - A collection of shaders representing the way the object's physical
  properties e.g. color, shininess, opacity.

* **Mesh** - A combination of a geometry and material which represents
  a single drawable entity in OpenGL.

* **Model Space** - A coordinate space which is local to a geometry (v).

* **World Space** - The global coordinate space (M * v).

* **Camera Space** - The camera's model space (V * M * v).

* **Clip Space** - A coordinate system in normalized device coordinates (P * V * M * v).

## OpenGL pipeline
* **Vertices**

  Essentially a list of data points each of which have the same attributes.

* **Vertex Shader**

  Reads in vertices and outputs positional data.

* **Primitives Generation**

  Convert vertex positions into one of a few different primitives.

* **Rasterization**

  Convert each primitive into fragments (pixel-sized parts).

* **Fragment Shader**

  Determine color and opacity for each fragment.

* **Blending**

  Determine colors for each pixel by combining fragment data.

* **Frame Buffer**

  Pixel data is written to a frame buffer and rendered to the screen.

* **Affine Transformation**

  An affine transformation is a transformation that preserves lines
  and parallelism (but not necessarily distances and angles).

## Using Manim to render a triangle with OpenGL
```py
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
```

Let's walk through the shader used above, starting with the vertices.
```py
attributes = np.zeros(3, dtype=[("position", np.float32, (3,))])
attributes["position"] = np.array(
    [
        [-1, -1, 0],
        [-1, 1, 0],
        [1, 1, 0],
    ]
)
```
These lines specify the data format for each vertex. The vertices
in this shader have a single attribute specifying their position.

```
vertex_shader="""
    #version 330
    in vec3 position;
    void main() {
        gl_Position = vec4(position, 1);
    }
"""
```

This vertex shader simply outputs the homogeneous equivalent of
the point that was passed to it. <!--insert brief elaboration on
homogeneous coordinates here.-->

After the vertex shader runs, the data it outputs is used to draw
triangles, the most common type of primitive.

These triangles are rasterized into fragments which are then
colored by the fragment shader.

```
fragment_shader="""
    #version 330
    out vec4 frag_color;
    void main() {
        frag_color = vec4(1, 0, 0, 1);
    }
"""
```
This fragment shader colors each fragment red by filling the r, g, b, and a channels of
each fragment with 1, 0, 0, and 1, respectively. This is output as a vector passed to
the frag_color variable.

The fragment data from the fragment shader is then blended in
order to determine the color of each pixel and written to the
frame buffer.

## Normalized Device Coordinates

The coordinate system that OpenGL draws in is constrained to
a 2x2x2 cube with the x, y, and z axes ranging from -1 to +1.

## Projection Matrix

Since we generally don't think of scenes in terms of normalized device
coordinates, we'll need a way to convert points in our preferred
coordinate space to their equivalents in normalized device coordinates.
Since this requires mapping points in your preferred
coordinate space into the 2x2x2 cube centered at the origin,
the x, y, and z coordinates will have to scaled
by factors of 2 / w, 2 / h, and 2 / d, respectively,
where w, h, and d represent the width, height, and depth of
your preferred coordinate space, respectively.
This is done by transforming them with what's called a
projection matrix.

```py
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
```

## Model Matrix
If we associate each mesh with a transformation matrix and
transform it with that matrix before rendering we can use
linear algebra to perform any affine transformation on our
meshes.

If we were to use a traditional 3x3 transformation matrix as
a model matrix it wouldn't be possible to encode translations.
However, homogeneous transformation matrices allow us to
encode translations, rotations, scales, and shears within
model matrices.

This gives us a powerful tool to transform any mesh using the
same method.

```py
vertex_shader="""
    #version 330

    uniform mat4 projection;
    uniform mat4 model;
    in vec4 position;

    void main() {
        gl_Position = projection * model * position;
    }
"""
```
This vertex shader takes a projection and model matrix and
uses them to transform each point prior to outputting them.

## Homogeneous Coordinates
Homogeneous coordinates offer a way of representing 3D
coordinates as 4 dimensional vectors. As a rule of
thumb, points represented with homogeneous coordinates
should have 1 as their w coordinate and vectors
represented with homogeneous coordinates should have
0 as their w coordinate. More information is at
https://www.tomdalling.com/blog/modern-opengl/explaining-homogenous-coordinates-and-projective-geometry/.

## View Matrix
The view matrix encodes the position of our world's camera.
Since any affine transformation to the camera is equivalent
to the opposite transformation on each object in the scene,
the view matrix is the inverse of the camera's model matrix.

## Projection Matrix Revisited
When we went over projected matrices before, we only used them
to scale objects. However, more sophisticated projection
matrices can be used to incorporate perspective in a scene.

There is a lot of theory one could go into regarding this, but
for the purposes of this lesson just know that **orthographic** 
projection matrices do not have a concept of perspective, while
**perspective** projection matrices do.

More information is at https://jsantell.com/3d-projection/.

## Barycentric Interpolation
OpenGL determines the inputs to the fragment shader for each
fragment by interpolating vertex data. OpenGL uses Barycentric
interpolation to determine these values.

A fragment color f is computed by
f = lambda_1 * f_1 + lambda_2 * f_2 + lambda_3 * f_3
where f_i is the data point being interpolated and
lambda_i is the ratio of the area of the triangle opposite
the vertex in question to the total area of the triangle.

## Hierarchical Model Matrices
Meshes (or empty coordinate spaces) with associated model
matrices can be organized hierarchically to simply positioning.

## Logo
Modeling is never done manually, if you ever need a complex shape
you should find a way to model it in a dedicated program.
