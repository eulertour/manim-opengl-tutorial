#!/usr/bin/env python
"""
This is intended to be run from the tutorial root.
"""

import os

grpc_dir = "_grpc"
CMD_STRING = f"""
python \
    -m grpc_tools.protoc \
    -I {grpc_dir}/proto \
    --python_out={grpc_dir}/gen \
    --grpc_python_out={grpc_dir}/gen \
        {grpc_dir}/proto/threejs.proto
"""
os.system(CMD_STRING)
