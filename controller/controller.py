import abc

from realsense.device_factory import DeviceFactory
from open3d_wrapper.point_cloud_data  import PointCloudData

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

    def start(self):
        self._multi_device.enable_all_devices()
    
    def capture(self):
       frameset_wrapper_dic = self._multi_device.poll_for_frames_all_devices()
       depth_scale = self._multi_device.get_depth_scale()

       for name,frameset_wrapper in frameset_wrapper_dic.items():
          # frameset_wrapper.align()
           point_cloud_data = PointCloudData(frameset_wrapper,depth_scale)
           point_cloud_data.make_pcd()
           point_cloud_data.save_pcd(name)
      

    
