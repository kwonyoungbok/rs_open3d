import numpy as np
import copy
import open3d as o3d
import time 

# ICP Registration
def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
#     source_temp.paint_uniform_color([1, 0, 0])
#     target_temp.paint_uniform_color([0, 0, 1])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp])
    

source = o3d.io.read_point_cloud("f0172080.pcd")
target = o3d.io.read_point_cloud("f0270455.pcd")
threshold = 0.02

trans_init = np.asarray([[ 0.95214505, -0.02709928,  0.30444282,  0.04781732],
 [ 0.02477871,  0.99962699,  0.0114841,  -0.00679823],
 [-0.30464047, -0.00339082,  0.95246138,  0.01210747],
 [ 0,          0,          0,          1,        ]])
draw_registration_result(source, target, trans_init)

print("Initial alignment")
evaluation = o3d.pipelines.registration.evaluate_registration(source, target, threshold, trans_init)
print(evaluation)

print("------------------------")
print("Apply point-to-point ICP")
p2p_time = time.time()
reg_p2p = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint())
print(reg_p2p)
print("Transformation is:", time.time()-p2p_time)
print(reg_p2p.transformation)
draw_registration_result(source, target, reg_p2p.transformation)

print("------------------------")
print("Apply point-to-plane ICP")
p2l_time=time.time()
reg_p2l = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
print(reg_p2l)
print("Transformation is:",time.time()-p2l_time)
print(reg_p2l.transformation)
draw_registration_result(source, target, reg_p2l.transformation)


