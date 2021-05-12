import pyrealsense2 as rs
import abc
from enum import Enum

from ..Frameset_wrapper import FramesetWrapper
from .pipeline import Pipeline as PipelineWrapper

align_to = rs.stream.color
align = rs.align(align_to)

class DeviceStatus(Enum):
    Init = 0
    Enable = 1
    Disable= 2


class DeviceImp(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def enable_device(self,config):
        """
        파이프라인 생성하여 이용 가능한 장치 상태 만듬

        param:
            - config: pyrealsense2.config() 객체

        return: 
            - True =  enable 성공 시
            - false = enable 실패 시
               
        """
        raise NotImplemented

    @abc.abstractmethod
    def poll_for_frames(self):
        """
        계속 호출해서 장치에 새로운 프레임셋 있는지 확인하고 반환하는 함수

        return:
          - FramesetWrapper = 결과 값 존재할 때 
          - None = 결과 값 없을 때 
          - raise  RuntimeError("not enable device") = 장치가 사용 불가능할 때 

        """
        raise NotImplemented

    
    def get_status(self):
        """
        return:
            - DeviceStatus: 현재 장치 상태
        """
        return self._status


    def get_device_serial(self):
        """
        return: 
            - string : 장치 시리얼 번호
        """
        return self._device_serial


    def get_status(self):
        """
        return:
            - DeviceStatus: 현재 장치 상태
        """
        return self._status
    
    def get_depth_scale(self):
        return  self._pipeline.get_depth_scale()



class Device(DeviceImp):
    def __init__(self,device_serial):
        self._device_serial= device_serial
        self._status= DeviceStatus.Init
        self._pipeline = None


    def enable_device(self,config):
        self._pipeline = PipelineWrapper(config)
        self._pipeline.start(self._device_serial)
        self._status= DeviceStatus.Enable
        return True

    def poll_for_frames(self):
        if not self._status == DeviceStatus.Enable:
            raise RuntimeError("not enable device")
       
        pipeline = self._pipeline
        frame_dic =  pipeline.poll_for_frames()

        if frame_dic is None:
            return None

        return FramesetWrapper(frame_dic)
