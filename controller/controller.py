import abc
import open3d as o3d
import time

from realsense.device_factory import DeviceFactory
from open3d_wrapper.point_cloud_data  import PointCloudData
from open3d_wrapper.local_registration import LocalRegistration

class ControllerImp(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def start(self):
        raise NotImplemented

    @abc.abstractmethod
    def capture(self):
        raise NotImplemented


class Controller(ControllerImp):
    def __init__(self):
        self._multi_device = DeviceFactory.createMultiDevice()
        self._localRegistration= LocalRegistration()


    def start(self):
        self._multi_device.enable_all_devices()
    
    def capture(self):
       mk_pcd_time = time.time()
       frameset_wrapper_dic = self._multi_device.poll_for_frames_all_devices()
       depth_scale = self._multi_device.get_depth_scale()

       pcd_list =[]
       for _,frameset_wrapper in frameset_wrapper_dic.items():
          # frameset_wrapper.align()
           point_cloud_data = PointCloudData(frameset_wrapper,depth_scale)
           point_cloud_data.make_pcd()
           pcd_list.append(point_cloud_data)
       print("pcd 생성 완료: ", time.time()-mk_pcd_time)
        
       regi_time = time.time()
       #_ ,tranformation_matrix=self._localRegistration.get_icp_p2p(pcd_list[0].get_pcd(),pcd_list[1].get_pcd())
      # _,tranformation_matrix = self._localRegistration.manual_registration(pcd_list[0].get_pcd(),pcd_list[1].get_pcd())
      # print("registration 시간: ",time.time()-regi_time , " m: " ,tranformation_matrix)

       o3d.visualization.draw_geometries([pcd_list[0].get_pcd()])
       o3d.visualization.draw_geometries([pcd_list[1].get_pcd()])
       o3d.visualization.draw_geometries([pcd_list[2].get_pcd()])
       o3d.visualization.draw_geometries([pcd_list[3].get_pcd()])

    #    source_pcd = pcd_list[0].transform(tranformation_matrix)
    #    target_pcd = pcd_list[1].get_pcd()
    #    o3d.visualization.draw_geometries([source_pcd, target_pcd])



      

    
