import re

import ffmpeg
from pytubefix import YouTube, Channel, Stream
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def get_video_tab_ids(channel_url: str) -> list[str]:
    yts: list[YouTube] = Channel(channel_url).video_urls
    return [yt.video_id for yt in yts]

def get_shorts_tab_ids(channel_url: str, ) -> list[str]:
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    url = channel_url.rstrip("/") + "/shorts"
    driver.get(url)

    elements = driver.find_elements(By.CSS_SELECTOR, "a.shortsLockupViewModelHostEndpoint.reel-item-endpoint")

    video_urls = [element.get_attribute("href") for element in elements]
    video_ids = [video_url.split("/")[-1] for video_url in video_urls]

    return video_ids


def get_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


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


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    return name
