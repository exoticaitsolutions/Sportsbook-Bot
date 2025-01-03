from datetime import datetime
import os
import re
import time
import logging
from database_configration import get_last_row
from urls import WEBSITE_URL, WEBSITE_URL_SEARCH
from webdriver_configration import driver_confrigration
from selenium.webdriver.common.by import By


all_texts = []
potd_all_texts = []
href_links = []

def setup_logging():
    log_dir = "logs_detail"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate a log file name based on the current date
    log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # Set up logging configuration
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,  # Set the logging level to INFO
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode='a'  # Append to the existing log file
    )
    logger = logging.getLogger()
    return logger

logger = setup_logging()

def scroll_down(driver):
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")

def scrapping_pick_of_day_link():
    logger.info("Starting the scrapping process.")
    
    driver = driver_confrigration()
    logger.info("Driver configuration completed.")
    
    driver.get(WEBSITE_URL)
    logger.info(f"Navigated to {WEBSITE_URL}.")
    time.sleep(10)
    driver.get(WEBSITE_URL_SEARCH)
    time.sleep(10)
    previous_length = 0
    data_base_last_title_date = get_last_row()
    if data_base_last_title_date is None:
        logger.info("No date found, skipping comparison.")
        
    while True:
        link_elements  = driver.find_elements(By.XPATH, "//a[@class='absolute inset-0']")
        if len(link_elements) == previous_length:
            break
        else:
            previous_length = len(link_elements)
    for potd in link_elements:
            text = potd.get_attribute("aria-label")  # Fetch the aria-label text
            
            if text and text not in all_texts:  # Avoid duplicates
                all_texts.append(text)
                if "Pick of the Day -" in text:
                    input_date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2}', text)
                    input_date = input_date_match.group()
                    title_date = datetime.strptime(input_date, "%m/%d/%y").strftime("%Y-%m-%d")
                    title_date_obj = datetime.strptime(title_date, "%Y-%m-%d").date()
                    print("title_date_obj : ", title_date_obj)
                    print("data_base_last_title_date : ", data_base_last_title_date)
                    if data_base_last_title_date == title_date_obj:
                        break
                    href = potd.get_attribute("href")
                    potd_all_texts.append(text)
                    href_links.append(href)

    scroll_down(driver)
    time.sleep(6)  # Pause to allow the page to load more elements
    logger.info(f"length of picks of day names : ------ {len(potd_all_texts)}")
    logger.info(f"length of links : ------ {len(href_links)}")
    return href_links,driver, potd_all_texts
