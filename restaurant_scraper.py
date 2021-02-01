import argparse

import math
 
import review_scraper 
import helper
from selenium.webdriver.common.by import By

import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger('restaurant_scraper')

URL = 'https://www.tripadvisor.co.uk/Restaurants-g186338-London_England.html'
NEXT_BTN = (By.CSS_SELECTOR, 'a.nav.next.rndBtn.ui_button.primary.taLnk')
COOKIES= (By.ID, "_evidon-accept-button")
LAST_PAGE = (By.CSS_SELECTOR, "a.pageNum.taLnk")
RESTAURANT_LIST = (By.ID, "taplc_location_reviews_list_resp_rr_resp_0")
RESTAURANTS = (By.CSS_SELECTOR, "a._15_ydu6b")


def main(max_resto_page, max_review_page):
    
    driver = helper.start_browser(URL)
    
    # cookie button
    helper.find_element(driver, COOKIES).click()
    
    # Find the last page number
    last_page = helper.find_elements(driver, LAST_PAGE)[-1]
    pages = int(last_page.get_attribute("data-page-number"))
    logger.info("found %s pages in total" % pages)
    
    curr_page = 1
    
    
    while True:
        logger.info("Scraping page %s" % curr_page) 
          
        if curr_page > max_resto_page:
            break
        
        urls = [x.get_attribute("href") for x in helper.find_elements(driver, RESTAURANTS)]
        logger.info("%s restaurants found", len(urls))
    
        
        for url in urls:
            review_scraper.main(url, max_review_page)
            
        logger.info("Page ready")
        if curr_page == pages:
            break
        else:
            next_page = helper.find_element(driver, NEXT_BTN)
            driver.get(next_page.get_attribute("href"))
            curr_page += 1
    
    driver.close()
    logger.info("Scraping finished")
 


if __name__ == "__main__":
    try:
        
        max_resto_page = 1
        max_review_page = 1
    
        # required arg
        parser = argparse.ArgumentParser()
        parser.add_argument('--max_resto', required=True)
        parser.add_argument('--max_review', required=True)
        args = parser.parse_args()

        max_resto_page = math.ceil(int(args.max_resto)/30)
        max_review_page = math.ceil(int(args.max_review)/10)
        
        logger.info("max_resto_page: %s pages in total" % max_resto_page)     
        logger.info("max_rev_page: %s pages in total" % max_review_page)   
         
        main(max_resto_page, max_review_page)
        
        exit(0)
        
    except Exception as ex:
        # output error, and return with an error code
        print (ex)

