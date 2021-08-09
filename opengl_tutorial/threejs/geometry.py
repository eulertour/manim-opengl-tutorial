import numpy as np


class Geometry:
    def __init__(self, position, normal, index=None):
        num_vertices = len(position) // 3
        dtype = [("position", np.float32, (3,))]
        if len(normal) > 0:
            dtype.append(("normal", np.float32, (3,)))
        self.attributes = np.zeros(
            num_vertices,
            dtype=dtype,
        )
        self.attributes["position"] = np.array(position).reshape((-1, 3))
        if len(normal) > 0:
            self.attributes["normal"] = np.array(normal).reshape((-1, 3))
        self.index = np.array(index)
