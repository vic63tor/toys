#!/usr/bin/env python3

import os
from setuptools import setup

directory = os.path.abspath(os.path.dirname(__file__))

setup(name='wechatsuperpower',
    
      description='Give wechat some super powers, for fun',
      author='Bob Zhang',
      packages = ['tinygrad', 'tinygrad.codegen', 'tinygrad.nn', 'tinygrad.runtime', 'tinygrad.shape'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
      ],
      install_requires=['numpy', 'requests', 'pillow', 'tqdm', 'networkx'],
      python_requires='>=3.8',
      extras_require={
        'gpu': ["pyopencl"],
        'llvm': ["llvmlite"],
        'cuda': ["pycuda"],
        'triton': ["triton>=2.0.0.dev20221202"],
        'metal': ["pyobjc-framework-Metal", "pyobjc-framework-Cocoa", "pyobjc-framework-libdispatch"],
        'linting': [
            "flake8",
            "pylint",
            "mypy",
            "pre-commit",
        ],
        'testing': [
            "torch~=1.13.0",
            "pytest",
            "pytest-xdist",
            "onnx~=1.13.0",
            "onnx2torch",
            "opencv-python",
        ],
      },
      include_package_data=True)