import requests
from bs4 import BeautifulSoup

def get_form_id(url, cookies):
    '''takes url as input and returns form id and form token (if it exists)'''
    page = requests.get(url, cookies=cookies)
    soupped_page = BeautifulSoup(page.content)
    print soupped_page.content
    form_id = soupped_page.select('input[name="form_build_id"]')
    return form_id[0].get('value')
    #p.text[form_id_index:form_id_index+37]

def login():
    # p = requests.get('http://nycgmc.groupanizer.com/user/login?destination=/')
    # form_id_index = p.text.find('id="form-')+4
    form_id = get_form_id('http://nycgmc.groupanizer.com/user/login?destination=/',{})
    payload = {'name' : 'paul.nichols', 
               'pass' : 'Ella27!',
               'form_build_id' : form_id,
               'form_id' : 'user_login', 
               'op' : "Log in"}
    logged_in = requests.post('http://nycgmc.groupanizer.com/user/login?destination=/', data=payload)
    cookies = logged_in.cookies
    return cookies

cookies = login()
# music_page = requests.get('http://nycgmc.groupanizer.com/music', cookies = cookies)
# soupped_page = BeautifulSoup(music_page.content)
print get_form_id('http://nycgmc.groupanizer.com/music', cookies)

def filter_page(*concert_ids):
    for concert in concert_ids:
        payload = {'terms[]' : concert,
                   'op' : 'Filter',
                   'form_build_id' : 'form-7b83873346e4f564c5ed9fc0df651a51',
                   'form_token' : '34f9f6d6ccb8f302d23f2c5c33b16451',
                   'form_id' : 'song_list_filters_form'
                   }



