from os import environ
from time import sleep
from pytz import timezone
from dotenv import load_dotenv
from datetime import datetime as datetime_datetime, timedelta
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options as ChromeOptions
load_dotenv()

HEADLESS = True

RESERVATIONS = [
    {
        'weekday': 'Miércoles',
        'hour': '12:00',
        'duration': '60',
    },
    {
        'weekday': 'Jueves',
        'hour': '12:00',
        'duration': '60',
    },
    {
        'weekday': 'Viernes',
        'hour': '17:00',
        'duration': '60',
    },
    {
        'weekday': 'Sábado',
        'hour': '11:00',
        'duration': '60',
    },
]

URL_LOGIN = 'https://www.easycancha.com/login'
URL_RESERVATIONS = 'https://www.easycancha.com/bookings'
URL_CLUB = 'https://www.easycancha.com/book/clubs/59/sports'

LOGIN_USERNAME_XPATH = '//input[@type="email"]'
LOGIN_PASSWORD_XPATH = '//input[@type="password"]'
LOGIN_BUTTON_XPATH = '//button[text()="Ingresar"]'

RESERVATIONS_XPATH = '//div[contains(text(), "Mis reservas")]'
HAS_RESERVATION_XPATH = '//span[contains(text(), "reserva activa")]'
SHOW_MORE_RESERVATIONS = '//button[contains(text(), "Cargar más reservas")]'
RESERVATION_CARDS_XPATH = '//div[@class="bookingContainer"]'
RESERVATION_RELATIVE_DATE_XPATH = './div[3]/div[1]'
RESERVATION_RELATIVE_HOUR_XPATH = './div[3]/div[2]'

LOADING_XPATH = '//div[@class="loading"]'

SPORT_TYPE_XPATH = '//div[contains(text(), "{type}")]/../../..'

MODAL_XPATH = '//div[@class="modal-dialog modal-md"]'
MONTH_YEAR_XPATH = '//th[@colspan="5"]'
MONTH_XPATH = '//span[text()="{month_name}"]/..'
DAY_XPATH = '//span[text()="{day_number}"]/..'
SELECT_TIME_XPATH = '//select[@id="time"]'
OPTION_TIME_VALUE_FORMAT = 'string:{hour}:{minute}:{second}'
SELECT_DURATION_XPATH = '//*[@id="timespan"]'
OPTION_DURATION_VALUE_FORMAT = 'number:{duration}'
SEARCH_XPATH = '//button[text()="Buscar"]'

NOT_FOUND_XPATH = '//div[contains(text(), "No se encontraron resultados '\
    'en el horario que buscas, pero te sugerimos alguno de'\
    ' los siguientes horarios:")]'

COURT_OPTIONS_XPATH = '//strong[text()="RESERVAR"]/..'
RESERVE_XPATH = '//button[text()="Reservar"]'

RESERVE_DONE_XPATH = '//*[contains(text(), "¡ Tu reserva ya está lista !")]'

WAIT_TIME = 60

chile_timezone = timezone('Chile/Continental')

MONTH_TRANSFORMATION = {
    1: 'enero',
    2: 'febrero',
    3: 'marzo',
    4: 'abril',
    5: 'mayo',
    6: 'junio',
    7: 'julio',
    8: 'agosto',
    9: 'septiembre',
    10: 'octubre',
    11: 'noviembre',
    12: 'diciembre'
}

MONTH_NAME_TO_NUMBER = {
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12,
}

WEEKDAY_TRANSFORMATION = {
    'Lunes': 0,
    'Martes': 1,
    'Miércoles': 2,
    'Jueves': 3,
    'Viernes': 4,
    'Sábado': 5,
    'Domingo': 6
}


def has_element_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
        return True
    except Exception as e:
        return False


def is_displayed(element):
    if element.is_displayed():
        return True
    try:
        attribute = element.get_attribute('style')
        return 'display: block' in attribute
    except Exception as e:
        return False


def has_element_displayed_by_xpath(driver, xpath):
    try:
        element = driver.find_element_by_xpath(xpath)
        return is_displayed(element)
    except Exception as e:
        return False


def wait_element_displayed(element):
    counter = 0
    while (not is_displayed(element)) and counter < WAIT_TIME:
        sleep(0.1)
        counter += 0.1
    return is_displayed(element)


def wait_loading_by_xpath(driver, xpath):
    element = driver.find_element_by_xpath(xpath)
    counter = 0
    started = False
    while counter < WAIT_TIME:
        is_disp = is_displayed(element)
        if not started:
            started = is_disp

        if started:
            if not is_disp:
                break

        sleep(0.1)
        counter += 0.1

    sleep(2)


def wait_element_displayed_by_xpath(driver, xpath):
    element = WebDriverWait(driver, WAIT_TIME).until(
        expected_conditions.presence_of_element_located((
            By.XPATH, xpath)))
    return wait_element_displayed(element)


def click_element_by_xpath(driver, xpath):
    element = driver.find_element_by_xpath(xpath)
    try:
        element.click()
    except Exception as e:
        print(e)
        driver.execute_script('arguments[0].click();', element)


def select_option_by_xpath(driver, xpath, value):
    element = driver.find_element_by_xpath(xpath)
    Select(element).select_by_value(value)


