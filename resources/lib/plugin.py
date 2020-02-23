# -*- coding: utf-8 -*-

import routing
import logging
import requests
import simplejson
import xbmcaddon
from resources.lib import kodiutils
from resources.lib import kodilogging
from resources.lib import wecapp
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory, setContent, setResolvedUrl


ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()


@plugin.route('/')
def index():

    setContent(plugin.handle, 'videos')

    videos = []

    for video in sorted(videos, key=lambda v: (v['date'], v['time'])):
        item = ListItem(
            label=video['title']
        )

        item.setArt({
            'thumb': video['thumb'],
            'icon': video['thumb']
        })

        item.setProperty('IsPlayable', 'true')

        item.setInfo('video', {'mediatype': 'video'})

        addDirectoryItem(
            plugin.handle,
            plugin.url_for(
                play_video,
                url=video['url']
            ),
            item,
            False,
            len(videos)
        )

    endOfDirectory(plugin.handle)


@plugin.route('/play')
def play_video():
    path = plugin.args['url'][0]
    # Create a playable item with a path to play.
    play_item = ListItem(path=path)
    # Pass the item to the Kodi player.
    setResolvedUrl(plugin.handle, True, listitem=play_item)


def run():
    plugin.run()
