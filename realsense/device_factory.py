import pyrealsense2 as rs

from .multi_device import DeviceContext


class DeviceFactory:

    @staticmethod
    def createMultiDevice():
        c = rs.config()
        c.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)
        c.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
        device_manager = DeviceContext(rs.context(), c)
        return device_manager
