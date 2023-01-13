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

PROJECT = '42cursus-computorv1'
TEAM_ID = '4548004'
DBPWD   = 's1mpl3_p4ssw0rd'

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

# ------------------------------------auth-------------------------------------

USER = ''
PWD = ''

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
    print("auth token:", authenticity_token)
    print("status:    ", login_req.status_code)
    print("logged in: ", verif.status_code == 404)

    if (login_req.status_code != 200 or verif.status_code != 404):
        s.close()
        return (None)
    return (s)

# ------------------------------------db-------------------------------------

#if intra.kdbx, ask if use credentials or overwrite them

def save_creds():
    global USER
    global PWD

    try:
        USER = input("Username: ") #'username'
        PWD  = getpass.getpass() #'*****'
        session = auth()
        while (not session):
            print("Sorry but couldn't login with those credentials")
            USER = input("Username: ")
            PWD  = getpass.getpass()
            session = auth()
    except Exception as error:
        print('Error', error)
        exit()
    else:
        print('Password entered: ', end='')
        print(PWD[0], end='')
        print("******" + PWD[-1]) if (len(PWD) > 1) else print()
        save_db = ' '
        while (save_db not in {'', 'Y', 'y', 'n', 'N'}):
            save_db = input('Save credentials in a keepass database (intra.kdbx) [Y/n] ')
        if (save_db not in {'', 'Y', 'y'}):
            USER = None
            PWD  = None
            return (session)
        if (not os.path.isfile('intra.kdbx')):
            #create db
            kp = pykeepass.create_database("intra.kdbx", password=DBPWD)
        else:
            #add to db
            kp = pykeepass.PyKeePass("intra.kdbx", password=DBPWD)
            #delete before adding if entry already exists
            entry = kp.find_entries(username=USER, first=True)
            while (entry):
                entry = kp.find_entries(username=USER, first=True)
                kp.delete_entry(entry)
        kp.add_entry(kp.root_group, 'intra', USER, PWD)
        kp.save()
    USER = None
    PWD  = None
    return (session)

def creds():
    global USER
    global PWD

    if (os.path.isfile('intra.kdbx')):
        creds = ' '
        while (creds not in {'', 'Y', 'y', 'n', 'N'}):
            creds = input('Use credentials of the database intra.kdbx [Y/n] ')
        if (creds in {'', 'Y', 'y'}):
            try:
                kp = pykeepass.PyKeePass("intra.kdbx", password=DBPWD)
                username = input('username: ')
                while (not kp.find_entries(username=username, first=True)):
                    print("entry doesn't exists")
                    username = input('username: ')
                USER = kp.find_entries(username=username, first=True)
                PWD  = USER.password
                USER = USER.username
                session = auth()
                USER = None
                PWD  = None
                if (not session):
                    print("Cannot login with credentials, please verify the database")
                    exit()
                return (session)
            except Exception as error:
                print('Error', error)
                return (save_creds())
        else:
            #add to db
            return (save_creds())
    else:
        #create db
        return (save_creds())

# --------------------------------------main-----------------------------------

def clear():
    _ = subprocess.call('clear' if os.name =='posix' else 'cls')

def show_slots(gget):
    print ("\n----------- SLOTS -------------")
    for page in gget:
        print (page['start'][11:19])
        print (page['end'][11:19], end="\n\n")

def main():
    s = creds()
    if (not s):
        return
    RL = URL + PROJECT + JSON + '?team_id=' + TEAM_ID + '&start=' + START + '&end=' + END
    print(RL)
    gold = s.get(RL).json()
    show_slots(gold)
    while True:
        time.sleep(2)
        gget = s.get(RL).json()
        if (gold != gget):
            clear()
            show_slots(gget)
            gold = gget
            time.sleep(2)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
