import pyrealsense2 as rs


from .single_device.device import Device


# 다중 디바이스 관리 객체
class DeviceContext:
    
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

    
    def poll_frames_all_devices(self):
        frames = {}
        while len(frames) < len(self._enabled_devices_dic):
            for (_,device) in self._enabled_devices_dic.items():
              frame =  device.poll_frames()
              if frame is None:
                  continue
              frames[device.get_device_serial()]=frame
        return frames

    def disable_streams(self):
        self._config.disable_all_streams()

### private method #######################################################################################################################################################

    def _initialize(self):
        self._create_devices()


    def _create_devices(self):
        for serial  in self._available_devices:
            print(serial)
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

    @staticmethod
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