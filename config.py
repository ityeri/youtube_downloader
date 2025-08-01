from pytubefix import YouTube, Channel, Stream

from utils import *

channel_url = "https://www.youtube.com/@airikannach"

video_ids: set[str] = set()

video_ids |= set(get_video_tab_ids(channel_url))
video_ids |= set(get_shorts_tab_ids(channel_url))

id_mask = {
    "79HvRSn0yS8",
    "k2GwzlGPxos",
    "cAFAhbEY5OU",
    "377XtZx3CX4",
    "WUz8HCi5dyU",
    "Gz66-Sedj_c",
    "CgahE0MVAPw",
    "eNbB4MWbZAI",
    "Hfm1vbrLQIE",
    "101l5uMlJ2k",
    "5P4syQCEAMg",
    "R194kMieXsE",
    "RqpJXlSWZyM"
}

video_ids -= id_mask

if __name__ == "__main__":
    for url in video_ids:
        print(url)