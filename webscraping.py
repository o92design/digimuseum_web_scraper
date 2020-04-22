import os
import requests
from bs4 import BeautifulSoup
import json

time_period = "1800+TO+1829"
time_period = "1830+TO+1849"
time_period = "1850+TO+1869"
time_period = "1870+TO+1899"

time_period = "1900+TO+1929"
time_period = "1930+TO+1949"
time_period = "1950+TO+1969"
time_period = "1970+TO+1989"
time_period = "1990+TO+2099"

time_period_name = time_period.replace("+", "_")
topic = "Ångfartyg"
#topic = "örlogsfartyg"
art_type = "Artdesign"
picture_limit = None

img_server = 'https://mm.dimu.org/image/'

SAVE_FOLDER = 'images'

def main():
    url_search = "https://digitaltmuseum.se/search/?aq=license%3F%3A%22CC+pdm%22%2C%22CC+by%22%2C%22CC+by-sa%22%2C%22zero%22+topic%3A%22" + topic + "%22+media%3F%3A%22image%22+type%3A\"" + art_type + "\"+time%3A%22" + time_period + "%22"
    response = requests.get(url_search)
    soup = BeautifulSoup(response.text, 'lxml')

    number_of_hits_soup = soup.findAll('input', {'type':'hidden', 'id':'js-search-more-other-count'})
    number_of_hits = int(number_of_hits_soup[0].attrs.get('value'))

    print("Got " + str(number_of_hits) + " hits with topic: " + topic + " timeperiod: " + time_period_name)
    url_search = url_search + "&o=0&n=" + str(number_of_hits)

    print("Gathering Pictures from URL:" + url_search)
    response = requests.get(url_search)
    soup = BeautifulSoup(response.text, 'lxml')
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)

    download_images(soup)

def download_images(soup:BeautifulSoup):
    images_objects = soup.find_all('a', {'class':'module__grid'}, limit=picture_limit)
    image_links = []
    for image_identifiers in images_objects:
        image_refs = image_identifiers.find_all('img')
        for image in image_refs:
            image_ref = str(image.get('data-src').replace("?dimension=250x250", ""))
            if image_ref not in image_links:
                image_links.append(image_ref)

    for i, imagelink in enumerate(image_links):
        response = requests.get(imagelink)
        imagename = imagelink.rsplit('/', 1)[1]
        imagepath = SAVE_FOLDER + '/' + topic + '/'
        if art_type != "":
            imagepath = imagepath + art_type + '/' + time_period_name + '/'
        else:
            imagepath = imagepath + '/' + time_period_name + '/'

        if not os.path.exists(imagepath):
            os.makedirs(imagepath)

        with open (imagepath + imagename + '.png', 'wb') as file:
            file.write(response.content)
        print ("[" + str(i+1) + "/" + str(len(image_links)) + "]-" + "Saved image: " + imagelink + " - " + imagepath + imagename + 'png')

    print ("Saved " + str(len(image_links)) + " in folder " + SAVE_FOLDER + '/' + topic + '/' + time_period_name + '/')
if __name__ == "__main__":
    main()
