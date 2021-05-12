import pyrealsense2 as rs
import abc


"""
사실 장치가 곧 파이프라인이라서 나누는게 의미가 있을까 싶은데

 굳이 나눈 이유는 _pipeline_profile 조작하기 시작하면 코드가 꽤나 복잡해짐
 그래서 그거 단순화 시킬려고 래핑했습니다.  

"""

align_to = rs.stream.color
align = rs.align(align_to)

class PipelineImp(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def start(self,device_serial):
        """
         param:
            - string: device_serial
        """
        raise NotImplemented


    @abc.abstractmethod
    def poll_for_frames(self):
        """
        비동기로 프레임 확인
        따라서 1초 30프레임이면 최소 1초에 30번 loop 돌려서 결과 얻어야한다.

        return:
            - List(rs.frameset)
            - None
        """
        raise NotImplemented


    @abc.abstractmethod
    def wait_for_frames(self):
        """
        동기로 프레임 확인

        return:
            - List(rs.frameset)
            - ?
        """
        raise NotImplemented


    def set_align(self,set_boolean=False):
        self.__align = set_boolean
        return self

    def is_align(self):
        return self.__align
    

    def get_streams(self):
        if self._pipeline_profile is None:
            raise  RuntimeError("파이프라인 None 입니다")
        streams =  self._pipeline_profile.get_streams()
        if streams is None:
            raise  RuntimeError("스트림 설정 오류 입니다.")
        return streams

    
    def find_stream(self,stream_type = rs.stream.depth):
        """
        param:
            - rs.stream.* : stream_type = 예를 들어서 rs.stream.depth 설정

        return:
            - stream
            - None
        """

        for stream in  self.get_streams():
            if stream_type ==  stream.stream_type():
                return stream
        return None

 
    @staticmethod
    def make_frame_dic_key_by_stream(frames, streams):
        """
         프레임과 스트림을 매칭해서 스트림 타입을 키로 하는 프레임 딕셔너리 생성함
        
        param:
            - rs.FrameSet :frames 
            - List(rs.Stream) : streams

        return:
            - None
            - dict( key=stream_type(), value=frame)
        """
        frame_dic = {}
        for stream in streams:
              if (rs.stream.infrared == stream.stream_type()):
                    frame = frames.get_infrared_frame(stream.stream_index())
                    key_ = (stream.stream_type(), stream.stream_index())
              else:
                    frame = frames.first_or_default(stream.stream_type())
                    key_ = stream.stream_type()
              frame_dic[key_] =frame
        if len(frame_dic) == 0:
            return None
        return frame_dic


class Pipeline(PipelineImp):
    def __init__(self,config):
        self._config = config
        self._pipeline = None
        self._pipeline_profile = None
        self.set_align(False)
        
    
    def start(self,device_serial):
        self._pipeline=  rs.pipeline()
        self._config.enable_device(device_serial)
        self._pipeline_profile = self._pipeline.start(self._config)

    
    def poll_for_frames(self):
        if self._pipeline is None:
            raise RuntimeError("파이프라인이 None 입니다")
        frames=  self._pipeline.poll_for_frames() # 여기서도 널 반환함
        streams = self.get_streams()

        if frames is None:
            return None

        if frames.size() != len(streams):
            return None

        if  self.is_align():
            frames =  align.process(frames)

        return PipelineImp.make_frame_dic_key_by_stream(frames,streams)


    def wait_for_frames(self):
        if self._pipeline is None:
            raise RuntimeError("파이프라인이 None 입니다")
        streams = self.get_streams()
        frames =self._pipeline.wait_for_frames() 
        
        if frames.size() != len(streams):
              raise RuntimeError("스트림과 프레임이 개수가 서로 다릅니다.")
              
        if  self.is_align():
            frames =  align.process(frames)

        return PipelineImp.make_frame_dic_key_by_stream(frames,streams)

    
    

    