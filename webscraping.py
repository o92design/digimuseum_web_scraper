import os
import requests
from bs4 import BeautifulSoup
import json

#time_period = "1800+TO+1829"
#time_period = "1830+TO+1849"
#time_period = "1850+TO+1869"
#time_period = "1870+TO+1899"

#time_period = "1900+TO+1929"
time_period = "1930+TO+1949"
#time_period = "1950+TO+1969"
#time_period = "1970+TO+1989"
#time_period = "1990+TO+2099"

time_period_name = time_period.replace("+", "_")
topic = "Ångfartyg"
#topic = "örlogsfartyg"
art_type = "Artdesign"
picture_limit = None

img_server = 'https://mm.dimu.org/image/'

SAVE_FOLDER = 'images'

class information:
    def __init__(self, id, group, year, topic, art_type):
        self.id = id
        self.group = group
        self.year = year
        self.topic = topic
        self.art_type = art_type

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
    images_objects = soup.findAll('a', {'class':'module__grid'}, limit=picture_limit)
    image_links = []
    names = []

    for name in images_objects:
        attr_href = str(name.attrs.get('href'))
        if attr_href.count("search") < 1:
            append_name = attr_href.replace("/ritning", "").replace("/", "")
            names.append(append_name)

    for name in names:
        image_links.append("https://digitaltmuseum.se/" + name)

    for i, imagelink in enumerate(image_links):
        response = requests.get(imagelink)
        imagename = imagelink.rsplit('/', 1)[1]
        imagepath = SAVE_FOLDER + '/' + topic + '/'
        if art_type != "":
            imagepath = imagepath + art_type + '/' + time_period_name + '/' + imagename + "/"
        else:
            imagepath = imagepath + '/' + time_period_name + '/' + imagename + "/"

        soup = BeautifulSoup(response.text, 'lxml')
        article_metadata = soup.findAll('section', {'class':'article__metadata'})

        if not os.path.exists(imagepath):
            os.makedirs(imagepath)

        if os.path.exists(imagepath + imagename + '_metadata' + '.xml'):
            os.remove(imagepath + imagename + '_metadata' + '.xml')

        with open(imagepath + imagename + '_metadata' + '.xml', 'a', encoding="utf-8") as file:
                file.write("<metadata>")
                file.write("\n")

        for article_index, article in enumerate(article_metadata):
            with open(imagepath + imagename + '_metadata_' + str(article_index+1) + '.xml', 'w', encoding="utf-8") as file:
                file.write(str(article))

            with open(imagepath + imagename + '_metadata' + '.xml', 'a', encoding="utf-8") as file:
                file.write(str(article))
                file.write("\n")

        with open(imagepath + imagename + '_metadata' + '.xml', 'a', encoding="utf-8") as file:
                file.write("</metadata>")
        meta_content = soup.findAll('meta')
        img_content = None
        for meta in meta_content:
            if meta.attrs.get('property') == "og:image":
                img_content = meta.attrs.get('content')
                break

        response = requests.get(img_content)

        with open (imagepath + imagename + '.png', 'wb') as file:
            file.write(response.content)

        with open (imagepath[:-1] + '.png', 'wb') as file:
            file.write(response.content)

        print ("[" + str(i+1) + "/" + str(len(image_links)) + "]-" + "Saved image: " + imagelink + " - " + imagepath + imagename + '.png')



    print ("Saved " + str(len(image_links)) + " in folder " + SAVE_FOLDER + '/' + topic + '/' + time_period_name + '/')
if __name__ == "__main__":
    main()
