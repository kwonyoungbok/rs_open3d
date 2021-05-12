import pyrealsense2 as rs
from enum import Enum

from .Frameset_wrapper import FramesetWrapper

align_to = rs.stream.color
align = rs.align(align_to)

class DeviceStatus(Enum):
    Init = 0
    Enable = 1
    Disable= 2


class DisableDeviceError(Exception):
    def __init__(self):
      self._msg = "사용 불가능한 장치 사용"

    def __str__(self):
        return self._msg


class NotEqualFrameSetAndStream(Exception):
    def __init__(self):
      self._msg = "스트림과 프레임셋 길이가 다릅니다."

    def __str__(self):
        return self._msg
   

### Device Class 장치 관리 클래스 ###############################################################################################################################

class Device:

    def __init__(self,device_serial):
        self._device_serial= device_serial
        self._status= DeviceStatus.Init
        self._align=False
        self._pipeline_profile = None
        self._pipeline = None


#### public method ######################################################################################################################################
  
    def enable_device(self,config):
        pipeline = rs.pipeline()
        config.enable_device(self._device_serial)
        self._pipeline_profile = pipeline.start(config)
        self._pipeline = pipeline
        self._status= DeviceStatus.Enable
        return True

    
    def get_device_serial(self):
        return self._device_serial


    def poll_frames(self):
        if not self._status == DeviceStatus.Enable:
            raise RuntimeError("not enable device")
   
        streams = self._get_streams()
        frameset = self._get_poll_frameset()
       
        if frameset.size() != len(streams):
            return None

        if self._align:
            frameset = align.process(frameset)

        new_frameset= self._get_frames(frameset,streams)
        return FramesetWrapper(new_frameset)

 
    def get_status(self):
        return self._status

    def stop(self):
        #재시작 하는법 찾아야됨
        self._pipeline.stop()
      

    def set_align(self,set_boolean=False):
        self._align = set_boolean
        return self
    
    def get_depth_shape(self):
        depth_stream = self._find_stream(rs.stream.depth)
        if depth_stream is None:
            return None,None
        return depth_stream.as_video_stream_profile().width(), depth_stream.as_video_stream_profile().height()

### private method ###########################################################################################################
    
    def _get_streams(self):
       # 에러 처리 생략       
       return self._pipeline_profile.get_streams()
    
    def _get_poll_frameset(self):
        #에러 처리 생략
        # print(self._pipeline,'파이프라인은 있지?')
        return self._pipeline.poll_for_frames()
    
    def _get_frames(self,frameset, streams):
        frames = {}
        for stream in streams:
              if (rs.stream.infrared == stream.stream_type()):
                    frame = frameset.get_infrared_frame(stream.stream_index())
                    key_ = (stream.stream_type(), stream.stream_index())
              else:
                    frame = frameset.first_or_default(stream.stream_type())
                    key_ = stream.stream_type()
              frames[key_] =frame
        if len(frames) == 0:
            return None
        return frames

    def _find_stream(self,stream_type = rs.stream.depth):
        for stream in  self._get_streams():
            if stream_type ==  stream.stream_type():
                return stream
        return None



