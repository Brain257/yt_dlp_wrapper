import requests
from bs4 import BeautifulSoup
import subprocess
import logging
import argparse
import os
import sys 
import random
import time

logging.basicConfig(level=logging.INFO)


parser = argparse.ArgumentParser(description='Wrapper for yt-dlp to download videos, either provide a vimeo list of urls or a single video url')
parser.add_argument('--url', type=str, help='URL of the video or video list page')
parser.add_argument('--verbose', type=bool, help='Print yt-dlp output')
parser.add_argument('--folder', type=str, help='Folder to save the videos to')
parser.add_argument('--random_max_timedelay', type=int, help='Random maximum time delay between downloads in seconds to avoid getting blocked by the server')

verbose = parser.parse_args().verbose
url = parser.parse_args().url
folder = parser.parse_args().folder
random_max_timedelay = parser.parse_args().random_max_timedelay


playlist_name = ""
if "/videos/" not in url:
    playlist_name = url.split('/')[-1]
    logging.info(f"Suspecting a video list page. Trying to extract videos from playlist {playlist_name}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all(attrs={'data-track-event': 'site_video'})

    video_urls = list(set([element.get("href") for element in elements]))
    if len(video_urls) == 0:
        logging.error(f"Failed to extract videos from playlist {playlist_name}")
    for video_url in video_urls:
        logging.info(f"Found video: {video_url}")
    
else:
    video_urls = [url]


count = 0
for url in video_urls:
    if count == 2: 
        break
    cmd = f"./yt-dlp.exe --cookies cookies.txt -o \"\%(original_url)s.mp4\" {url}"

    logging.info(f"Trying to download: {url}")
    try: 
        if verbose: 
            subprocess.Popen(cmd, stdout=sys.stdout).communicate()
        else:
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")

    filename = url.split("videos/")[-1]
    logging.info(f"Successfully downloaded {filename}.")
    # windows hack 
    url = url.replace("/", "⧸").replace(":", "：")

    os.rename(f'{url}.mp4', f'{filename}.mp4')

    if folder != None:
        folder = folder
    elif playlist_name != "":
        folder = playlist_name
    else:
        continue

    logging.info(f"Moving to {folder}.")

    if not os.path.exists(folder):
        os.makedirs(folder)

    os.rename(f'{filename}.mp4', f'{folder}/{filename}.mp4')
    random.random(random_max_timedelay)
    print(f"Sleeping for: {random_max_timedelay}")
    time.sleep(random_max_timedelay)
    count += 1
