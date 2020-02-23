import datetime
import requests

from dateutil.parser import parse as parse_date
from dateutil import tz

ROOT_URL = 'https://eu3-prod-direct.eurosportplayer.com'


class Eurosport(object):
    def __init__(self, token):
        self.token = token
        self.session = requests.Session()

        self.session.headers = {
            'cookie': 'st={}'.format(token)
        }

    def schedule(self):
        return EurosportResponse(
            self.session.get(
                '{}/cms/routes/schedule?include=default'.format(ROOT_URL)
            ).json()
        )

    def playback_info(self, video_id):
        return self.session.get(
            '{}/playback/v2/videoPlaybackInfo/{}?usePreAuth=true'.format(
                ROOT_URL,
                video_id
            )
        ).json()


class EurosportResponse(object):
    def __init__(self, data):
        self._data = data

    def videos(self, onlyAvailable=True):

        def filterMethod(o):

            if o.get('type') != 'video':
                return False
            if not onlyAvailable:
                return True

            availability = o.get('attributes', {}).get('availabilityWindows', [])
            if len(availability) > 0:
                av_window = availability[0]
                av_start = parse_date(av_window['playableStart'])
                av_end = parse_date(av_window['playableEnd'])
                now = datetime.datetime.now(tz.tzutc())
                return av_start <= now <= av_end

            return False

        return filter(
            filterMethod,
            self._data.get('included', [])
        )

    def images(self):
        return filter(
            lambda o: o.get('type') == 'image',
            self._data.get('included', [])
        )

    def get_image_url(self, id):
        wanted_images = list(
            filter(
                lambda i: i['id'] == id,
                self.images()
            )
        )
        if len(wanted_images) > 0:
            return wanted_images[0]['attributes'].get('src')
        return None
