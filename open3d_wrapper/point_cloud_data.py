import open3d as o3d
import time 

from realsense.Frameset_wrapper import FramesetWrapper


class PointCloudData:

    flip_transform = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]]

    def __init__(self,frameset_wrapper,depth_scale):
        self._frameset_wrapper= frameset_wrapper
        self._depth_scale = depth_scale
        self._clipping_distance_in_meters =1 # meter
        self._pcd = None

    
    def get_color_intrinsic_matrix(self):
       color_intrinsic ,_ = self._frameset_wrapper.get_intrinsic()
       out = o3d.camera.PinholeCameraIntrinsic(1920, 1080, color_intrinsic.fx,
                                            color_intrinsic.fy, color_intrinsic.ppx,
                                            color_intrinsic.ppy)
       return out 

    

    def make_pcd(self):
        depth_np = self._frameset_wrapper.get_depth_np()
        color_np = self._frameset_wrapper.get_color_np()

        print(depth_np,color_np,"보자")
        depth_image = o3d.geometry.Image(depth_np)
        color_image = o3d.geometry.Image(color_np)

        rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color_image,
            depth_image,
            depth_scale=1.0 / self._depth_scale,
            depth_trunc=self._clipping_distance_in_meters,
            convert_rgb_to_intensity=False)

        intrinsic = self.get_color_intrinsic_matrix()
        temp = o3d.geometry.PointCloud.create_from_rgbd_image(
                rgbd_image, intrinsic)
        temp.transform(self.flip_transform)

        pcd = o3d.geometry.PointCloud()
        pcd.points = temp.points
        pcd.colors = temp.colors
        self._pcd = pcd
        return pcd

    def save_pcd(self,file_name):
        if self._pcd is None:
            raise RuntimeError("pcd 파일을 생성 할 수 없습니다.")
        o3d.io.write_point_cloud(file_name+".pcd", self._pcd)



    



