# 밑에 링크에서 분석해서 추상화
# https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/box_dimensioner_multicam/realsense_device_manager.py#L284 
# https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/align-depth2color.py
import pyrealsense2 as rs
import numpy as np
import cv2
import sys


align_to = rs.stream.color
align = rs.align(align_to)

class Device:
    def __init__(self, pipeline, pipeline_profile):
        self.pipeline = pipeline
        self.pipeline_profile = pipeline_profile



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



def post_process_depth_frame(depth_frame, decimation_magnitude=1.0, spatial_magnitude=2.0, spatial_smooth_alpha=0.5,
                             spatial_smooth_delta=20, temporal_smooth_alpha=0.4, temporal_smooth_delta=20):
    """ 
    RS에서 획득한 깊이 프레임 전처리 필터링 하는 함수
        Return:
            filtered_frame : rs.frame()
    """

    # Post processing possible only on the depth_frame
    assert (depth_frame.is_depth_frame())

    # Available filters and control options for the filters
    decimation_filter = rs.decimation_filter()
    spatial_filter = rs.spatial_filter()
    temporal_filter = rs.temporal_filter()

    filter_magnitude = rs.option.filter_magnitude
    filter_smooth_alpha = rs.option.filter_smooth_alpha
    filter_smooth_delta = rs.option.filter_smooth_delta

    # Apply the control parameters for the filter
    decimation_filter.set_option(filter_magnitude, decimation_magnitude)
    spatial_filter.set_option(filter_magnitude, spatial_magnitude)
    spatial_filter.set_option(filter_smooth_alpha, spatial_smooth_alpha)
    spatial_filter.set_option(filter_smooth_delta, spatial_smooth_delta)
    temporal_filter.set_option(filter_smooth_alpha, temporal_smooth_alpha)
    temporal_filter.set_option(filter_smooth_delta, temporal_smooth_delta)

    # Apply the filters
    filtered_frame = decimation_filter.process(depth_frame)
    filtered_frame = spatial_filter.process(filtered_frame)
    filtered_frame = temporal_filter.process(filtered_frame)

    return filtered_frame



