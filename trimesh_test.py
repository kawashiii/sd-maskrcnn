import numpy as np
import trimesh
import pyrender
import cv2 as cv

trimesh.util.attach_to_log()

# Scene Initialization
scene = pyrender.Scene()

# Load plane
plane_filename = "./test_model/plane.obj"
plane_trimesh = trimesh.load_mesh(plane_filename)
plane_texture =  cv.cvtColor(cv.imread('./test_model/plane.jpg'), cv.COLOR_BGR2RGB)
plane_texture = pyrender.Texture(source=plane_texture, source_channels='RGB')
plane_material = pyrender.material.MetallicRoughnessMaterial(baseColorTexture=plane_texture, wireframe=True)
plane_pyrender_mesh = pyrender.Mesh.from_trimesh(plane_trimesh, material=plane_material)
scene.add(plane_pyrender_mesh)

# Load bin
bin_filename = "./test_model/bin.obj"
bin_trimesh = trimesh.load_mesh(bin_filename)
bin_texture =  cv.cvtColor(cv.imread('./test_model/bin.jpg'), cv.COLOR_BGR2RGB)
bin_texture = pyrender.Texture(source=bin_texture, source_channels='RGB')
bin_material = pyrender.material.MetallicRoughnessMaterial(baseColorTexture=bin_texture, wireframe=True)
bin_pyrender_mesh = pyrender.Mesh.from_trimesh(bin_trimesh, material=bin_material)
scene.add(bin_pyrender_mesh)

# View Scene
# pyrender.Viewer(scene, use_raymond_lighting=True)
pyrender.Viewer(scene)
