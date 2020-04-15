import json
import os
import subprocess as sp
from tempfile import NamedTemporaryFile

import cv2


class VideoUtilities:
    @staticmethod
    def get_ffprobe_path():
        return os.path.abspath("./bin/ffprobe.exe")

    @staticmethod
    def get_ffmpeg_path():
        return os.path.abspath("./bin/ffmpeg.exe")

    @classmethod
    def probe(cls, video_file_path: str):
        try:
            ffprobe_path = cls.get_ffprobe_path()
            print(ffprobe_path)
            assert os.path.exists(ffprobe_path), "Invalid ffprobe path provided"
            assert os.path.exists(video_file_path), "The video file doesn't exist"
            _, ext = os.path.splitext(video_file_path)
            assert ext in [".mp4"], "Invalid video file extension"
            cmd = [ffprobe_path,
                   "-loglevel", "quiet",
                   "-print_format", "json",
                   "-show_format",
                   "-show_streams",
                   video_file_path
                   ]
            pipe = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
            out, err = pipe.communicate()

            return json.loads(out)
        except Exception as ex:
            raise ex

    @classmethod
    def duration(cls, vid_file_path):
        # Video's duration in seconds
        _json = cls.probe(vid_file_path)
        if 'format' in _json:
            if 'duration' in _json['format']:
                return float(_json['format']['duration'])
        if 'streams' in _json:
            # commonly stream 0 is the video
            for s in _json['streams']:
                if 'duration' in s:
                    return float(s['duration'])
        # if everything didn't happen,
        # we got here because no single 'return' in the above happen.
        raise Exception('I found no duration')

    @classmethod
    def extract_frame(cls, vid_file_path):
        try:
            ffmpeg_path = cls.get_ffmpeg_path()
            assert os.path.exists(ffmpeg_path), "Invalid ffmpeg path provided"
            assert os.path.exists(vid_file_path), "The video file doesn't exist"
            _, ext = os.path.splitext(vid_file_path)
            tmpfile = NamedTemporaryFile(prefix="pytorchstudio_", suffix='.jpg')
            assert ext in [".mp4"], "Invalid video file extension"
            cmd = [ffmpeg_path,
                   "-i", vid_file_path,
                   "-ss", "00:00:01.00",
                   "-frames:v", "1",
                   tmpfile.name
                   ]
            pipe = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
            out, err = pipe.communicate()
            tmpfile.close()

            return out
        except Exception as ex:
            raise ex

    @classmethod
    def extract_frame_cv2(cls, video_file):
        try:
            vidcap = cv2.VideoCapture(video_file)
            vidcap.set(cv2.CAP_PROP_POS_MSEC, 2000)  # just cue to 20 sec. position
            success, image = vidcap.read()
            if success:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                return image
        except:
            return None
