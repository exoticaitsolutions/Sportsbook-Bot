import os
import re
import csv
import time
from datetime import datetime
from chatgpt_intigration import chat_gpt_integration
from database_configration import create_reditposts
from utils import scrapping_pick_of_day_link, setup_logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

from webdriver_configration import driver_confrigration

# Load environment variables from the .env file
load_dotenv()

logger = setup_logging()

CSV_FILE_NAME = os.getenv('CSV_FILE_NAME')

def scrap_link():
    links, driver, names = scrapping_pick_of_day_link()

    post_list = []
    link_count = 0

    for link, name in zip(links, names):
        driver.get(link)
        link_count += 1
        logger.info(f"Visited link #{link_count}: {link}")
        time.sleep(5)

        logger.log("Starting to scrape comments with slow incremental scrolling...")

        # Scroll settings
        current_height = 0
        scroll_step = 900  # Pixels to scroll in each step
        max_attempts = 500  # Limit scrolling attempts for slow scrolling
        processed_xpaths = set()  # Track processed xpaths to avoid duplicates

        for attempt in range(max_attempts):
            # Incrementally scroll down the page
            driver.execute_script(f"window.scrollTo(0, {current_height});")
            time.sleep(1)  # Pause slightly between scrolls for a smooth experience

            # Check for 'View more comments' button
            try:
                view_more_button = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "View more comments")]'))
                )
                if view_more_button:
                    view_more_button.click()
                    time.sleep(2)  # Wait for new comments to load
            except Exception as e:
                print("No 'View more comments' button found. Continuing scrolling...")

            # Increment the scroll position
            current_height += scroll_step
            new_height = driver.execute_script("return document.body.scrollHeight")

            # Stop scrolling if the bottom of the page is reached
            if current_height >= new_height:
                break

        # Scrape comments after slow scrolling is complete
        for i in range(1, 100):  # Adjust range as needed
            xpath = f'/html/body/shreddit-app/div[1]/div[1]/div/main/div/faceplate-batch/shreddit-comment-tree/shreddit-comment[{i}]/div[3]'

            if xpath in processed_xpaths:
                continue  # Skip already processed xpaths

            try:
                comment_elements = driver.find_elements(By.XPATH, xpath)
                if comment_elements:
                    for comment_element in comment_elements:
                        post_text = comment_element.text.strip()
                        if name and post_text:
                            # Extract date from `name` and format it
                            input_date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2}', name)
                            title_date = None
                            if input_date_match:
                                input_date = input_date_match.group()
                                title_date = datetime.strptime(input_date, "%m/%d/%y").strftime("%Y-%m-%d")

                            # Create the dictionary for the current comment
                            post_dict = {
                                "url": link,
                                "name": name,
                                "post": post_text,
                            }
                            logger.info(f"post_dict: {post_dict}")

                            # Save data to the database
                            create_reditposts(link, name, post_text, title_date)
                            logger.info("Data successfully inserted into the database")
                            # assistant_response = chat_gpt_integration(post_text)      #uncomment for chatgpt integrations

                            # Avoid duplicate entries in the list
                            if post_dict not in post_list:
                                post_list.append(post_dict)
                                processed_xpaths.add(xpath)  # Mark this XPath as processed
                        else:
                            print("No valid data found for this comment.")
                else:
                    print("No comments found for the given XPath.")
            except Exception as e:
                logger.info(f"Error processing XPath {xpath}: {e}")
                continue

    # Save all scraped data to a CSV file
    with open(CSV_FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["url", "name", "post"])
        writer.writeheader()
        writer.writerows(post_list)

    logger.info(f"\nData saved to {CSV_FILE_NAME} successfully!")

scrap_link()








