from app import wsgi  # noqa
from easycancha.models import Weekday, Sport

for name in Sport.SEED_LIST:
    Sport.objects.get_or_create(name=name)

for number, name in Weekday.NAME_DICT.items():
    Weekday.objects.get_or_create(number=number, defaults=dict(name=name))
