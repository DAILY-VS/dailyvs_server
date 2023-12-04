from allauth import utils
from config.settings import base
from config.settings.base import local_settings
from urllib.parse import urlsplit

def monkey_patching():
    def custom_build_absolute_uri(request, location, protocol=None):
        site = local_settings.FRONT_BASE_URL
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            uri = "{domain}{url}".format(
                domain=site,
                url=location,
            )
        else:
            uri = location
        return uri

    utils.build_absolute_uri = custom_build_absolute_uri