import glob
from PIL import Image, ImageDraw
import imageio.v2 as imageio
from skimage.color import rgb2gray, label2rgb
from skimage.feature import canny
from skimage.morphology import dilation
from skimage.measure import label, regionprops
from scipy import ndimage
import numpy as np
import re


def do_boxes_overlap(a, b, padding):
    return (a[0] < b[2] + padding and a[2] + padding > b[0] and a[1] < b[3] + padding and a[3] + padding > b[1])

def merge_boxes(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))

numbers = re.compile(r'(\d+)')
def numerical_sort(a):
    parts = numbers.split(a)
    parts[1::2] = map(int, parts[1::2])
    return parts

def add_margin(pillow_image, top, right, bottom, left, color):
    width, height = pillow_image.size
    nwidth = width + left + right
    nheight = height + top + bottom
    result = Image.new(pillow_image.mode, (nwidth, nheight), color)
    result.paste(pillow_image, (left, top))
    return result

# https://maxhalford.github.io/blog/comic-book-panel-segmentation/

def process_one_image(PATH: str, show = False):
    images = []
    image = imageio.imread(PATH)

    # Image.fromarray(image).show()

    grayscale = rgb2gray(image)
    # Image.fromarray((grayscale * 255).astype('uint8'), 'L').show()

    edges = canny(grayscale)
    thick_edges = dilation(dilation(edges))
    segmentation = ndimage.binary_fill_holes(thick_edges)
    
    labels = label(segmentation)
    # Image.fromarray(np.uint8(label2rgb(labels, bg_label = 0) * 255)).show()

    regions = regionprops(labels)
    panels = []

    for region in regions:
        for i, panel in enumerate(panels):
            if do_boxes_overlap(region.bbox, panel):
                panels[i] = merge_boxes(panel, region.bbox)
                break
        else: panels.append(region.bbox)

    for i, bbox in reversed(list(enumerate(panels))):
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if area < 0.01 * image.shape[0] * image.shape[1]: del panels[i]

    if show:
        panel_image = np.zeros_like(labels)
        for i, bbox in enumerate(panels, start = 1):
            panel_image[np.r_[bbox[1]:bbox[3], bbox[0]:bbox[2]]] = i
        print(panel_image[:1000])

        Image.fromarray(label2rgb(panel_image, bg_label = 0).astype('uint8')).show()

    pillow_image = Image.open(PATH).convert('RGB')

    for panel in panels:
        cropped_image = pillow_image.crop((panel[1], panel[0], panel[3], panel[2]))
        images.append(cropped_image)

    return images


def process_more_images() -> list:
    images = []

    for image_file in sorted(glob.glob('image_cache/*'), key = numerical_sort):
        images.extend(process_one_image(image_file))

        print('FINISHED', image_file)

    return images

def get_cropped(PATH: str, area: tuple):
    image = Image.open(PATH).convert('RGB')
    cropped_image = image.crop(area)
    return cropped_image

def add_rectangle(PATH: str, area: tuple):
    image = Image.open(PATH).convert('RGB')

    rect = ImageDraw.Draw(image)
    rect.rectangle(((area[0], area[1]), (area[2] - area[0], area[3] - area[1])), outline = '#00ff00')

    return image


def segment_whitespace(PATH: str):
    image = imageio.imread(PATH)
    grayscale = rgb2gray(image)

    edges = canny(grayscale)
    thick_edges = dilation(dilation(edges))
    segmentation = ndimage.binary_fill_holes(thick_edges)
    
    labels = label(segmentation)
    # Image.fromarray(np.uint8(label2rgb(labels, bg_label = 0) * 255)).show()

    in_process = False
    start = -1
    regions = []

    for lidx in range(labels.shape[0]): 
        if in_process:
            if np.sum(labels[lidx]) == 0: 
                regions.append((start, lidx))
                in_process = False
        else: 
            if np.sum(labels[lidx]) > 0: 
                start = lidx
                in_process = True

    return regions

# Newest segmenter (also the most promising)
def segment_whitespace_v2(PATH: str, FORMAT = True, PADDING = 0):
    image = imageio.imread(PATH)
    grayscale = rgb2gray(image)

    edges = canny(grayscale)
    thick_edges = dilation(dilation(edges))
    segmentation = ndimage.binary_fill_holes(thick_edges)
    
    labels = label(segmentation)
    # Image.fromarray(np.uint8(label2rgb(labels, bg_label = 0) * 255)).show()

    regions = regionprops(labels)
    panels = []

    for region in regions:
        for i, panel in enumerate(panels):
            if do_boxes_overlap(region.bbox, panel, padding = PADDING):
                panels[i] = merge_boxes(panel, region.bbox)
                break
        else: panels.append(region.bbox)

    # panel_image = np.zeros_like(labels)
    # for i, bbox in enumerate(panels, start = 1):
    #     panel_image[bbox[0]: bbox[2], bbox[1]:bbox[3]] = i
    # Image.fromarray((label2rgb(panel_image, bg_label = 0) * 255).astype('uint8')).show()

    assert [panels[i][0] > panels[i - 1][1] for i in range(1, len(panels))].count(True) == len(panels) - 1

    if FORMAT:
        # 1. The image height has to be less than 4/3 the width
        # 2. The image height has to be at least the same as the width

        image_width = image.shape[1]
        min_height = (4 / 3) * image_width

        pages = [[panels[0][0], panels[0][2]]]

        for pidx in range(1, len(panels)):
            if panels[pidx][2] - panels[pidx][0] < 0.15 * image_width: pages[-1][1] = panels[pidx][2]
            else: 
                if panels[pidx][2] - pages[-1][0] > min_height: pages.append([panels[pidx][0], panels[pidx][2]])
                else: pages[-1][1] = panels[pidx][2]
    
        return pages

    return panels


if __name__ == '__main__':
    
    # images = process_more_images()
    # images = process_one_image('pdfs/master_image.jpeg', show = False)
    # images[0].save(r'pdfs/Solo Leveling Chapter 1 (English Edition) Formatted.pdf', save_all = True, append_images = images[1:])

    regions = segment_whitespace('pdfs/master_image.jpeg')
    images = []
    for region in regions:
        cropped_image = get_cropped('pdfs/master_image.jpeg', (0, region[0], 720, region[1]))
        images.append(cropped_image)

    images[0].save(r'pdfs/Solo Leveling Chapter 1 (English Edition) Formatted 1.pdf', save_all = True, append_images = images[1:])
