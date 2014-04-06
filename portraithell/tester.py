import sys
import re
import requests
from StringIO import StringIO
from PIL import Image

from portraithell.detector import BandDetector


RE_YOUTUBE = re.compile(r'youtube.com/.*watch.*v(=|\%3D)([\w_-]+)&?')


def main():
    for url in sys.argv[1:]:
        match = RE_YOUTUBE.search(url)
        if not match:
            print("No match: {}".format(url))
            continue
        youtube_id = match.group(2)
        for i in range(1, 4):
            response = requests.get('http://img.youtube.com/vi/{}/{}.jpg'.format(youtube_id, i))
            image = Image.open(StringIO(response.content))
            detector = BandDetector()
            if detector.check_image(image) is False:
                print("Not vertical!")
                break
        else:
            print("WHOA! {} is a vertical video!".format(url))
    pass

if __name__ == "__main__":
    main()
