import datetime

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import os
if os.name == 'nt':
    import pywintypes, win32file, win32con

all_fetched = False
current_page = 1
images_dir_name = 'images'
last_page_file_name = 'last.page'
last_page_file_name_dist = last_page_file_name + '.dist'

if not os.path.exists(images_dir_name):
    os.makedirs(images_dir_name)

if os.path.exists(last_page_file_name):
    last_page_file = open(last_page_file_name)
    current_page = int(last_page_file.readline())
    last_page_file.close()
elif os.path.exists(last_page_file_name_dist):
    last_page_dist_file = open(last_page_file_name_dist)
    current_page = int(last_page_dist_file.readline())
    last_page_dist_file.close()

while all_fetched is False:
    source = 'https://spotlight.it-notes.ru/page/' + str(current_page)
    request = requests.get(source)

    if request.status_code == 200:
        soup = BeautifulSoup(request.text, "html.parser")

        articles = soup.findAll('article')
        for article in articles:
            image = article.find('img', {'class': ('thumbnail', 'wp-post-image')})
            image_link = image['src'].replace('-1024x576', '')
            file_name = image_link.split("/")[-1]

            date = article.find('span', {'class': 'date'})
            datetime_obj = datetime.datetime.strptime(date.contents[0], '%d-%b-%Y')
            download_path = os.path.join(images_dir_name, file_name)

            urllib.request.urlretrieve(image_link, download_path)

            if os.name == 'nt':
                wintime = pywintypes.Time(time.mktime(datetime_obj.utctimetuple()))
                winfile = win32file.CreateFile(
                    download_path, win32con.GENERIC_WRITE,
                    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                    None, win32con.OPEN_EXISTING,
                    win32con.FILE_ATTRIBUTE_NORMAL, None)

                win32file.SetFileTime(winfile, wintime, None, None)

                winfile.close()

            os.utime(download_path, (time.mktime(datetime_obj.utctimetuple()), time.mktime(datetime_obj.utctimetuple())))

            last_page_file = open(last_page_file_name, 'w+')
            last_page_file.write(str(current_page))
            last_page_file.close()

            print("Downloaded: " + file_name + " from page " + str(current_page))

        current_page += 1
    else:
        all_fetched = True

print('All wallpapers scrapped!')