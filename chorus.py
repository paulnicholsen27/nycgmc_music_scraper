import requests
<<<<<<< HEAD
import urllib
import urllib2
import re
import os
from os.path import isfile, join

from bs4 import BeautifulSoup


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

def empty_folder(directory):
  for f in os.listdir(directory):
    file_path = os.path.join(directory, f)
    try:
      if os.path.isfile(file_path):
        os.unlink(file_path)
    except Exception, e:
      print e

def get_music(concert_id, session,directory):
    '''takes as input one concert id and returns all music
    for that concert period'''
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
    link_list = [link.get('href') for link in soup.find_all('a') if 'node' in link.get('href')] #contains extraneous /node/add link
    try:
      link_list.remove('/node/add')
    except:
      pass
    for link in link_list:
      url = 'http://nycgmc.groupanizer.com' + link
      song_page = session.get(url)
      song_page_soup = BeautifulSoup(song_page.content)

      music_links = {music_link.text:music_link.get('href') for music_link in song_page_soup.find_all('a') if music_link.get('href').endswith('.pdf')}
      for filename in music_links:
        new_filename = filename.replace('/', '_')
        print new_filename
        # song_version = song_version_pattern.search(new_filename)
        # song_title = song_title_pattern.search(new_filename)
        # if song_version and song_title:
        #   song_version = song_version.group(0)
        #   song_title = song_title.group(1)
        # else:
        #   song_title = new_filename
        # print song_title, song_version

        f = open(directory + new_filename, 'wb')
        f.write(session.get(music_links[filename]).content)
        f.close()

      
# def get_files(directory):
  # existing_files: [ f for f in os.listdir(directory) if isfile(join(directory, f)) and f.endswith('.pdf')]

def main():
  CONCERT_ID = [130] #will later change to be input by user for diff concerts
  session = requests.session()
  directory = '/Users/nicholsp/Dropbox/music_files/'
  empty_folder(directory)
  get_music(CONCERT_ID,session, directory)

main()

print 'finished'
