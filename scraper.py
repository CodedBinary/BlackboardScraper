import requests
from bs4 import BeautifulSoup
import base64


#getdocuments():



username = ""
password = ""

#password = base64.b64encode(password)
payload = {
    'login': 'Login',
    'action': 'login',
    'user_id': username,
    'encoded_pw': password,
    }
url = 'https://learn.uq.edu.au/webapps/login/'

session = requests.Session()
session.post(url, data=payload)

request = session.get("https://learn.uq.edu.au/webapps/blackboard/execute/announcement?method=search&context=course_entry&course_id=_129055_1&handle=announcements_entry&mode=view")
soup = BeautifulSoup(request.text, "html.parser")
print(soup)
