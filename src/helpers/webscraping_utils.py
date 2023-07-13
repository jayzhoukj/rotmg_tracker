from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def click_button(driver, xpath, wait_duration=10):
    elem = WebDriverWait(driver, wait_duration).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                xpath
            )
        )
    )

    elem.click()

    return


def send_inputs(driver, xpath, input_value, wait_duration=10):
    elem = WebDriverWait(driver, wait_duration).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                xpath
            )
        )
    )

    elem.send_keys(Keys.CONTROL, 'A')
    elem.send_keys(input_value)

    return


def get_text(driver, xpath, wait_duration=10):
    try:
        elem = WebDriverWait(driver, wait_duration).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    xpath
                )
            )
        )

        output = elem.text

    except:
        output = 'N/A'

    return output


def get_attribute(driver, xpath, attribute, wait_duration=10):
    elem = WebDriverWait(driver, wait_duration).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                xpath
            )
        )
    )

    return elem.get_attribute(attribute)


