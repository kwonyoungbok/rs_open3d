import open3d as o3d
import numpy as np

pcd = o3d.io.read_point_cloud("1620801496.1653326.pcd")
print(pcd)
print(np.asarray(pcd.points))

o3d.visualization.draw_geometries([pcd],
                                  window_name='Test123')