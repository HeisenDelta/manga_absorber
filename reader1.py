# For mangakakalot

import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import requests
import os
import glob
import shutil


# Clear image cache
for cached_file in glob.glob('image_cache/*'): os.remove(cached_file)

# Global Variables
domain = 'https://ww4.mangakakalot.tv/'
mangaid = 'dr980474/'
manganame = 'Solo Leveling'
lang = 'English'

chapter_min = 1
chapter_max = 1
assert chapter_min <= chapter_max

if chapter_min == chapter_max: full = f'{manganame} Chapter {str(chapter_min)} ({lang} Edition)'
else: full = f'{manganame} Chapters {str(chapter_min)}-{str(chapter_max)} ({lang} Edition)'

# Helper functions
def get_pdf_images(chapter: str, full: str, logging = True, cache = False) -> list:
    base_url = urllib.parse.urljoin(domain, f'chapter/manga-{mangaid}/')
    url = urllib.parse.urljoin(base_url, f'chapter-{str(chapter)}')

    # Webdriver initialization
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options = chrome_options)
    driver.get(url)

    images = []
    page_number: int = 1

    img_cont = driver.find_element('xpath', "//div[@id='vungdoc']")
    images_cont = img_cont.find_elements('xpath', "./img[@class='img-loading']") 

    for image in images_cont[1: -1]: 
        image_link = image.get_attribute('src') if image.get_attribute('src') else image.get_attribute('data-src')
        # image_links.append(image_link)

        image_data = requests.get(image_link, stream = True)
        image_raw = image_data.raw
        if image_data.status_code != 200: raise Exception('The image could not be retrieved')                       # In case of error

        if cache:
            image_file_name = f'image_cache/{full} Chapter {str(chapter)} Page {str(page_number)}.jpg'
            with open(image_file_name, 'wb') as image_file: shutil.copyfileobj(image_raw, image_file)

            image_obj = Image.open(image_file_name).convert('RGB')

        images.append(image_obj)
        if logging: print('FINISHED', full, 'Chapter', chapter, 'Page', page_number)

        page_number += 1

    driver.quit()

    return images


if __name__ == '__main__':
    images = []

    # Doesn't work if cache = False, i.e. doesn't work unless the image is downloaded first
    for chapter in range(chapter_min, chapter_max + 1): 
        images.extend(get_pdf_images(chapter, full, logging = True, cache = True))

    images[0].save(r'pdfs/' + full + '.pdf', save_all = True, append_images = images[1:])



