#!/usr/bin/python3

from bs4 import BeautifulSoup as bs
import subprocess
import time
import requests
import random
import os
import getpass
import datetime
import pykeepass

# -----------------------------------------------------------------------------
# modifications

PROJECT = 'cpp-module-08'
TEAM_ID = '3815675'

# -----------------------------------------------------------------------------
# header

URL = 'https://projects.intra.42.fr/projects/'
JSON = '/slots.json'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'

# -----------------------------------input-------------------------------------

while True:
    try:
        s = input("Starting day (today = 0): ")
        s = (0 if s == '' else int(s))
        e = input("Ending day (Same day = 0): ")
        e = (0 if e == '' else int(e))
        break
    except Exception as error:
        print("Must be an int")

START = datetime.date.today() + datetime.timedelta(days=s)
END = START + datetime.timedelta(days=1+e)

START = str(START)
END = str(END)

print("start:", START, "00:00")
print("end  :", END, "00:00")

# ------------------------------------db-------------------------------------

#if intra.kdbx, ask if use credentials or overwrite them

try:
    USER = input("Username: ") #'username'
    PWD = getpass.getpass() #'*****'
except Exception as error:
    print('Error', error)
    exit()
else:
    print('Password entered: ', end='')
    print(PWD[0], end='')
    if (len(PWD) > 1):
        print("******", end='')
        print(PWD[-1], end='')
    print()
#ask password for db
pykeepass.create_database("intra.kdbx", password="s1mpl3_p4ssw0rd")

# ------------------------------------auth-------------------------------------

def auth():
    # authentication

    SIGN_ORIGIN = 'https://signin.intra.42.fr'
    SIGN_URL = 'https://signin.intra.42.fr/users/sign_in'

    HEADERS = {
        'User-Agent' : USER_AGENT,
        'Origin'     : SIGN_ORIGIN,
        'Referer'    : SIGN_URL
    }

    s = requests.session()
    g = s.get(SIGN_ORIGIN)

    # tokens

    mkra_token = g.cookies['_mkra_ctxt']
    intra_42_token = g.cookies['_intra_42_session_production']
    authenticity_token = bs(g.text, 'html.parser').find('input', {'name' : 'authenticity_token'}).get('value')

    login_payload = {
        'utf8'               : '✓',
        'authenticity_token' : authenticity_token,
        'user[login]'        : USER,
        'user[password]'     : PWD,
        'commit'             : 'Sign+in'
    }

    # request

    login_req = s.post(SIGN_URL, headers=HEADERS, data=login_payload)
    verif = s.get('https://profile.intra.42.fr/users/./locations_stats.json')

    print("intra_42:  ", intra_42_token)
    print("mkra:      ", mkra_token)
    print("auth token:", authenticity_token)
    print("status:    ", login_req.status_code)
    print("logged in: ", verif.status_code == 404)

    if (login_req.status_code != 200 or verif.status_code != 404):
        exit()
    return (s)

# --------------------------------------main-----------------------------------

def clear():
    _ = subprocess.call('clear' if os.name =='posix' else 'cls')

def main():
    s = auth()
    RL = URL + PROJECT + JSON + '?team_id=' + TEAM_ID + '&start=' + START + '&end=' + END
    print(RL)
    while True:
        time.sleep(2)
        clear()
        gget = s.get(RL).json()
        print ("------------------------")
        for page in gget:
            print (page['start'][11:19])
            print (page['end'][11:19])
            print ()
        time.sleep(2)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
