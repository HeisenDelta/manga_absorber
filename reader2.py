# Combine all images into one really long image - specifically for manhwa
# Hell yeah, works perfectly

import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import requests

# Global Variables
domain = 'https://ww4.mangakakalot.tv/'
mangaid = 'dr980474/'
manganame = 'Solo Leveling'
lang = 'English'

chapter = 1
full = f'{manganame} Chapters {str(chapter)} ({lang} Edition)'

# Helper functions
def get_pdf_images(full: str, logging = True) -> list:
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

    for image in images_cont: 
        image_link = image.get_attribute('src') if image.get_attribute('src') else image.get_attribute('data-src')
        # image_links.append(image_link)

        image_data = requests.get(image_link, stream = True)
        image_raw = image_data.raw
        if image_data.status_code != 200: raise Exception('The image could not be retrieved')

        image_obj = Image.open(image_raw).convert('RGB')
        images.append(image_obj)

        if logging: print('FINISHED', full, 'Chapter',  page_number)

        page_number += 1

    driver.quit()

    return images


if __name__ == '__main__':
    images = get_pdf_images(full, logging = True)
    for image in images: print(image.size[0], image.size[1])

    widths = list(map(lambda x: x.size[0], images))
    std_width = max(set(widths), key = widths.count)
    images = [image for image in images if image.size[0] == std_width]

    theight = 0
    for image in images: theight += image.size[1]

    master_image = Image.new('RGB', size = (std_width, theight))
    start = 0
    for image in images: 
        master_image.paste(image, (0, start))
        start += image.size[1]

    master_image.save('pdfs/master_image.jpeg', 'JPEG')
