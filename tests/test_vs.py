import os

from PIL import Image

from portraithell import Detector


def images_from_path(path):
    imgs = []
    for filename in os.listdir(path):
        if filename.endswith('.jpg'):
            imgs.append(Image.open(os.path.join(path, filename)))
    return imgs


def test_portrait():
    detector = Detector()
    # portraits
    img_path = os.path.join(os.path.dirname(__file__), 'imgs')
    base_path = os.path.join(img_path, 'port/')
    for set_path in os.listdir(base_path):
        imgs = images_from_path(os.path.join(base_path, set_path))
        assert detector.detect(imgs), \
            'Failed to detect portait orientation ' + set_path


def test_landscape():
    detector = Detector()
    img_path = os.path.join(os.path.dirname(__file__), 'imgs')
    # landscapes
    base_path = os.path.join(img_path, 'land/')
    for set_path in os.listdir(base_path):
        assert not detector.detect(
            images_from_path(os.path.join(base_path, set_path))
        ), 'Failed to detect landscape orientation' + set_path
