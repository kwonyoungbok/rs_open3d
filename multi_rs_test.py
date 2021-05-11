import pyrealsense2 as rs
import numpy as np
import cv2
import sys

from multi_rs.device_context import DeviceContext



if __name__ == "__main__":
   # try:
        # builder 만드는것도 괜찮겠네.. 너무 복잡해 만드는게.

        c = rs.config() 
        c.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)
        c.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 15)
        device_manager = DeviceContext(rs.context(), c)
        device_manager.enable_all_devices()
       
        while True:
            frames = device_manager.poll_frames_all_devices()
            print("무한 루프?",frames)
        
        device_manager.disable_streams()

        # while True:
        #     frames = device_manager.poll_frames()
        #     r_ret=   device_manager.restructure_frames(frames)
        #     colors= device_manager.pull_np_in_restructure(r_ret,'color')
        #     depths = device_manager.pull_np_in_restructure(r_ret,'depth')
           
    
        #     depth_colorized_list = device_manager.colorize_depth(depths)
        #     # bg_removed_list = device_manager.remove_bg(device_manager.increse_depth_list_channel(depths),colors)
            
        #     color_img = device_manager.merge_np(3,colors)
        #     depth_img =device_manager.merge_np(3,depth_colorized_list)

        #     color_img =cv2.resize(color_img,dsize=(1280,720),interpolation=cv2.INTER_CUBIC)
        #     depth_img =cv2.resize(depth_img,dsize=(1280,720),interpolation=cv2.INTER_CUBIC)


        #     cv2.imshow('Align Example',np.vstack((color_img,depth_img)))

        #     key = cv2.waitKey(1) 
        #     if key & 0xFF == ord('q') or key == 27:  # Press esc or 'q' to close the image window
        #         cv2.destroyAllWindows()
        #         break


    # finally:
    #     device_manager.disable_streams()