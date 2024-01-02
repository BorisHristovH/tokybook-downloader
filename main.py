import sys
import re
import ast
import requests
import os
from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs

BASE_PATH = './downloaded/'
AUDIO_BOOK_NAME = 'A Feast for Crows'
AUDIO_BOOK_PATH = BASE_PATH + AUDIO_BOOK_NAME + '/'
AUDIO_FILE_BASE_URL = 'https://files02.tokybook.com/audio/'
MP3_LINK_GETTER = 'https://api.crystallization.tv/api-us/getMp3Link'

def extract_and_download_tracks_from_url():
    main_page_url = sys.argv[1]
    response_body = requests.get(main_page_url)
    #write_to_file("site.html", response_body.text)
    playlist = get_playlist_from_body(response_body)

    for track in playlist:
        track_url_path = track["chapter_link_dropbox"]
        if track["name"] == 'welcome':
            continue
        mp3_name = track["name"] + ".mp3"
        save_file_path = AUDIO_BOOK_PATH + mp3_name

        uri = urlparse(AUDIO_FILE_BASE_URL)
        post_url = uri._replace(path=track_url_path).geturl()

        download_url = post_data_to_get_download_link(track)
        print("Got the download url ", download_url)
        doc = requests.get(download_url)

        write_to_file(save_file_path, doc.content)
        print("Wrote to file ", save_file_path)


# tracks are in a json in a specific script tag
def get_playlist_from_body(page):
    soup = bs(page.content, "html.parser")
    playlist = soup.find(class_="entry-content")
    scripts = list(map(lambda x : str(x.contents), playlist.select("script")))
    the_script = list(filter(lambda a: 'tracks' in a, scripts))[0] # should be only one with tracks

    extracted_variable = re.findall(' tracks = (\[(?:\[??[^\[]*?\]))',the_script)[0]
    clean_json = clean_up_json(extracted_variable)
    data = ast.literal_eval(clean_json)

    return data

def post_data_to_get_download_link(track):
    data = {
        "chapterId": track["chapter_id"],
        "serverType": '1'
    }
    response = requests.post(url=MP3_LINK_GETTER, json=data)
    return response.json()['link_mp3']

def clean_up_json(extracted_variable):
    formatted = re.sub(r',\s*}', '}', extracted_variable)
    white_space_stripped = formatted.replace(" ", "").replace("\\n", "")
    return white_space_stripped


def download(track_url):
    pass


def write_to_file(name, content):
    with open(name, "wb") as f:
        f.write(content)


if __name__ == "__main__":
    isExist = os.path.exists(AUDIO_BOOK_PATH)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(AUDIO_BOOK_PATH)
        print("The ", AUDIO_BOOK_PATH, " directory is created!")
    extract_and_download_tracks_from_url()
