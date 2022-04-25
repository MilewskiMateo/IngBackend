import uuid
import os

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from Abstract.IGenerateCompilation import IGenerateCompilation
from Abstract.ISteamCompilation import IStreamCompilation

class GenerateLogic(IGenerateCompilation):
    def generate_compiation(timestamps):
        video_clips = []
        name = str(uuid.uuid4())
        for stamp in timestamps:
            if stamp >= 10:
                stamp = stamp - 10
            video_clips.append(VideoFileClip("Videos/movie.mp4").subclip(stamp, stamp + 10))

        final_clip = concatenate_videoclips(video_clips)
        final_clip.write_videofile("Compilations/" + name + ".webm")
        return name

class StreamLogic(IStreamCompilation):
    def stream_compilation(identity, byte1=None, byte2=None):
        full_path = "Compilations/" + identity + ".webm"
        file_size = os.stat(full_path).st_size
        start = 0

        if byte1 < file_size:  start = byte1
        length = byte2 + 1 - byte1 if byte2 else file_size - start

        with open(full_path, 'rb') as f:
            f.seek(start)
            chunk = f.read(length)
        return chunk, start, length, file_size