from selenium import webdriver
from selenium.webdriver.chrome.options import Options


WAIT = 10 # seconds


def find_element(find_from, element):
    return find_from.find_element(element[0], element[1])

def find_elements(find_from, element):
    return find_from.find_elements(element[0], element[1])

def start_browser(URL):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome("./chromedriver", options=chrome_options)
    driver.maximize_window()
    driver.implicitly_wait(WAIT)
    driver.get(URL)
    return driver