class DeviceManager:
    def __init__(self, context, pipeline_configuration):
        """
        Class to manage the Intel RealSense devices
        Parameters:
        -----------
        context                 : rs.context()
                                  The context created for using the realsense library
        pipeline_configuration  : rs.config()
                                  The realsense library configuration to be used for the application
        """
        assert isinstance(context, type(rs.context()))
        assert isinstance(pipeline_configuration, type(rs.config()))
      
        self._context = context
        self._available_devices = enumerate_connected_devices(context)
        self._enabled_devices = {}
        self._config = pipeline_configuration
        self._frame_counter = 0

    def enable_device(self, device_serial):
        """
        Enable an Intel RealSense Device
        Parameters:
        -----------
        device_serial     : string
                            Serial number of the realsense device
        """
        pipeline = rs.pipeline()

        # Enable the device
        self._config.enable_device(device_serial)
        pipeline_profile = pipeline.start(self._config)
        self._enabled_devices[device_serial] = (Device(pipeline, pipeline_profile))

    def enable_all_devices(self,select_idx=False,idx=0):
        """
        Enable all the Intel RealSense Devices which are connected to the PC
        """
        print(str(len(self._available_devices)) + " devices have been found")
    
        if select_idx:
            self.enable_device(self._available_devices[idx])
            return

        for serial in self._available_devices:
            self.enable_device(serial)

    # def enable_emitter(self, enable_ir_emitter=True):
    #     """ 이 메서드 호출하면 에러
    #     Enable/Disable the emitter of the intel realsense device
    #     """
    #     for (device_serial, device) in self._enabled_devices.items():
    #         # Get the active profile and enable the emitter for all the connected devices
    #         sensor = device.pipeline_profile.get_device().first_depth_sensor()
    #         sensor.set_option(rs.option.emitter_enabled, 1 if enable_ir_emitter else 0)
    #         if enable_ir_emitter:
    #             sensor.set_option(rs.option.laser_power, 330)

    # def load_settings_json(self, path_to_settings_file):
    #     """ 400번대 모델 전용인듯 코드 상태가
    #     Load the settings stored in the JSON file
    #     """

    #     with open(path_to_settings_file, 'r') as file:
    #     	json_text = file.read().strip()

    #     for (device_serial, device) in self._enabled_devices.items():
    #         # Get the active profile and load the json file which contains settings readable by the realsense
    #         device = device.pipeline_profile.get_device()
    #         advanced_mode = rs.rs400_advanced_mode(device)
    #         advanced_mode.load_json(json_text)

    def poll_frames(self):
        """
        Poll for frames from the enabled Intel RealSense devices. This will return at least one frame from each device. 
        If temporal post processing is enabled, the depth stream is averaged over a certain amount of frames
        
        Parameters:
        -----------
        """
        frames = {}
        while len(frames) < len(self._enabled_devices.items()) :
            for (serial, device) in self._enabled_devices.items():
                streams = device.pipeline_profile.get_streams()
                frameset = device.pipeline.poll_for_frames() #frameset will be a pyrealsense2.composite_frame object
                if frameset.size() == len(streams):
                    # align
                   # frameset = align.process(frameset)
                    frames[serial] = {}
                    for stream in streams:
                        if (rs.stream.infrared == stream.stream_type()):
                            frame = frameset.get_infrared_frame(stream.stream_index())
                            key_ = (stream.stream_type(), stream.stream_index())
                        else:
                            frame = frameset.first_or_default(stream.stream_type())
                            key_ = stream.stream_type()
                        frames[serial][key_] = frame
        return frames


    def get_depth_shape(self):
        """  이 쓰레기 메서드는 왜 존재하지? 왜 임의의 뎁스 카메라 높이 너비가 필요하지?
        Retruns width and height of the depth stream for one arbitrary device
        Returns:
        -----------
        width : int
        height: int
        """
        width = -1
        height = -1
        for (serial, device) in self._enabled_devices.items():
            for stream in device.pipeline_profile.get_streams():
                if (rs.stream.depth == stream.stream_type()):
                    width = stream.as_video_stream_profile().width()
                    height = stream.as_video_stream_profile().height()
        return width, height

    def get_device_intrinsics(self, frames):
        """
        Get the intrinsics of the imager using its frame delivered by the realsense device
        Parameters:
        -----------
        frames : rs::frame
                 The frame grabbed from the imager inside the Intel RealSense for which the intrinsic is needed
        Return:
        -----------
        device_intrinsics : dict
        keys  : serial
                Serial number of the device
        values: [key]
                Intrinsics of the corresponding device
        """
        device_intrinsics = {}
        for (serial, frameset) in frames.items():
            device_intrinsics[serial] = {}
            for key, value in frameset.items():
                device_intrinsics[serial][key] = value.get_profile().as_video_stream_profile().get_intrinsics()
        return device_intrinsics

    def get_depth_to_color_extrinsics(self, frames):
        """
        Get the extrinsics between the depth imager 1 and the color imager using its frame delivered by the realsense device
        Parameters:
        -----------
        frames : rs::frame
                 The frame grabbed from the imager inside the Intel RealSense for which the intrinsic is needed
        Return:
        -----------
        device_intrinsics : dict
        keys  : serial
                Serial number of the device
        values: [key]
                Extrinsics of the corresponding device
        """
        device_extrinsics = {}
        for (serial, frameset) in frames.items():
            device_extrinsics[serial] = frameset[
                rs.stream.depth].get_profile().as_video_stream_profile().get_extrinsics_to(
                frameset[rs.stream.color].get_profile())
        return device_extrinsics

    def disable_streams(self):
        self._config.disable_all_streams()
    
    def restructure_frames(self,frames):
        """
         poll_frames 하면 데이터 형식이 키값 들어가서 (#255 막 이런식으로)
         막상 외부에서 사용하기 힘들어서 이 함수로 좀 더 쉽게 사용하도록

         반환값 {
             기기번호:{
                 color: 프레임
                 depth: 프레임
             }
             ...
          }
        """
        ret = {}
        for (serial,_) in self._enabled_devices.items():
            ret[serial]={}
            serial_frames = list(frames[serial].values())
            for frame in serial_frames:
                name = frame.__str__()
                if "BGR8" in name:
                    key = 'color'
                    ret[serial][key]= frame
                elif "Z16" in name:
                    key= 'depth'
                    ret[serial][key]= frame
        return ret
    
    def pull_np_in_restructure(self,r_frames,type_stream='color'):
        ret = []
        for (serial,_) in self._enabled_devices.items():
            np_value= self.frame_to_np(r_frames[serial][type_stream])
            ret.append(np_value)
        return ret

    def increse_depth_list_channel(self,depth_list):
        ret = []
        for depth in depth_list: # 3channel로 증강
            ret.append(np.dstack((depth,depth,depth)))
        return ret
    
    def remove_bg(self,depth_3channel_list, color_list,grey_color=153,clipping_distance=0.03):
        # 작동 안함.. 
        ret = []
        for i in range(len(depth_3channel_list)):
          bg_removed=  np.where((depth_3channel_list[i] > clipping_distance) | (depth_3channel_list[i] <= 0), grey_color, color_list[i])
          ret.append(bg_removed)
        return ret


    def frame_to_np(self,frame):
        return np.asanyarray(frame.get_data())

    def colorize_depth(self,depth_list):
        ret = []
        for depth in depth_list:
           di = cv2.applyColorMap(cv2.convertScaleAbs(depth, alpha=0.03), cv2.COLORMAP_JET)
           ret.append(di)
        return ret

    def merge_np(self,width,arr_np):
        chunked =  [arr_np[i:i+width] for i in range(0,len(arr_np),width)]
        to_vstack_list = []
        for to_hstack_list in chunked:
            if len(to_hstack_list)< width: # 개수가 안맞을때 검은색 화면 만듬
                fragment = to_hstack_list[0]
                for i in range(width-len(to_hstack_list)):
                    to_hstack_list.append(np.zeros(fragment.shape,np.uint8))
            to_vstack_list.append(np.hstack(tuple(to_hstack_list)))

        return np.vstack(tuple(to_vstack_list))


    
    
    

