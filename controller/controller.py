import abc

from realsense.device_factory import DeviceFactory

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
       return self._multi_device.poll_for_frames_all_devices()
      

    
