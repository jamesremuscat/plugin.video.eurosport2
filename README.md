# Eurosport Player proof-of-concept for Kodi

**You must have a valid subscription to Eurosport Player in order to use this
plugin.**

This plugin is not created, supported or endorsed by Eurosport.

## Installation

The [usual procedure for Kodi plugins](https://kodi.wiki/view/HOW-TO:Install_add-ons_from_zip_files) -
ultimately, you should end up with a copy of this repo in your Kodi plugins
directory (`~/.kodi/addons` or similar).

This plugin requires:

- dateutil
- inputstreamhelper
- requests
- InputStream Adaptive

If you don't already have them, you can install them via this plugin's
information page within Kodi.

## Authentication

I've not even attempted to solve the "login requires captcha" problem, so you
need to log in to the Eurosport Player website and copy your authentication
token to the plugin settings.

- Log in to www.eurosportplayer.com
- Open up your browser's dev tools and view cookies
- The cookie you want is called `st` - it should have a value starting `eyJ0`
- Copy that value into the addon settings - either via the Kodi web interface's
  "send text to Kodi" option or by editing the file
  `~/.kodi/userdata/addon_data/plugin.video.eurosport2/settings.xml`

As far as I can tell, that token is valid for the lifetime of your subscription
and doesn't expire (but I could be wrong).

## Limitations

- Only videos available on the current "schedule" page are listed; I've not yet
made any attempt to access video on demand or previously scheduled events.
- Error handling is minimal, if extant at all.
- I don't make much use of Eurosport's video categorisation system; might be quite
nice to do so.
- Probably more that I can't think of right now

This is just a proof-of-concept (mostly written because I wanted to watch the
WEC stream without connecting a laptop to my TV) so there are many ways it could
be improved / expanded!

## Acknowledgements

Inspiration taken from
[the original Eurosport Player plugin by JinRonin](
  https://github.com/JinRonin/plugin.video.eurosportplayer
); the `2` in this plugin's name is to distinguish it from that original.

## License

This addon is licensed under the MIT licence - see `LICENSE` for details.
