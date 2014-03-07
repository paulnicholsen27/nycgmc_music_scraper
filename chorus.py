import requests
import urllib
import urllib2
import urlparse
import re
import os
import httplib
from os.path import isfile, join

from bs4 import BeautifulSoup
from pytube import YouTube
from pprint import pprint

import pdb

yt = YouTube()

def get_form_params(session, url, cookies):
    '''takes url as input and returns form id and form token (if it exists)'''
    form_token = None
    page = session.get(url, cookies=cookies)
    soupped_page = BeautifulSoup(page.content)
    form_build_id = soupped_page.select('input[name="form_build_id"]')
    form_token = soupped_page.select('input[name="form_token"]')
    if form_token:
        return form_build_id[0].get('value'), form_token[0].get('value')
    else:
        return form_build_id[0].get('value'), None

def login(session, name='paul.nichols', password='Ella27!'):
    '''takes as input a username and password, returns logged-in cookie'''
    form_build_id, form_token = get_form_params(session, 'http://nycgmc.groupanizer.com/user/login?destination=/',{})
    print "form build_id:", form_build_id
    print "form_token:", form_token
    payload = {'name' : name, 
    'pass' : password,
    'form_build_id' : form_build_id,
    'form_id' : 'user_login', 
    'op' : 'Log in'}
    logged_in = session.post('http://nycgmc.groupanizer.com/user/login?destination=/', data=payload)
    cookies = logged_in.cookies
    return cookies

def empty_folder(*args):
    for folder in args:
        for f in os.listdir(folder):
            file_path = os.path.join(folder, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e

def parse_page(concert_id, session):
    '''parses page and returns list of music links (.pdf) and list of video links (.mp4)'''
    sheet_music_links = []
    video_links = []
    url = 'http://nycgmc.groupanizer.com/music'
    cookies = login(session)
    form_build_id, form_token = get_form_params(session, url, cookies)
    print "concert_id:", concert_id
    # song_title_pattern = re.compile('(.+)\([v\d]')
    # song_version_pattern = re.compile('(\d+.\d+)')
    payload = {'terms[]' : concert_id,
    'op' : 'Filter',
    'form_build_id' : form_build_id,
    'form_token' : form_token,
    'form_id' : 'user_login'
    }
    music_page = session.get(url, data=payload, cookies=cookies)
    soup = BeautifulSoup(music_page.content)
    link_list = [link.get('href') for link in soup.find_all('a') if 'node' in link.get('href')]
     #contains extraneous /node/add link
    try:
        link_list.remove('/node/add')
    except:
        pass
    for link in link_list:
        url = 'http://nycgmc.groupanizer.com' + link
        song_page = session.get(url)
        song_page_soup = BeautifulSoup(song_page.content)
        for music_link in song_page_soup.find_all('a'):
            if music_link.get('href').endswith('.pdf'):
                sheet_music_links.append((music_link.text, music_link.get('href')))
            else:
                if music_link.get('href').find('youtu') != -1: #finds youtube and youtu.be
                    video_links.append(music_link.get('href'))

    return sheet_music_links, video_links

def write_sheet_music_to_file(session, sheet_music_links, directory_str):
    '''takes as input list of music links and writes all sheet music to specified directory_str
            for that concert period'''
    for filename in sheet_music_links:
        new_filename = filename[0].replace('/', '_')
        print new_filename


        f = open(directory_str + new_filename, 'wb')
        f.write(session.get(filename[1]).content)
        f.close()


def write_videos_to_file(session, video_links, directory_str):
    for url in video_links:
        if url.find('youtu.be') != -1:
            yt.url = unshorten_url(url)
        else: 
            yt.url = url
        pprint(yt.filename)
        video = yt.filter('mp4')[-1] #gets highest video resolution of mp4 format
        fullpath = '{0}{1}.{2}'.format(directory_str, yt.filename, 'mp4')
        print fullpath
        if not isfile(fullpath):
            video.download(directory_str)

def unshorten_url(url):
    parsed = urlparse.urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc)
    h.request('HEAD', parsed.path)
    response = h.getresponse()
    if response.status/100 == 3 and response.getheader('Location'):
        return response.getheader('Location')
    else:
        return url

def main():
    concert_id = [130] #will later change to be input by user for diff concerts
    session = requests.session()
    if os.path.exists('/Users/nicholsp/Dropbox/chorus_music/'):
        directory_str = '/Users/nicholsp/Dropbox/chorus_music/'
    else:
        directory_str = '/Users/paulnichols/Dropbox/chorus_music/'
    sheet_music_directory = directory_str + 'sheet_music/'
    choralography_directory = directory_str + 'choralography/'
    empty_folder(directory_str, sheet_music_directory, choralography_directory)
    sheet_music_links, video_links = parse_page(concert_id, session)
    write_sheet_music_to_file(session, sheet_music_links, sheet_music_directory)
    write_videos_to_file(session, video_links, choralography_directory)
    print 'Finished!'

main()

