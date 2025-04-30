# spoof_video.py

import os
import ffmpeg

def spoof_video(filepath, output_folder):
    base = os.path.basename(filepath)
    name, _ = os.path.splitext(base)
    out_path = os.path.join(output_folder, f"{name}_spoofed.mp4")

    (
        ffmpeg
        .input(filepath)
        .output(out_path, vcodec='libx264', video_bitrate='500k', r=29.97, preset='ultrafast')
        .run(overwrite_output=True)
    )
