import csv
from pathlib import Path

import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger('restaurant_scraper')


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import helper

OUTPUT_PATH= 'output/'

COOKIES= (By.ID, "_evidon-accept-button")
CURR_PAGE_NUM =  (By.CSS_SELECTOR, "a.pageNum.current")
MORE_BTN = (By.CSS_SELECTOR, "span.taLnk.ulBlueLinks")
NEXT_BTN = (By.CSS_SELECTOR, "a.nav.next")
LAST_PAGE = (By.CSS_SELECTOR, "a.pageNum.last")
ALL_LANGS = (By.ID, "filters_detail_language_filterLang_ALL")
LOADING_DIV = (By.ID, "taplc_hotels_loading_box_rr_resp_0")
REVIEW_LIST = (By.ID, "taplc_location_reviews_list_resp_rr_resp_0")
REVIEWS = (By.CSS_SELECTOR, "div.ui_column.is-9")
SCORE = (By.XPATH, ".//span[contains(@class, 'ui_bubble_rating bubble_')]")
DATE = (By.CSS_SELECTOR, "span.ratingDate")
TITLE = (By.CSS_SELECTOR, "span.noQuotes")
REVIEW_TEXT = (By.CSS_SELECTOR, "p.partial_entry")
REVIEW_LANG = (By.CSS_SELECTOR, "div.prw_reviews_google_translate_button_hsx")
RESTAURANT_NAME = (By.CSS_SELECTOR, "h1._3a1XQ88S")

class more_loads_full_reviews(object):
    def __init__(self, locator):
        self.locator = locator
    def __call__(self, driver):
        try:
            button = helper.find_element(driver, self.locator)
            text = button.text
            if text == 'Show less':
                return True
            button.click()
            return False
        except Exception as e:
            logger.debug("%s", str(e))
            return False


def get_language(review):
    lang = "en" #assume English
    lang_divs = helper.find_elements(review, REVIEW_LANG)
    if len(lang_divs) > 0:
        button = lang_divs[0]
        span = button.find_elements_by_tag_name("span")[0]
        url = span.get_attribute("data-url")
        index = url.find("sl=")
        if index != -1:
            lang = url[index+3: index+5]

    return lang

def main(URL, max_review_page):

    driver = helper.start_browser(URL)
    
    # cookie button
    helper.find_element(driver, COOKIES).click()
    
    
    # Find the restaurant name 
    res_name = helper.find_element(driver, RESTAURANT_NAME).text
    
    
    # Prepare CSV file
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

    csvFile = open(OUTPUT_PATH + res_name + ".csv", "w", newline='', encoding="utf-16")
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(['Score','Date','Title','Review', 'Language'])  

    # Get reviews in all languages (wait for load)
    helper.find_element(driver, ALL_LANGS).click()
    WebDriverWait(driver, helper.WAIT).until(EC.invisibility_of_element_located(LOADING_DIV))
    

    
    # Find the last page number
    last_page = helper.find_element(driver, LAST_PAGE)
    pages = int(last_page.get_attribute("data-page-number"))
    
    curr_page = 1


    while True:

        # Make sure all assumptions hold
        page = helper.find_element(driver, CURR_PAGE_NUM)
        page_number = page.get_attribute("data-page-number")
        assert curr_page == int(page_number)
        assert helper.find_element(driver, ALL_LANGS).get_attribute("checked") == "true"
        
        if curr_page > max_review_page:
            break

        # Load and get all reviews
        WebDriverWait(driver, 30).until(more_loads_full_reviews(MORE_BTN))
        review_list = helper.find_element(driver, REVIEW_LIST)
        reviews = helper.find_elements(review_list, REVIEWS)

        for review in reviews:
            
            # Read the interesting review information
            score_span = helper.find_element(review, SCORE)
            score = score_span.get_attribute("class").split("_")[3]
            date = helper.find_element(review, DATE).get_attribute("title")
            title = helper.find_element(review, TITLE).text
            text = helper.find_element(review, REVIEW_TEXT).text.replace("\n", "")
            lang = get_language(review)
            # Save to CSV
            csvWriter.writerow((score, date, title, text, lang))

        if curr_page == pages or curr_page == max_review_page:
            break
        else:
            next_page = helper.find_element(driver, NEXT_BTN)
            driver.get(next_page.get_attribute("href"))
            curr_page += 1

    # Close CSV file and browser
    csvFile.close()
    driver.close()
    logger.info("Scraping finished")