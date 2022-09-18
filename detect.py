import cv2
import pytesseract
import requests
import numpy as np

from internet.largecats import findSpeechBubbles, tesseract


def get_text(image_link: str) -> None:
    # req = urllib.request.urlopen(image_link)
    # arr = np.asarray(bytearray(req.read()), dtype = np.uint8)
    # img = cv2.imdecode(arr, -1)

    resp = requests.get(image_link, stream = True).raw
    imgdata = np.asarray(bytearray(resp.read()), dtype = np.uint8)
    img = cv2.imdecode(imgdata, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 19))

    dilation = cv2.dilate(thresh, rect_kernel, iterations = 1)
    contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    img_copy = img.copy()

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        rect = cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 8)

        cropped = img_copy[y: y + h, x: x + w]
        text = pytesseract.image_to_string(cropped)
        print(text)

    cv2.imshow('image', img_copy)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


images = [
    'https://cm.blazefast.co/cd/58/cd58789f697efe862f6c7d931d63ba52.jpg', 
    'https://cm.blazefast.co/e7/58/e7587a6d3788a0137dc9948aef644c66.jpg', 
    'https://cm.blazefast.co/cf/39/cf39cbc12aca7ee2c62f5a96fb50880b.jpg', 
    'https://cm.blazefast.co/90/b7/90b78357c1227be46bd12f20787eb7f2.jpg', 
    'https://cm.blazefast.co/58/43/584335c0921afacf980e9a0a322ad2b5.jpg', 
    'https://cm.blazefast.co/e2/40/e2409af4607aeb4bb68eb61862cc090e.jpg', 
    'https://cm.blazefast.co/08/f3/08f3fbe33bbe66dd2e769026146d54f2.jpg', 
    'https://cm.blazefast.co/05/8f/058f1977f03b6595c1976a438306fbb6.jpg', 'https://cm.blazefast.co/59/bb/59bb22cd65070684ab066b384d7e175a.jpg', 'https://cm.blazefast.co/18/97/1897b8aa1d92d380591087057d3e2d69.jpg', 'https://cm.blazefast.co/e7/18/e7182c7612c9979ea477ffb146f3a820.jpg', 'https://cm.blazefast.co/21/d1/21d171ae540402afe007600e2b9eeb71.jpg', 'https://cm.blazefast.co/d6/21/d6212ad1a55c24bf1f27660290f86a1f.jpg', 'https://cm.blazefast.co/45/5f/455f7070abbf5f9c9c9e78b2c7ed0b82.jpg', 'https://cm.blazefast.co/55/84/5584dd432f527966dd199194430c2e54.jpg', 'https://cm.blazefast.co/db/cf/dbcf310be31ba298708854439327fcba.jpg', 'https://cm.blazefast.co/7e/9d/7e9d7240a455f7613c8b6d6389ed24c9.jpg', 'https://cm.blazefast.co/65/49/65498b7884684d47490a096c9b795d4f.jpg', 'https://cm.blazefast.co/6a/20/6a20bc0eb260ea57fdb9a42a70c3fc07.jpg', 'https://cm.blazefast.co/e9/c6/e9c662acfcd2acbb495d9ff1c52cec5d.jpg', 'https://cm.blazefast.co/78/70/78708e345a77934400b512bd4ba397c4.jpg', 'https://cm.blazefast.co/41/87/4187becb17d53db83e4bf6ab0463497c.jpg', 'https://cm.blazefast.co/81/7e/817e1424bafbaf877e4b5e51a2bad322.jpg', 'https://cm.blazefast.co/a0/60/a0607b8b3d8d2dea92a962631fcdf46e.jpg', 'https://cm.blazefast.co/55/33/5533f2ae9c86328afad5dad38ceff245.jpg', 'https://cm.blazefast.co/78/3e/783e80a1015200a9136312d7f26a9ff5.jpg', 'https://cm.blazefast.co/c4/b0/c4b0496a7eb95d02bb28588a19b2918a.jpg', 'https://cm.blazefast.co/97/bc/97bc676ccbd11d43a1c5747afd8aef10.jpg', 'https://cm.blazefast.co/86/6b/866b9fbc976b0339c2f548494ceb8e82.jpg', 'https://cm.blazefast.co/ed/b5/edb577b215f0d7a181b26181200c00aa.jpg', 'https://cm.blazefast.co/93/9b/939b478b9995221910c2b182e7e19402.jpg', 'https://cm.blazefast.co/27/25/2725250ea76bc790702ae005c7555baf.jpg', 'https://cm.blazefast.co/c5/0b/c50b086130c0492f9de59004ebcf50fb.jpg', 'https://cm.blazefast.co/76/f6/76f6a850b035321256b550958f1ee0e8.jpg', 'https://cm.blazefast.co/84/72/8472b8e8c73128cbde951d6bbb27a21b.jpg', 'https://cm.blazefast.co/97/8d/978d6bd567b5497c163b64b1dc144747.jpg', 'https://cm.blazefast.co/be/ed/beedff111f95bf319cf4e3cffeec6663.jpg', 'https://cm.blazefast.co/60/3d/603d3c1a6606fdd07b0955b7df54aca2.jpg', 'https://cm.blazefast.co/12/f5/12f590c0bf21d030594c86c98a0b9ea9.jpg', 'https://cm.blazefast.co/de/ae/deaeefcc8477b128af4ec3ada9a986f3.jpg', 'https://cm.blazefast.co/92/9f/929fedc70989e2c92b1779cf29bd5bfb.jpg', 'https://cm.blazefast.co/55/9c/559c9ad30259b22409e2d6b93b70248c.jpg', 'https://cm.blazefast.co/3f/d3/3fd37109c8f7d6e386e2419b07f5dbf4.jpg', 'https://cm.blazefast.co/1f/c6/1fc64d520c1a5989d3b28d09d5270298.jpg', 'https://cm.blazefast.co/6e/ef/6eefd6bc994a3800e7bd33c6809195b6.jpg']

# get_text('https://cm.blazefast.co/d6/21/d6212ad1a55c24bf1f27660290f86a1f.jpg')
# get_text2('test_image.jpeg')
