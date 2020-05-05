import sys
import os
import requests
from bs4 import BeautifulSoup


def authenticate(username,password):
    authurl = "https://auth.uq.edu.au"

    redirect = requests.get(authurl)
    loginurl = redirect.url
    print(loginurl)

    payload = {
        'username': username,
        'password': password,
        }

    session = requests.Session()
    login = session.post(loginurl, data=payload)
    print(login.url)

    #request = session.get("https://learn.uq.edu.au/webapps/blackboard/execute/announcement?method=search&context=course_entry&course_id=_129055_1&handle=announcements_entry&mode=view")
    #soup = BeautifulSoup(request.text, "html.parser")
    #print(soup)

def main(argv):
    pass


if __name__ == "main":
    main(sys.argv)


#getdocuments():
