# -*- coding: utf-8 -*-

import argparse
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os 

# Initialize a global variable for the WebDriver
driver = ''

# Function to create the WebDriver instance
def create_driver(username, cookie, option):
    global driver

    # Configure Chrome options, including a custom extension
    options = webdriver.ChromeOptions()
    # Add headless mode and disable GPU
    options.add_argument('--window-position=-32000,-32000')
    options.add_extension(r"Old-Twitter-Layout-2023.crx")

    service = Service(ChromeDriverManager().install())
    # Create the WebDriver instance with the configured options
    driver = webdriver.Chrome(service=service, options=options)

    # Navigate to Twitter and set the authentication cookie
    driver.get('https://twitter.com/')
    driver.add_cookie({'name': 'auth_token', 'value': cookie, 'domain': '.twitter.com',
                       'secure': True, 'path': '/', })
    
    driver.get(f"https://twitter.com/{username}/{option}")
    
    

# Function to scrape followers or following
def scrape_users(option):
    start_time = time.time()
    
    final_located = False
    data = [
        ['Name', 'Username']  # Translated variable names
    ]

    # Get the number of followers or following
    time.sleep(5)
    user_count = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, f'//*[@id="profile-stat-{option}-value"]')))
    user_count = user_count.text

    len_names = 0
    message = True
    count = 0
    # Scroll down until the last user is located
    while not final_located:
       
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")

        names = driver.find_elements(By.XPATH, '//div[@class="user-item-text"]')
        # Keep track of how many users remaining
        new_len_names = len(names)
        if len_names != new_len_names:
            print(f'{new_len_names}/{user_count} {option} loaded.')
            len_names = new_len_names
            count = 0
        else:
            message = True
           
        if message and count == 0:
            print(f"Allowing the system some time to load the remaining {option}.")
            message = False
            count = 1

        try:
            element = WebDriverWait(driver, 0.1).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[4]/main/div/div[2]/div[4]"))
            )
            load_located = True
        except TimeoutException:
            load_located = False
        try:
            element_final = WebDriverWait(driver, 0.1).until(
                EC.visibility_of_element_located(
                    (By.XPATH, f'//*[@id="{option}-list"]/div[{user_count}]/div[1]/a/div/span[1]'))
            )  
            final_located = True
        except TimeoutException:
            final_located = False
        if load_located:
            driver.execute_script("arguments[0].click();", element)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Scrolling took {execution_time} seconds to execute.")
    return data

# Function to save followers or following to a CSV file
def save_users(data, username, output_folder, option):
    start_time1 = time.time()

    # Get lists of user names and usernames
    names = driver.find_elements(By.XPATH, '//div[@class="user-item-text"]')
    usernames = driver.find_elements(By.XPATH, '//span[@class="tweet-header-handle"]')

    # Append user data to the existing data list
    for i in range(len(names)):
        data.append([names[i].text, usernames[i].text])

    # Create the specified output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save data to a CSV file within the specified output folder
    csv_file_path = os.path.join(output_folder, f'{username}_{option}.csv')

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(data)

    end_time1 = time.time()
    execution_time = end_time1 - start_time1
    print(f"Writing took {execution_time} seconds to execute.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Scrape Twitter users.')
    parser.add_argument('--cookie', required=True, help='Twitter auth_token cookie value')
    parser.add_argument('--username', required=True, help='Twitter username to scrape')
    parser.add_argument('--output_folder', required=True, help='Output folder to store the CSV file')
    parser.add_argument('--option', required=True, choices=['followers', 'following'], help='Specify either "followers" or "following"')

    args = parser.parse_args()

    print("Creating the driver: It may take some time if it's the first time.")
    create_driver(args.username, args.cookie, args.option)
    print("Driver created successfully.")

    print(f"Scraping {args.option}...")
    data = scrape_users(args.option)
    print(f"{args.option.capitalize()} scraped successfully.")

    print(f"Saving {args.option} to CSV...")
    save_users(data, args.username, args.output_folder, args.option)
    print(f"{args.option.capitalize()} saved to CSV successfully.")

    # Close the WebDriver instance
    driver.quit()
