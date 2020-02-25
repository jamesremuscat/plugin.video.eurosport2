# -*- coding: utf-8 -*-

import dateutil
import logging
import requests
import routing
import simplejson
import xbmcaddon

from datetime import date, timedelta
from resources.lib import kodiutils, kodilogging
from resources.lib.eurosport import Eurosport
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory, setContent, setResolvedUrl


ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()

setContent(plugin.handle, 'videos')

token = ADDON.getSetting('eurosport-token')
logger.info('Using token: {}'.format(token))
e = Eurosport(token)


def add_static_index_items(schedule_id):
    schd_item = ListItem('Schedule')
    addDirectoryItem(
        plugin.handle,
        plugin.url_for(
            list_schedule,
            schedule_id=schedule_id
        ),
        schd_item,
        True
    )


def listitem_from_video(schedule, video, include_start_time=False):
    attrs = video['attributes']

    if attrs.get('broadcastType') == 'LIVE':
        title = 'Live: {}'.format(attrs.get('name'))
    else:
        title = attrs.get('name')

    start_time = attrs.get('scheduleStart')
    if include_start_time and start_time:
        parsed_start_time = dateutil.parser.parse(start_time)
        title = '{} {}'.format(
            parsed_start_time.strftime('%H:%M'),
            title.encode('utf-8')
        )

    item = ListItem(title)

    images = video.get(
        'relationships', {}
    ).get(
        'images', {}
    ).get(
        'data', []
    )

    if len(images) > 0:
        image_url = schedule.get_image_url(images[0]['id'])
        item.setArt({
            'thumb': image_url,
            'icon': image_url
        })

    is_available = attrs.get('isAvailable', False)
    is_playable_string = 'true' if is_available else 'false'
    if not is_available:
        title = '[COLOR dimgray]{}[/COLOR]'.format(title)

    labels = {
        'title': title,
        'plot': attrs.get('description'),
        'premiered': attrs.get('scheduleStart'),
        'mediatype': 'video'
    }

    item.setInfo('Video', labels)

    item.setProperty('IsPlayable', is_playable_string)
    item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    item.setProperty('inputstream.adaptive.manifest_type', 'hls')

    return item


def video_sort_key(video, liveFirst=True):
    attrs = video['attributes']
    if liveFirst and attrs.get('broadcastType') == 'LIVE':
        # sort live videos first
        return -1
    return attrs.get('scheduleStart')


@plugin.route('/')
def index():

    schedule = e.schedule()

    schd_obj = schedule.find_alias('schedule')
    if schd_obj:
        add_static_index_items(schd_obj['id'])

    videos = schedule.videos()

    for video in sorted(videos, key=video_sort_key):
        item = listitem_from_video(schedule, video)

        addDirectoryItem(
            plugin.handle,
            plugin.url_for(
                play_video,
                id=video['id']
            ),
            item,
            False,
            len(videos)
        )

    endOfDirectory(plugin.handle)


@plugin.route('/schedule')
def list_schedule():
    schedule_id = plugin.args['schedule_id'][0]

    if 'day' in plugin.args:
        day = plugin.args['day'][0]

        schedule = e.collection(
            schedule_id,
            {
                'include': 'default',
                'pf[day]': day
            }
        )

        videos = schedule.videos(onlyAvailable=False)

        for video in sorted(videos, key=lambda v: video_sort_key(v, False)):
            item = listitem_from_video(schedule, video, include_start_time=True)

            addDirectoryItem(
                plugin.handle,
                plugin.url_for(
                    play_video,
                    id=video['id']
                ),
                item,
                False,
                len(videos)
            )
    else:
        today = date.today()
        for day_idx in range(14):
            day_delta = day_idx - 7
            day = today + timedelta(days=day_delta)

            day_formatted = day.strftime("%Y-%m-%d")
            item = ListItem(day_formatted)
            item.select(day == today)

            addDirectoryItem(
                plugin.handle,
                plugin.url_for(
                    list_schedule,
                    schedule_id=schedule_id,
                    day=day_formatted
                ),
                item,
                True
            )

    endOfDirectory(plugin.handle)


@plugin.route('/play')
def play_video():
    video_id = plugin.args['id'][0]

    playback_info = e.playback_info(video_id)
    stream_url = playback_info.get(
        'data', {}
    ).get(
        'attributes', {}
    ).get(
        'streaming', {}
    ).get(
        'hls', {}
    ).get('url')

    # Create a playable item with a path to play.
    play_item = ListItem(path=stream_url)
    # Pass the item to the Kodi player.
    setResolvedUrl(plugin.handle, True, listitem=play_item)


def run():
    plugin.run()
