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
