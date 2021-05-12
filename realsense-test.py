import pyrealsense2 as rs
import numpy as np
import cv2
import sys

from realsense.multi_device import DeviceContext


if __name__ == "__main__":
    
        # builder 만드는것도 괜찮겠네.. 너무 복잡해 만드는게.
    c = rs.config()
    c.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)
    c.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
    device_manager = DeviceContext(rs.context(), c)
    device_manager.enable_all_devices()   
    try:
        # c = rs.config()
        # c.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)
        # c.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 15)

        # # 기계 없을떄 에러 던지도록
       
        # device_manager = DeviceContext(rs.context(), c)
        # device_manager.enable_all_devices()   
        while True:
            frames = device_manager.poll_for_frames_all_devices()
            print(frames)
           
            for frame in frames.values():
                color_np= frame.get_color_np()
                depth_np= frame.colorize_depth()
                cv2.imshow('Align Example',color_np)


            key = cv2.waitKey(1) 
            if key & 0xFF == ord('q') or key == 27:  # Press esc or 'q' to close the image window
                cv2.destroyAllWindows()
                break
    finally:
         device_manager.disable_streams()