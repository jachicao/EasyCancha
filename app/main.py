from app import wsgi  # noqa
from pytz import timezone
from traceback import print_exc
from django.utils.timezone import localtime
from datetime import datetime as datetime_datetime
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from easycancha.models import RecurrentReservation, OneTimeReservation
from easycancha.tasks import reserve_date, get_next_weekday
from .cipher import AESCipher


def decrypt(string):
    aes = AESCipher()
    return aes.decrypt(string)


HEADLESS = True

chile_timezone = timezone('America/Santiago')


chrome_options = ChromeOptions()

if HEADLESS:
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

driver = Chrome(chrome_options=chrome_options)

for recurrentreservation in RecurrentReservation.objects.select_related(
        'clubsport', 'clubsport__club',
        'clubsport__sport', 'weekday', 'platformuser').iterator():
    clubsport = recurrentreservation.clubsport
    sport = clubsport.sport
    club = clubsport.club
    platformuser = recurrentreservation.platformuser
    weekday = recurrentreservation.weekday
    now = datetime_datetime.now(chile_timezone)
    next_date = \
        get_next_weekday(now, weekday.number).date()
    next_datetime = datetime_datetime(
        next_date.year, next_date.month, next_date.day,
        recurrentreservation.hour,
        recurrentreservation.minute, 0, 0, chile_timezone)
    try:
        reserve_date(
            driver,
            platformuser.username,
            decrypt(platformuser.password),
            sport.name, club.easycancha_id,
            next_datetime, recurrentreservation.duration)
    except Exception as e:
        print(e)
        print_exc()

for onetimereservation in OneTimeReservation.objects.select_related(
        'clubsport', 'clubsport__club',
        'clubsport__sport', 'platformuser').iterator():
    clubsport = onetimereservation.clubsport
    sport = clubsport.sport
    club = clubsport.club
    platformuser = onetimereservation.platformuser
    try:
        reserve_date(
            driver,
            platformuser.username,
            decrypt(platformuser.password),
            sport.name, club.easycancha_id,
            localtime(
                onetimereservation.datetime, chile_timezone),
            onetimereservation.duration)
    except Exception as e:
        print(e)
        print_exc()

driver.quit()
