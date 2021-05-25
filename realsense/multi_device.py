import pyrealsense2 as rs
import time 
from os import makedirs
from os.path import exists, join
import shutil
import cv2


from .single_device.device import Device


# 다중 디바이스 관리 객체
class DeviceContext:
    
    def __init__(self, context, pipeline_configuration):
        assert isinstance(context, type(rs.context()))
        assert isinstance(pipeline_configuration, type(rs.config()))
        self._context = context
        self._available_devices = DeviceContext.enumerate_connected_devices(context)
        self._enabled_devices_dic = {}
        self._devices=[]
        self._config = pipeline_configuration
       # self._frame_counter = 0
        self._initialize()

### public method ###########################################################################################################################################
    def enable_all_devices(self):
        len_device = len(self._available_devices)
        if len_device is 0:
            raise RuntimeError("장치가 없습니다.")
            
        print(str(len_device) + " devices have been found")

        for device in self._devices:
            enabled = device.enable_device(self._config)
            if enabled:
                self._enabled_devices_dic[device.get_device_serial()]=device

    
    def poll_for_frames_all_devices(self):
        frames = {}

        enabled_devices_length = len(self._enabled_devices_dic)
        if enabled_devices_length == 0:
            raise RuntimeError("준비된 장치가 0개 입니다.")

        while len(frames) < enabled_devices_length:
           
            for (_,device) in self._enabled_devices_dic.items():
              frame =  device.poll_for_frames()
              if frame is None:
                  continue
              frames[device.get_device_serial()]=frame
        return frames

    def get_depth_scale(self):
         for device in self._devices:
             return device.get_depth_scale()

    def disable_streams(self):
        self._config.disable_all_streams()


    def record_imgs(self, record_index  = 0):
        base_path = '../dataset/realsense'
        make_folder(base_path)

        frames = self.poll_for_frames_all_devices()
        for device_serial_name, frame in frames.items():
            device_path = join(base_path,device_serial_name)
            path_depth = join(device_path, "depth")
            path_color = join(device_path, "color")
            make_folder(path_depth)
            make_folder(path_color)
            
            cv2.imwrite("%s/%s-%06d.png" % \
                        (path_depth,device_serial_name, record_index), frame.get_depth_np())
            cv2.imwrite("%s/%s-%06d.jpg" % \
                        (path_color,device_serial_name, record_index), frame.get_color_np())


        

### private method #######################################################################################################################################################

    def _initialize(self):
        self._create_devices()


    def _create_devices(self):
        for serial  in self._available_devices:
            self._devices.append(Device(serial))


    
### static method ##########################################################################################################################################################

    @staticmethod
    def enumerate_connected_devices(context):
        """ 
        연결된 장치를 열거하는 메서드
         Return:
                connect_device: 연결된 장치 배열
        """
        connect_device = []
        for d in context.devices:
            if d.get_info(rs.camera_info.name).lower() != 'platform camera':
                connect_device.append(d.get_info(rs.camera_info.serial_number))
        return connect_device

    # @staticmethod
    # def post_process_depth_frame(depth_frame, decimation_magnitude=1.0, spatial_magnitude=2.0, spatial_smooth_alpha=0.5,
    #                             spatial_smooth_delta=20, temporal_smooth_alpha=0.4, temporal_smooth_delta=20):
    #     """ 
    #     RS에서 획득한 깊이 프레임 전처리 필터링 하는 함수
    #         Return:
    #             filtered_frame : rs.frame()
    #     """

    #     # Post processing possible only on the depth_frame
    #     assert (depth_frame.is_depth_frame())

    #     # Available filters and control options for the filters
    #     decimation_filter = rs.decimation_filter()
    #     spatial_filter = rs.spatial_filter()
    #     temporal_filter = rs.temporal_filter()

    #     filter_magnitude = rs.option.filter_magnitude
    #     filter_smooth_alpha = rs.option.filter_smooth_alpha
    #     filter_smooth_delta = rs.option.filter_smooth_delta

    #     # Apply the control parameters for the filter
    #     decimation_filter.set_option(filter_magnitude, decimation_magnitude)
    #     spatial_filter.set_option(filter_magnitude, spatial_magnitude)
    #     spatial_filter.set_option(filter_smooth_alpha, spatial_smooth_alpha)
    #     spatial_filter.set_option(filter_smooth_delta, spatial_smooth_delta)
    #     temporal_filter.set_option(filter_smooth_alpha, temporal_smooth_alpha)
    #     temporal_filter.set_option(filter_smooth_delta, temporal_smooth_delta)

    #     # Apply the filters
    #     filtered_frame = decimation_filter.process(depth_frame)
    #     filtered_frame = spatial_filter.process(filtered_frame)
    #     filtered_frame = temporal_filter.process(filtered_frame)

    #     return filtered_frame


def make_folder(path_folder):
    print(path_folder)
    if not exists(path_folder):
        makedirs(path_folder)

"""
굉장히 위험한 함수. 
"""
def make_clean_folder(path_folder):
     if not exists(path_folder):
        makedirs(path_folder)
     else:
        shutil.rmtree(path_folder)
        makedirs(path_folder)
