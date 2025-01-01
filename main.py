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

logger = setup_logging()

def scrap_link():
    links, driver, names = scrapping_pick_of_day_link()
    link_count = 0
    post_list = []

    for link, name in zip(links, names):
        driver.get(link)
        link_count += 1
        print(f"Visited link #{link_count}: {link}")
        logger.info(f"Visited link #{link_count}: {link}")
        time.sleep(5)

        print("Starting to scrape comments with specific XPath...")

        # Scroll settings
        current_height = 0
        scroll_step = 500  # Pixels to scroll in each step
        max_attempts = 500  # Limit scrolling attempts
        processed_xpaths = set()  # Track processed xpaths to avoid duplicates

        for attempt in range(max_attempts):
            # Check for 'View more comments' button
            try:
                view_more_button = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "View more comments")]'))
                )
                if view_more_button:
                    print("View more comments button found. Clicking...")
                    view_more_button.click()
                    time.sleep(2)  # Wait for new comments to load
            except Exception as e:
                print("No 'View more comments' button found. Continuing scrolling...")

            # Scroll down the page
            driver.execute_script(f"window.scrollTo(0, {current_height});")
            time.sleep(1)  # Adjust for slower scrolling

            # Process comments with dynamic XPath
            for i in range(1, 100):  # Adjust range as needed
                xpath = f'/html/body/shreddit-app/div[1]/div[1]/div/main/div/faceplate-batch/shreddit-comment-tree/shreddit-comment[{i}]/div[3]'

                if xpath in processed_xpaths:
                    continue  # Skip already processed xpaths

                try:
                    comment_elements = driver.find_elements(By.XPATH, xpath)
                    if comment_elements:
                        for comment_element in comment_elements:
                            post_text = comment_element.text.strip()

                            post_dict = {
                                "url": link,
                                "name": name,
                                "post": post_text,
                            }
                            logger.info(f"post_dict : {post_dict}")
                            print("\n" + "-" * 80)
                            print(f"post_dict : {post_dict}")
                            print("-" * 80 + "\n")
                            input_date = re.search(r'\d{1,2}/\d{1,2}/\d{2}', name).group()
                            title_date = datetime.strptime(input_date, "%m/%d/%y").strftime("%Y-%m-%d")
                            # assistant_response = chat_gpt_integration(post_text)
                            try:
                                create_reditposts(link, name, post_text, title_date)
                            except:
                                print(f"Error processing during data insertion : {e}")
                            logger.info("Data successfully insert in database")
                            print("Data successfully insert in database")
                            if post_dict not in post_list:  # Avoid duplicate entries
                                post_list.append(post_dict)
                                processed_xpaths.add(xpath)  # Mark as processed

                except Exception as e:
                    print(f"Error processing XPath {xpath}: {e}")
                    continue

            # Increment the scroll position
            current_height += scroll_step
            new_height = driver.execute_script("return document.body.scrollHeight")

            # Stop scrolling if the bottom of the page is reached
            if current_height >= new_height:
                print("Reached the bottom of the page.")
                break

        # Save data to CSV
        csv_file = "posts.csv"
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["url", "name", "post"])
            writer.writeheader()
            writer.writerows(post_list)

    print(f"\nData saved to {csv_file} successfully!")

scrap_link()