if __name__ == "__main__":
    try:
        c = rs.config()
        c.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)
        c.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 15)
        # c.enable_stream(rs.stream.infrared, 1, 1280, 720, rs.format.y8, 6)
        # c.enable_stream(rs.stream.infrared, 2, 1280, 720, rs.format.y8, 6)
        device_manager = DeviceManager(rs.context(), c)
        
        one_device = True
        print(sys.argv[1],":...ssap...")
        if sys.argv[1] == 'all':
            one_device= False

        
        print(sys.argv[1],":...ssap...",one_device)
        device_manager.enable_all_devices(one_device,int(sys.argv[2]))

        while True:
            frames = device_manager.poll_frames()
            r_ret=   device_manager.restructure_frames(frames)
            colors= device_manager.pull_np_in_restructure(r_ret,'color')
            depths = device_manager.pull_np_in_restructure(r_ret,'depth')
           
    
            depth_colorized_list = device_manager.colorize_depth(depths)
            # bg_removed_list = device_manager.remove_bg(device_manager.increse_depth_list_channel(depths),colors)
            
            color_img = device_manager.merge_np(3,colors)
            depth_img =device_manager.merge_np(3,depth_colorized_list)

            color_img =cv2.resize(color_img,dsize=(1280,720),interpolation=cv2.INTER_CUBIC)
            depth_img =cv2.resize(depth_img,dsize=(1280,720),interpolation=cv2.INTER_CUBIC)


            cv2.imshow('Align Example',np.vstack((color_img,depth_img)))

            key = cv2.waitKey(1) 
            if key & 0xFF == ord('q') or key == 27:  # Press esc or 'q' to close the image window
                cv2.destroyAllWindows()
                break


       # device_extrinsics = device_manager.get_depth_to_color_extrinsics(frames)
    finally:
        device_manager.disable_streams()