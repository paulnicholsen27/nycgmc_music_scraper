import requests
import urllib, urllib2
import os
from bs4 import BeautifulSoup

CONCERT_ID = [130] #will later change to be input by user for diff concerts
SESSION = requests.session()

def get_form_params(url, cookies):
    '''takes url as input and returns form id and form token (if it exists)'''
    form_token = None
    page = SESSION.get(url, cookies=cookies)
    soupped_page = BeautifulSoup(page.content)
    form_build_id = soupped_page.select('input[name="form_build_id"]')
    form_token = soupped_page.select('input[name="form_token"]')
    if form_token:
      return form_build_id[0].get('value'), form_token[0].get('value')
    else:
      return form_build_id[0].get('value'), None

def login(name='paul.nichols', password='Ella27!'):
    '''takes as input a username and password, returns logged-in cookie'''
    form_build_id, form_token = get_form_params('http://nycgmc.groupanizer.com/user/login?destination=/',{})
    print "form build_id:", form_build_id
    print "form_token:", form_token
    payload = {'name' : name, 
               'pass' : password,
               'form_build_id' : form_build_id,
               'form_id' : 'user_login', 
               'op' : 'Log in'}
    logged_in = SESSION.post('http://nycgmc.groupanizer.com/user/login?destination=/', data=payload)
    cookies = logged_in.cookies
    return cookies


def get_music(concert_id):
    '''takes as input one concert id and returns all music
    for that concert period'''
    url = 'http://nycgmc.groupanizer.com/music'
    cookies = login()
    form_build_id, form_token = get_form_params(url, cookies)
    print "concert_id:", concert_id
    payload = {'terms[]' : concert_id,
               'op' : 'Filter',
               'form_build_id' : form_build_id,
               'form_token' : form_token,
               'form_id' : 'user_login'
               }
    music_page = SESSION.get(url, data=payload, cookies=cookies)
    soup = BeautifulSoup(music_page.content)
    link_list = [link.get('href') for link in soup.find_all('a') if 'node' in link.get('href')] #contains extraneous /node/add link
    try:
      link_list.remove('/node/add')
    except:
      pass
    for link in link_list:
      url = 'http://nycgmc.groupanizer.com' + link
      song_page = SESSION.get(url)
      song_page_soup = BeautifulSoup(song_page.content)

      music_links = {music_link.text:music_link.get('href') for music_link in song_page_soup.find_all('a') if music_link.get('href').endswith('.pdf')}
      for filename in music_links:
        cleaned_filename = filename.replace('/', '_')
        if not os.path.exists('/Users/paulnichols/Dropbox/music_files'):
            os.makedirs('/Users/paulnichols/Dropbox/music_files')
        filepath = os.path.join('/Users/paulnichols/Dropbox/music_files', cleaned_filename)
        with open(filepath, 'w+') as f:
          f.write(SESSION.get(music_links[filename]).content)
      


get_music(CONCERT_ID)
print 'finished'
