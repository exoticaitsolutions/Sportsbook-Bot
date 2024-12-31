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

def scrap_links_posts():
    links, driver, names = scrapping_pick_of_day_link() 
    link_count = 0 
    comments_list = [] 

    for link, name in zip(links, names):  # Loop over links and names
        driver.get(link)
        link_count += 1  # Increment the counter for each link visited
        print(f"Visited link #{link_count}: {link}")
        time.sleep(5)  # Allow the page to load

        # Scroll the page down gradually
        scroll_pause_time = 5  # Time to wait between scrolls
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Check for "View more comments" button and click it if found
            try:
                view_more_button = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "View more comments")]'))
                )
                view_more_button.click()
                print("Clicked 'View more comments'.")
                time.sleep(2)  # Wait for more comments to load
            except Exception:
                pass  # No "View more comments" button found, continue scrolling

            # Scroll to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            # Check if new content is loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Stop if no new content is loaded
            last_height = new_height

        # Extract comments using your specific `xpath`
        print("Starting to scrape posts...")
        logger.info("Starting to scrape posts...")
        for i in range(1, 100):  # Adjust range as needed
            xpath = f'/html/body/shreddit-app/div[1]/div[1]/div/main/div/faceplate-batch/shreddit-comment-tree/shreddit-comment[{i}]/div[3]'
            
            try:
                # Wait for the comment to appear and retrieve it
                data = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )

                post_text = data.text
                pattern = r"(Record: .+)|(?:Net Units: .+)|(?:ROI: .+)"
                matches = re.findall(pattern, post_text)
                output = "\n".join([match for match in matches if match])

                # if "POTD" in post_text and "Record" in post_text:
                comment_dict = {
                    "url": link,
                    "name": name,  # Add the name here
                    "post": post_text,
                    "data": output
                }
                print("comment_dict : ", comment_dict)
                # assistant_response = chat_gpt_integration(post_text)
                # print("assistant_response : ", assistant_response)
                input_date = re.search(r'\d{1,2}/\d{1,2}/\d{2}', name).group()
                title_date = datetime.strptime(input_date, "%m/%d/%y").strftime("%Y-%m-%d")
                comments_list.append(comment_dict)  # Append this comment's dictionary to the list
                create_reditposts(link, name, post_text, title_date)
                print("Sucessfully data inserted in database")
                logger.info("Sucessfully data inserted in database")

            except Exception as e:
                print(f"No more posts found")
                break  # Break the loop if no further comments are found

    print(f"Total links visited: {link_count}")  # Print the total count after processing all links
    print("\nAll Saved post (Structured as List of Dictionaries):")

    # Save the comments list to a CSV file
    csv_file = "post.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["url", "name", "post", "data"])
        writer.writeheader()  # Write the header row
        writer.writerows(comments_list)  # Write all rows from comments_list

    print(f"\nData saved to {csv_file} successfully!")

    
scrap_links_posts()