def login(driver, username, password):
    user_element = driver.find_element_by_xpath(LOGIN_USERNAME_XPATH)
    user_element.clear()
    user_element.send_keys(username)
    password_element = driver.find_element_by_xpath(LOGIN_PASSWORD_XPATH)
    password_element.clear()
    password_element.send_keys(password)
    click_element_by_xpath(driver, LOGIN_BUTTON_XPATH)
    wait_loading_by_xpath(driver, LOADING_XPATH)


def reserve_date(driver, sport_type, datetime, duration):
    if datetime - datetime_datetime.now(chile_timezone) > timedelta(weeks=1):
        return

    EASYCANCHA_USERNAME = environ['EASYCANCHA_USERNAME']
    EASYCANCHA_PASSWORD = environ['EASYCANCHA_PASSWORD']
    # login
    driver.get(URL_LOGIN)

    while has_element_by_xpath(driver, LOGIN_USERNAME_XPATH):
        login(driver, EASYCANCHA_USERNAME, EASYCANCHA_PASSWORD)

    # check for old reservations
    driver.get(URL_RESERVATIONS)
    if has_element_displayed_by_xpath(driver, LOADING_XPATH):
        wait_loading_by_xpath(driver, LOADING_XPATH)

    sleep(2)

    if has_element_by_xpath(driver, SHOW_MORE_RESERVATIONS):
        click_element_by_xpath(driver, SHOW_MORE_RESERVATIONS)

    for element in driver.find_elements_by_xpath(RESERVATION_CARDS_XPATH):
        date_text = element.find_element_by_xpath(
            RESERVATION_RELATIVE_DATE_XPATH).get_attribute('innerText').strip()
        day_name, day_number, month_name, year_number = date_text.split(' ')
        month_number = MONTH_NAME_TO_NUMBER.get(month_name)
        hour_text = element.find_element_by_xpath(
            RESERVATION_RELATIVE_HOUR_XPATH).get_attribute('innerText').strip()
        hour, minute = hour_text.split(':')
        reservation_datetime = datetime_datetime(
            int(year_number), int(month_number), int(day_number), int(hour),
            int(minute), 0, 0, chile_timezone)
        if reservation_datetime - datetime < timedelta(minutes=duration) or \
                datetime - reservation_datetime < timedelta(minutes=duration):
            return

    # reserve new
    driver.get(URL_CLUB)

    sport_xpath = SPORT_TYPE_XPATH.format(type=sport_type)
    wait_element_displayed_by_xpath(driver, sport_xpath)
    click_element_by_xpath(driver, sport_xpath)
    wait_element_displayed_by_xpath(driver, MODAL_XPATH)
    click_element_by_xpath(driver, MONTH_YEAR_XPATH)
    month_xpath = MONTH_XPATH.format(
        month_name=MONTH_TRANSFORMATION.get(datetime.month))
    wait_element_displayed_by_xpath(driver, month_xpath)
    click_element_by_xpath(driver, month_xpath)
    day_xpath = DAY_XPATH.format(
        day_number=str(datetime.day).zfill(2))
    wait_element_displayed_by_xpath(driver, day_xpath)
    click_element_by_xpath(driver, day_xpath)
    select_option_by_xpath(driver, SELECT_TIME_XPATH,
                           OPTION_TIME_VALUE_FORMAT.format(
                               hour=str(datetime.hour).zfill(2),
                               minute=str(datetime.minute).zfill(2),
                               second=str(datetime.second).zfill(2)
                           ))
    select_option_by_xpath(driver, SELECT_DURATION_XPATH,
                           OPTION_DURATION_VALUE_FORMAT.format(
                               duration=duration
                           ))

    click_element_by_xpath(driver, SEARCH_XPATH)
    wait_loading_by_xpath(driver, LOADING_XPATH)
    if has_element_by_xpath(driver, LOGIN_USERNAME_XPATH):
        login(driver, EASYCANCHA_USERNAME, EASYCANCHA_PASSWORD)
        wait_loading_by_xpath(driver, LOADING_XPATH)

    if has_element_by_xpath(driver, NOT_FOUND_XPATH):
        return

    wait_element_displayed_by_xpath(driver, COURT_OPTIONS_XPATH)
    click_element_by_xpath(driver, COURT_OPTIONS_XPATH)
    wait_element_displayed_by_xpath(driver, RESERVE_XPATH)
    click_element_by_xpath(driver, RESERVE_XPATH)
    wait_element_displayed_by_xpath(driver, RESERVE_DONE_XPATH)


def get_next_weekday(date, weekday):
    difference = weekday - date.weekday()
    days_ahead = difference % 7
    if difference == 0:
        days_ahead = 7
    return date + timedelta(days_ahead)


for obj in RESERVATIONS:
    weekday_number = WEEKDAY_TRANSFORMATION[obj['weekday']]
    next_date = get_next_weekday(datetime_datetime.now(
        chile_timezone), weekday_number).date()
    hour, minute = obj['hour'].split(':')
    next_datetime = datetime_datetime(
        next_date.year, next_date.month, next_date.day,
        int(hour), int(minute), 0, 0, chile_timezone)
    chrome_options = ChromeOptions()
    if HEADLESS:
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    driver = Chrome(chrome_options=chrome_options)
    try:
        reserve_date(driver, 'Tenis', next_datetime, int(obj['duration']))
    except Exception as e:
        print(e)
    driver.quit()
