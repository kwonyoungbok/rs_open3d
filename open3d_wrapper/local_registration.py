import numpy as np
import copy
import open3d as o3d
import time 


class LocalRegistration:

    _trans_init = np.asarray([[ -0.45998067, -0.27524449,  0.84419089,  0.31921783],
                              [-0.21835325,  0.95661005,  0.19292244,  0.05974049],
                              [-0.86066232, -0.09559123, -0.50012266, -0.71095326],
                              [ 0,          0,          0,          1,        ]])

    def __init__(self):
        pass
    
 
    def get_icp_p2p(self,source,target,threshold=0.02,trans_init=_trans_init):
        """
        retrun:
            - reg_p2p 
            - transformation = 이동행렬
        """
        reg_p2p = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=2000)
        )
        return reg_p2p , reg_p2p.transformation 
    
    def get_icp_p2l(self,source,target,threshold=0.02,trans_init=_trans_init):
          sigma = 0.1  # mean and standard deviation
          loss = o3d.pipelines.registration.TukeyLoss(k=sigma)
          p2l = o3d.pipelines.registration.TransformationEstimationPointToPlane(loss)

          reg_p2l = o3d.pipelines.registration.registration_icp(
          source, target, threshold, trans_init,p2l)
         # o3d.pipelines.registration.TransformationEstimationPointToPlane())
          return reg_p2l , reg_p2l.transformation

    
    def __pick_points(self,pcd):
        print("")
        print(
        "1) Please pick at least three correspondences using [shift + left click]"
        )
        print("   Press [shift + right click] to undo point picking")
        print("2) After picking points, press 'Q' to close the window")
        vis = o3d.visualization.VisualizerWithEditing()
        vis.create_window()
        vis.add_geometry(pcd)
        vis.run()  # user picks points
        vis.destroy_window()
        print("")
        return vis.get_picked_points()


    def manual_registration(self,source, target):
        picked_id_source = self.__pick_points(source)
        picked_id_target = self.__pick_points(target)
        assert (len(picked_id_source) >= 3 and len(picked_id_target) >= 3)
        assert (len(picked_id_source) == len(picked_id_target))
        corr = np.zeros((len(picked_id_source), 2))
        corr[:, 0] = picked_id_source
        corr[:, 1] = picked_id_target
        p2p = o3d.pipelines.registration.TransformationEstimationPointToPoint()
        trans_init = p2p.compute_transformation(source, target,
                                        o3d.utility.Vector2iVector(corr))
        return p2p, trans_init






"""
[[ 0.01853959 -0.22487553  0.97421111  0.434891  ]
 [ 0.26626846  0.94030061  0.21198084  0.10834739]
 [-0.9637206   0.25547165  0.07731005 -0.48069104]
 [ 0.          0.          0.          1.        ]]
"""
        
