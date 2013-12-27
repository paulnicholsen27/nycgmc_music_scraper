import requests
from bs4 import BeautifulSoup

def get_form_params(url, cookies):
    '''takes url as input and returns form id and form token (if it exists)'''
    form_token = None
    page = requests.get(url, cookies=cookies)
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
    logged_in = requests.post('http://nycgmc.groupanizer.com/user/login?destination=/', data=payload)
    cookies = logged_in.cookies
    return cookies

concert_ids = [85] #will later change to be input by user for diff concerts

def filter_page(concert_ids, cookies):
    '''takes as input one or more concert ids and returns all music
    for that concert period'''
    url = 'http://nycgmc.groupanizer.com/music'
    form_build_id, form_token = get_form_params(url, cookies)
    for concert in concert_ids:
      print "concert:", concert
      payload = {'terms[]' : concert,
                 'op' : 'Filter',
                 'form_build_id' : 'form-69b1dddb1f7871a9324ab3949ffd20cf',
                 'form_token' : '34f9f6d6ccb8f302d23f2c5c33b16451',
                 'form_id' : 'user_login'
                 }
      music_page = requests.get(url, data=payload, cookies=cookies)

# !!! Next step:  Filter concert music.  Currently returning all.  

cookies = login()
print filter_page(concert_ids, cookies)
#Junk Code
    #p.text[form_id_index:form_id_index+37]

# p = requests.get('http://nycgmc.groupanizer.com/user/login?destination=/')
# form_id_index = p.text.find('id="form-')+4

    # music_page = requests.get('http://nycgmc.groupanizer.com/music', cookies = cookies)
