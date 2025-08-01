import os
import queue
import traceback
import uuid
from enum import Enum
from multiprocessing import Queue, Process

from pytubefix import YouTube, Stream
from pytubefix.cli import on_progress

from utils import *


class VideoStatus(Enum):
    WAIT = 0
    MID_FAILED = 1
    COMPLETED = 2
    FAILED = 3

class Worker:
    # 예 일회용임
    def __init__(self, video_ids: list[str]):
        self.video_ids: list[str] = video_ids
        self.que: Queue[tuple[str, VideoStatus]] = Queue()
        self.video_statuses: dict[str, VideoStatus] = {video_id: VideoStatus.WAIT for video_id in self.video_ids}
        self.process: None | Process = None

    @property
    def is_done(self) -> bool | None:
        if self.process is None:
            return None

        return self.process.is_alive()

    def update_status(self):
        statuses: list[tuple[str, VideoStatus]] = list()

        while True:
            try:
                statuses.append(self.que.get_nowait())
            except queue.Empty: break

        for status in statuses:
            self.video_statuses[status[0]] = status[1]

    def start(self): # 외부 실행용
        self.process = Process(target=self.run, args=(self.video_ids, self.que,))
        self.process.start()

    def join(self):
        self.process.join()

    @staticmethod
    def run(video_ids: list[str], que: Queue): # 내부용
        for i, video_id in enumerate(video_ids):

            print(f"{len(video_ids)}개 중 {i + 1}번째 영상 시작")

            is_complete = False

            for try_nums in range(3):

                print(f"{try_nums + 1} 번째 시도 시작...")

                try:

                    print("영상 정보 가져오는중")
                    yt = YouTube(get_video_url(video_id), "WEB", on_progress_callback=on_progress)
                    print(f"영상 제목: {yt.title}")

                    print("비디오 스트림 다운로드...")
                    video_file_name = str(uuid.uuid4())
                    video_stream: Stream = sorted(yt.streams.fmt_streams, key=get_resolution)[-1]
                    video_stream.download(output_path="temp", filename=f"{video_file_name}.mp4")

                    print("오디오 스트림 다운로드...")
                    audio_file_name = str(uuid.uuid4())
                    audio_stream: Stream = sorted(yt.streams.fmt_streams, key=get_audio_bitrate)[-1]
                    audio_stream.download(output_path="temp", filename=f"{audio_file_name}.mp3")

                    print("파일 병합...")
                    merged_file_name = str(uuid.uuid4())
                    merge_video_audio(
                        f"temp/{video_file_name}.mp4", f"temp/{audio_file_name}.mp3", f"temp/{merged_file_name}.mp4"
                    )

                    print("파일 이동...")
                    try:
                        os.remove(f"downloads/{sanitize_filename(yt.title)}.mp4")
                    except FileNotFoundError:
                        pass

                    os.rename(f"temp/{merged_file_name}.mp4", f"downloads/{sanitize_filename(yt.title)}.mp4")

                    print("파일 정리...")

                    try:
                        os.remove(f"temp/{video_file_name}.mp4")
                    except FileNotFoundError: pass
                    try:
                        os.remove(f"temp/{audio_file_name}.mp3")
                    except FileNotFoundError: pass

                    is_complete = True
                    print(f"{try_nums + 1} 번째 시도 성공")


                except Exception as e:
                    print(f"{try_nums + 1} 번째 시도 실패")
                    traceback.print_exc()
                    que.put((video_id, VideoStatus.MID_FAILED))

                if is_complete: break

            if is_complete:
                print(f"{len(video_ids)}개 중 {i + 1}번째 영상 성공")
                que.put((video_id, VideoStatus.COMPLETED))

            else:
                print(f"{len(video_ids)}개 중 {i + 1}번째 영상 실패")
                que.put((video_id, VideoStatus.FAILED))

            print()