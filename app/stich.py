from __future__ import print_function
import os
import glob
from PIL import Image

def generate(dir):
    files = glob.glob(dir + '/*')
    resultHeight = int(round(len(files) / 15 * 100))
    result = Image.new("RGB", (1500, resultHeight))

    for index, file in enumerate(files):
      path = os.path.expanduser(file)
      img = Image.open(path)
      img.thumbnail((100, 100), Image.ANTIALIAS)
      x = index // 2 * 100
      y = index % 2 * 100
      w, h = img.size
      result.paste(img, (x, y, x + w, y + h))

    result.save(os.path.expanduser(dir + 'result.jpg'))

    return dir + 'result.jpg'
