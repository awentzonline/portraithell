from gevent.monkey import patch_all; patch_all()  # no qa

import re
from StringIO import StringIO

import gevent
import requests
from gevent.pool import Group
from gevent.queue import Queue
from PIL import Image

import portraithell
from .detector import Detector


class TargetVideo(object):
    def __init__(self, youtube_id, reddit_permalink):
        self.reddit_permalink = reddit_permalink
        self.youtube_id = youtube_id
        self.frames = []

    @property
    def frame_urls(self):
        return [
            'http://img.youtube.com/vi/{}/{}.jpg'.format(self.youtube_id, i)
            for i in range(1, 4)
        ]

    @property
    def youtube_url(self):
        return 'https://www.youtube.com/watch?v=' + self.youtube_id

    @property
    def reddit_url(self):
        return 'http://www.reddit.com' + self.reddit_permalink

    def __unicode__(self):
        return 'Video: {}, {}'.format(self.youtube_url, self.reddit_url)


def scrape_reddit(youtube_interest_q, delay=10):
    reddit_url = 'http://www.reddit.com/domain/youtube.com/new/.json'
    # this also includes youtube attribution links
    re_youtube = re.compile(r'youtube.com/.*watch.*v(=|\%3D)([\w_-]+)&?')
    seen_ids = set()
    headers = {
        'User-Agent': 'portrait-video-hater/{} /u/gifhell'.format(
            portraithell.__version__
        )
    }
    while True:
        print len(seen_ids)
        response = requests.get(reddit_url, headers=headers)
        data = response.json()
        try:
            items = data['data']['children']
        except KeyError:
            print 'Reddit error:', response.status_code
            print response.content
            continue
        for item in items:
            item_data = item['data']
            youtube_url = item_data['url']
            match = re_youtube.search(youtube_url)
            if not match:
                print 'No match:' + youtube_url
                continue
            youtube_id = match.group(2)
            if youtube_id in seen_ids:
                continue
            target_video = TargetVideo(youtube_id, item_data['permalink'])
            youtube_interest_q.put(target_video)
            seen_ids.add(youtube_id)
        gevent.sleep(delay)


def download_youtube_thumbs(youtube_interest_q, detector_input_q):
    for target_video in youtube_interest_q:
        urls = target_video.frame_urls
        #print "Downloading frames for {}".format(target_video.reddit_id)
        for url in urls:
            #print url
            response = requests.get(url)
            image = Image.open(StringIO(response.content))
            target_video.frames.append(image)
        detector_input_q.put(target_video)


def detect_bad_videos(detector_input_q, bad_video_q):
    detector = Detector()
    for target_video in detector_input_q:
        if detector.detect(target_video.frames):
            bad_video_q.put(target_video)


def bad_video_fanout(bad_video_q, out_qs):
    for bad_video in bad_video_q:
        for q in out_qs:
            q.put(bad_video)


def post_to_tumblr(tumblr_q):
    for video in tumblr_q:
        print("Posting to tumblr: {}".format(video))


def post_reddit_response(video_q):
    for video in video_q:
        print("Making a polite message on reddit: {}".format(video))


def debug_results(bad_video_q):
    for video in bad_video_q:
        print unicode(video)


def run_troller():
    youtube_interest_q = Queue()
    detector_input_q = Queue()
    bad_video_q = Queue()
    tumblr_q = Queue()
    reddit_q = Queue()
    conf = [
        (scrape_reddit, youtube_interest_q),
        (download_youtube_thumbs, youtube_interest_q, detector_input_q),
        (detect_bad_videos, detector_input_q, bad_video_q),
        (debug_results, bad_video_q),
        (post_to_tumblr, tumblr_q),
        (post_reddit_response, reddit_q),
        (bad_video_fanout, bad_video_q, (tumblr_q, reddit_q)),
    ]
    group = Group()
    for args in conf:
        group.spawn(*args)
    try:
        while True:
            gevent.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run_troller()
