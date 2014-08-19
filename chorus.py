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
from config import username, password

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


def login(session, name, password):
    '''takes as input a username and password, returns logged-in cookie'''
    form_build_id, form_token = get_form_params(
        session, 'http://nycgmc.groupanizer.com/user/login?destination=/', {})
    print "form build_id:", form_build_id
    print "form_token:", form_token
    payload = {'name': name,
               'pass': password,
               'form_build_id': form_build_id,
               'form_id': 'user_login',
               'op': 'Log in'}
    logged_in = session.post(
        'http://nycgmc.groupanizer.com/user/login?destination=/', data=payload)
    cookies = logged_in.cookies
    return cookies


def empty_folder(*args):
    '''cleans out folder and redownloads'''
    #!!!TODO: check to see if file exists; if old version, replace, else leave alone
    for folder in args:
        for f in os.listdir(folder):
            file_path = os.path.join(folder, f)
            try:
                if os.path.isfile(file_path) and (file_path.endswith('.pdf') or file_path.endswith('.mp3')):
                    os.unlink(file_path)
            except Exception, e:
                print e


def parse_page(concert_id, session):
    '''parses page and returns list of music links (.pdf)
    and list of video links (.mp4)'''
    sheet_music_links = []
    video_links = []
    recording_links = []
    url = 'http://nycgmc.groupanizer.com/music'
    cookies = login(session, username, password)
    form_build_id, form_token = get_form_params(session, url, cookies)
    print "concert_id:", concert_id
    # song_title_pattern = re.compile('(.+)\([v\d]')
    # song_version_pattern = re.compile('(\d+.\d+)')
    payload = {'terms[]': concert_id,
               'op': 'Filter',
               'form_build_id': form_build_id,
               'form_token': form_token,
               'form_id': 'user_login'
               }
    music_page = session.get(url, data=payload, cookies=cookies)
    soup = BeautifulSoup(music_page.content)
    link_list = [link.get('href') for link in soup.find_all('a')
                 if 'node' in link.get('href')]
     #remove extraneous /node/add link
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
                sheet_music_links.append(
                    (music_link.text, music_link.get('href')))
            elif music_link.get('href').find('youtu') != -1:
                #finds youtube and youtu.be
                video_links.append(music_link.get('href'))
            elif music_link.get('href').endswith('.mp3'):
                recording_links.append(
                    (music_link.text, music_link.get('href')))
    return sheet_music_links, video_links, recording_links, cookies


def write_sheet_music_to_file(session, sheet_music_links, directory_str):
    '''takes as input list of music links and writes all sheet music
        to specified directory_str for that concert period'''
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
        video = yt.filter('mp4')[-1]
        #gets highest video resolution of mp4 format
        fullpath = '{0}{1}.{2}'.format(directory_str, yt.filename, 'mp4')
        print fullpath
        if not isfile(fullpath):
            video.download(directory_str)


def process_recording_links(session, recording_links, directory_str, cookies):
    '''sends recordings and respective directory strings to be written'''
    tenorI_dir = directory_str + 'tenorI/'
    tenorII_dir = directory_str + 'tenorII/'
    baritone_dir = directory_str + 'baritone/'
    bass_dir = directory_str + 'bass/'
    full_dir = directory_str + 'full/'
    for directory in [tenorI_dir, tenorII_dir, baritone_dir,
                      bass_dir, full_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    empty_folder(tenorI_dir, tenorII_dir, bass_dir, full_dir, baritone_dir)
    for recording_link in recording_links:
        fullpath = '{0}{1}'.format(
            directory_str, recording_link[0].replace('/', '_'))
        if not isfile(fullpath):
            if fullpath.lower().find('full') != -1 or\
                    fullpath.lower().find(').mp3') != -1:
                write_recording_to_file(
                    session, recording_link, full_dir, cookies)


def write_recording_to_file(session, link, directory_str, cookies):
    '''downloads all recording sessions to proper directories'''
    #link should be (filename, url)
    new_filename = link[0].replace('/', '_')
    destination = directory_str + new_filename
    response = urllib2.urlopen(link[1])
    song = session.get(session.get(link[1]).content, cookies=cookies)
    f = open(directory_str + new_filename, 'wb')
    f.write(song)
    f.close()
    return


def unshorten_url(url):
    '''takes youtube shortened urls and expands them full form'''
    parsed = urlparse.urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc)
    h.request('HEAD', parsed.path)
    response = h.getresponse()
    if response.status/100 == 3 and response.getheader('Location'):
        return response.getheader('Location')
    else:
        return url


def main():
    concert_dict = {134: 'dublin', 163: 'london_non_bgs', 132: 'st_john'}
    #!!!TODO:  change to be input by user for diff concerts
    session = requests.session()
    for concert_id in concert_dict:
        concert_name = concert_dict[concert_id]
        if os.path.exists('/Users/nicholsp/Dropbox/chorus_music/'):
            #cuz I work on different computers
            base_directory_str = '/Users/nicholsp/Dropbox/chorus_music/'
        else:
            base_directory_str = '/Users/paulnichols/Dropbox/chorus_music/'
        concert_directory_str = base_directory_str + concert_name + '/'
        sheet_music_directory = concert_directory_str + 'sheet_music/'
        choralography_directory = concert_directory_str + 'choralography/'
        recording_directory = concert_directory_str + 'recordings/'
        for directory in [concert_directory_str, sheet_music_directory,
                          choralography_directory, recording_directory]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        empty_folder(concert_directory_str, sheet_music_directory,
                     choralography_directory)
        sheet_music_links, video_links, recording_links, cookies = parse_page(
            concert_id, session)
        write_sheet_music_to_file(
            session, sheet_music_links, sheet_music_directory)
        write_videos_to_file(session, video_links, choralography_directory)
        print 'Finished downloading for concert {0}'.format(concert_name)

if __name__ == '__main__':
    main()
