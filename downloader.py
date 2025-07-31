import os

from pytubefix import YouTube, Stream
from pytubefix.cli import on_progress
import ffmpeg
import re
import time
from datetime import timedelta

from config import urls

def get_resolution(stream: Stream) -> int:
    if not stream.resolution:
        return 0
    else:
        return int(stream.resolution.replace("p", ""))

def get_audio_bitrate(stream: Stream) -> int:
    if not stream.abr:
        return 0
    else:
        return int(stream.abr.replace("kbps", ""))

def sanitize_filename(name: str) -> str:
    # Windows 금지 문자 제거
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    return name

def merge_video_audio(video_path, audio_path, output_path):
    video_input = ffmpeg.input(video_path)
    audio_input = ffmpeg.input(audio_path)

    (
        ffmpeg
        .output(video_input.video, audio_input.audio, output_path, vcodec='copy', acodec='aac', shortest=None)
        .overwrite_output()
        # .global_args('-loglevel', 'quiet')
        .run()
    )

print(urls)

os.makedirs("downloads/", exist_ok=True)
os.makedirs("temp/", exist_ok=True)

start_time = time.time()

for i, url in enumerate(urls):

    print(f"{len(urls)}개 중 {i + 1}번째 영상 시작")

    is_complete = False

    for try_nums in range(3):

        print(f"{try_nums + 1} 번째 시도 시작...")

        try:

            print("영상 정보 가져오는중")
            yt = YouTube(url, "WEB", on_progress_callback=on_progress)
            print(f"영상 제목: {yt.title}")

            print("비디오 스트림 다운로드...")
            video_stream: Stream = sorted(yt.streams.fmt_streams, key=get_resolution)[-1]
            video_stream.download(output_path="temp", filename=f"temp.mp4")

            print("오디오 스트림 다운로드...")
            audio_stream: Stream = sorted(yt.streams.fmt_streams, key=get_audio_bitrate)[-1]
            audio_stream.download(output_path="temp", filename=f"temp.mp3")

            print("파일 병합...")
            merge_video_audio(
                "temp/temp.mp4", "temp/temp.mp3", "temp/temp1.mp4"
            )

            print("파일 이동...")
            try:
                os.remove(f"downloads/{sanitize_filename(yt.title)}.mp4")
            except FileNotFoundError: pass

            os.rename("temp/temp1.mp4", f"downloads/{sanitize_filename(yt.title)}.mp4")

            is_complete = True
            print(f"{try_nums + 1} 번째 시도 성공")

        except Exception as e:
            print(f"{try_nums + 1} 번째 시도 실패")
            print(e)

        if is_complete: break

    if is_complete:
        print(f"{len(urls)}개 중 {i + 1}번째 영상 성공")
    else:
        print(f"{len(urls)}개 중 {i + 1}번째 영상 실패")

    print()

end_time = time.time()

time_elapsed = end_time - start_time

print(f"{len(urls)}개 전체 완료. 총 소요시간: {str(timedelta(seconds=time_elapsed))}")