import sys
import re
import json
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs

BASE_PATH = './downloaded/'
AUDIO_FILE_BASE_URL = 'https://files02.tokybook.com/audio/'
MP3_LINK_GETTER = 'https://api.crystallization.tv/api-us/getMp3Link'
def extract_and_download_tracks_from_url():
    main_page_url = sys.argv[1]
    response_body = requests.get(main_page_url)
    write_to_file("site.html", response_body.text)
    playlist = get_playlist_from_body(response_body)

    for track in playlist:
        track_url_path = track["chapter_link_dropbox"]
        if track["name"] == 'welcome':
            continue
        mp3_name = track["name"] + ".mp3"
        save_file_path = BASE_PATH + main_page_url.split('/')[-2] + '/' + mp3_name

        uri = urlparse(AUDIO_FILE_BASE_URL)
        post_url = uri._replace(path=track_url_path).geturl()

        download_url = post_data_to_get_download_link(track)

        doc = requests.get(download_url)

        with open('downloaded_song.mp3', 'wb') as file:
                file.write(doc.content)
        write_to_file(save_file_path, doc.content)


# tracks are in a json in a specific script tag
def get_playlist_from_body(page):
    soup = bs(page.content, "html.parser")
    playlist = soup.find(class_="entry-content")
    scripts = list(map(lambda x:x.text, playlist.select("script")))
    the_script = list(filter(lambda a: 'tracks' in a, scripts))[0] # should be only one with tracks

    extracted_variable = re.findall(' tracks = (\[(?:\[??[^\[]*?\]))',the_script)[0]
    clean_json = clean_up_json(extracted_variable)
    data = json.loads(clean_json) # sad not working
    return data

def post_data_to_get_download_link(track):
    data = {
        "chapterId": track["chapter_id"],
        "serverType": '1'
    }
    response = requests.post(url=MP3_LINK_GETTER, json=data)
    return response.json()['link_mp3']

def clean_up_json(extracted_variable):
    return re.sub(r',\s*}', '}', extracted_variable)

def download(track_url):
    pass


def write_to_file(name, text):
    f = open(name, 'w', encoding='utf-8')
    f.write(text)
    f.close()


if __name__ == "__main__":
    extract_and_download_tracks_from_url()
