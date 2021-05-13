import numpy as np
import copy
import open3d as o3d
import time 


class LocalRegistration:

    _trans_init = np.asarray([[ 0.99589865,  0.04557182, -0.0795458,  -0.10749126],
                              [-0.01708884,  0.99973791, -0.00392333, -0.00551725],
                              [0.06534958,  0.0050876,   0.99784857, -0.00213089],
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
    



        
