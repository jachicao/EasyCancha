from os import environ
from time import sleep
from pytz import timezone
from dotenv import load_dotenv
from datetime import datetime as datetime_datetime, timedelta
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
load_dotenv()

LOGIN_USERNAME_XPATH = '//input[@type="email"]'
LOGIN_PASSWORD_XPATH = '//input[@type="password"]'
LOGIN_BUTTON_XPATH = '//button[text()="Ingresar"]'

LOADING_XPATH = '//div[@class="loading"]'

SPORT_TYPE_XPATH = '//div[contains(text(), "{type}}")]/../../..'

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

TENIS_COURT_XPATH = '//strong[text()="RESERVAR"]/..'
RESERVE_XPATH = '//button[text()="Reservar"]'

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
        driver.execute_script('arguments[0].click();', element)


def select_option_by_xpath(driver, xpath, value):
    element = driver.find_element_by_xpath(xpath)
    Select(element).select_by_value(value)


def login(driver, username, password):
    driver.find_element_by_xpath(LOGIN_USERNAME_XPATH).send_keys(
        username)
    driver.find_element_by_xpath(LOGIN_PASSWORD_XPATH).send_keys(
        password)
    click_element_by_xpath(driver, LOGIN_BUTTON_XPATH)


def reserve_date(sport_type, datetime, duration):
    if datetime - datetime_datetime.now() > timedelta(weeks=1):
        raise Exception('Time exceeds a week')
        return
    EASYCANCHA_USERNAME = environ['EASYCANCHA_USERNAME']
    EASYCANCHA_PASSWORD = environ['EASYCANCHA_PASSWORD']

    driver = Chrome()
    driver.get('https://www.easycancha.com/login')

    login(driver, EASYCANCHA_USERNAME, EASYCANCHA_PASSWORD)

    driver.get('https://www.easycancha.com/book/clubs/59/sports')

    wait_loading_by_xpath(driver, LOADING_XPATH)
    click_element_by_xpath(driver, SPORT_TYPE_XPATH.format(type=sport_type))
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
        driver.quit()
        return

    click_element_by_xpath(driver, TENIS_COURT_XPATH)
    wait_element_displayed_by_xpath(driver, RESERVE_XPATH)
    click_element_by_xpath(driver, RESERVE_XPATH)

    sleep(5000)

    driver.quit()


reserve_date('Tenis', datetime_datetime(2018, 9, 16, 8, 0, 0), 90)
