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

    def collection(self, collection_id, params={}):
        args = ['{}={}'.format(k, v) for k, v in params.items()]
        return EurosportResponse(
            self.session.get(
                '{}/cms/collections/{}?{}'.format(
                    ROOT_URL,
                    collection_id,
                    '&'.join(args)
                )
            ).json()
        )

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

    def find_alias(self, alias_name):
        candidates = list(filter(
            lambda o: o.get('attributes', {}).get('alias') == alias_name,
            self._data.get('included', [])
        ))
        if len(candidates) > 0:
            return candidates[0]
        else:
            return None

    def videos(self, onlyAvailable=True):

        def filterMethod(o):

            if o.get('type') != 'video':
                return False

            availability = o.get('attributes', {}).get('availabilityWindows', [])
            if len(availability) > 0:
                av_window = availability[0]
                av_start = parse_date(av_window['playableStart'])
                # NB Videos continue to be available after 'playableEnd'... *shrug*
                now = datetime.datetime.now(tz.tzutc())
                is_available = av_start <= now
                o['attributes']['isAvailable'] = is_available
                return is_available or not onlyAvailable

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

    def get_included_by_id(self, id):
        candidates = list(filter(
            lambda o: o.get('id') == id,
            self._data.get('included', [])
        ))
        if len(candidates) > 0:
            return candidates[0]
        else:
            return None

    def get_relations(self, relation_type):
        relationships = list(
            filter(
                lambda r: r.get('type') == relation_type,
                self._data.get('relationships')
            )
        )

        return list(
            map(
                lambda r: self.get_included_by_id(r['id']),
                relationships
            )
        )
