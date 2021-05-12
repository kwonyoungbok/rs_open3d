import numpy as np
import cv2
import pyrealsense2 as rs

align_to = rs.stream.color
rs_align = rs.align(align_to)

class FramesetWrapper:
    def __init__(self,frameset):
        self.frameset = frameset
        self.np_set = None


    def _get_np_set(self):
        if self.frameset is None:
            return None
        if self.np_set is None:
            self.np_set = self._to_np()
        return self.np_set


    def _restructure_frameset(self):
        """
            { <stream.depth: 1>: <pyrealsense2.frame Z16 #58>, <stream.color: 2>: <pyrealsense2.frame BGR8 #46> }
            이런식으로 프레임셋이 나와서
            {
                depth:...
                color:...
            }로 변환
        """
        frames = self.frameset
        if frames is None:
            return frames
        ret = {}
        for frame in list(frames.values()):
            name = frame.__str__()
            if "BGR8" in name:
                ret["color"]=frame
            elif "Z16" in name:
                ret["depth"]=frame
        return ret
   
    def _to_np(self):
        """
        """
        recon = self._restructure_frameset()

        print(recon,"응?")
        if recon is None:
            return None
        ret = {}
        for name ,frame in recon.items():
            if name == "depth":
                ret[name]= np.array(frame.get_data())
                #ret[name]= np.dstack((ret[name],ret[name],ret[name])) 
            elif name == "color":
                ret[name]= np.asarray(frame.get_data())
                ret[name]= ret[name][...,::-1].copy()

            
        return ret
    
    def get_color_np(self):
        np_set = self._get_np_set()

        if np_set is None:
            return None
        color_np = np_set.get('color')  
        if color_np is None:
            return None
        return color_np

    def get_depth_np(self):
        np_set = self._get_np_set()
        if np_set is None:
            return None
        depth_np = np_set.get('depth')
        if depth_np is None:
            return None
        return depth_np

    
    def colorize_depth(self):
        depth_np = self.get_depth_np()
        if depth_np is None:
            return None
        return cv2.applyColorMap(cv2.convertScaleAbs(depth_np, alpha=0.03), cv2.COLORMAP_JET)

    
    def get_intrinsic(self):
        reconstructed_frameset = self._restructure_frameset()
        if reconstructed_frameset is None:
            return None
        color_frame= reconstructed_frameset.get("color")
        depth_frame= reconstructed_frameset.get("depth")

        color_intrinsic = color_frame.profile.as_video_stream_profile().intrinsics
        depth_intrinsic = depth_frame.profile.as_video_stream_profile().intrinsics

        return color_intrinsic,depth_intrinsic

   
    def align(self):
        self.frameset = rs_align.process(self.frameset)
        return None



    # def remove_bg(self,depth_3channel_list, color_list,grey_color=153,clipping_distance=0.03):
    #     # 작동 안함..  고치긴 해야할듯?
    #     ret = []
    #     for i in range(len(depth_3channel_list)):
    #       bg_removed=  np.where((depth_3channel_list[i] > clipping_distance) | (depth_3channel_list[i] <= 0), grey_color, color_list[i])
    #       ret.append(bg_removed)
    #     return ret

    # def merge_np(self,width,arr_np):
    #     chunked =  [arr_np[i:i+width] for i in range(0,len(arr_np),width)]
    #     to_vstack_list = []
    #     for to_hstack_list in chunked:
    #         if len(to_hstack_list)< width: # 개수가 안맞을때 검은색 화면 만듬
    #             fragment = to_hstack_list[0]
    #             for i in range(width-len(to_hstack_list)):
    #                 to_hstack_list.append(np.zeros(fragment.shape,np.uint8))
    #         to_vstack_list.append(np.hstack(tuple(to_hstack_list)))

    #     return np.vstack(tuple(to_vstack_list))

    

    



        