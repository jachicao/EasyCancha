from app import wsgi  # noqa
from os import environ
from easycancha.models import Weekday, Sport, Platform, PlatformUser

for name in Sport.SEED_LIST:
    Sport.objects.get_or_create(name=name)

for number, name in Weekday.NAME_DICT.items():
    Weekday.objects.get_or_create(number=number, defaults=dict(name=name))

for name in Platform.SEED_LIST:
    platform, _ = Platform.objects.get_or_create(name=name)

    if 'EASYCANCHA_USERNAME' in environ and 'EASYCANCHA_PASSWORD' in environ:
        PlatformUser.objects.get_or_create(
            username=environ['EASYCANCHA_USERNAME'], defaults=dict(
                password=environ['EASYCANCHA_PASSWORD'],
                platform_id=platform.id
            ))
