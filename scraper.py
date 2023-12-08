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
def create_driver(username, cookie):
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
    driver.get(f"https://twitter.com/{username}/followers")
    

# Function to scrape followers
def scrape_followers():
    start_time = time.time()
    
    final_located = False
    data = [
        ['Name', 'Username']  # Translated variable names
    ]

    # Get the number of followers
    time.sleep(5)
    follower_count = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="profile-stat-followers-value"]')))
    follower_count = follower_count.text

    len_names = 0
    message = True
    count = 0
    # Scroll down until the last follower is located
    while not final_located:
       
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")

        names = driver.find_elements(By.XPATH, '//div[@class="user-item-text"]')
        # Keep track of how many followers remaining
        new_len_names = len(names)
        if len_names != new_len_names:
            print(f'{new_len_names}/{follower_count} followers loaded.')
            len_names = new_len_names
            count = 0
        else:
            message = True
           
        if message and count == 0:
            print("Allowing the system some time to load the remaining followers.")
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
                    (By.XPATH, '/html/body/div[4]/main/div/div[2]/div[3]/div[' + follower_count + ']/div[1]/a/div/span[1]'))
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

# Function to save followers to a CSV file
def save_followers(data, username, output_folder):
    start_time1 = time.time()

    # Get lists of follower names and usernames
    names = driver.find_elements(By.XPATH, '//div[@class="user-item-text"]')
    usernames = driver.find_elements(By.XPATH, '//span[@class="tweet-header-handle"]')

    # Append follower data to the existing data list
    for i in range(len(names)):
        data.append([names[i].text, usernames[i].text])

    # Create the specified output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save data to a CSV file within the specified output folder
    csv_file_path = os.path.join(output_folder, f'{username}_followers.csv')

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(data)

    end_time1 = time.time()
    execution_time = end_time1 - start_time1
    print(f"Writing took {execution_time} seconds to execute.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Scrape Twitter followers.')
    parser.add_argument('--cookie', required=True, help='Twitter auth_token cookie value')
    parser.add_argument('--username', required=True, help='Twitter username to scrape followers')
    parser.add_argument('--output_folder', required=True, help='Output folder to store the CSV file')

    args = parser.parse_args()

    print("Creating the driver: It may take some time if it's the first time.")
    create_driver(args.username, args.cookie)
    print("Driver created successfully.")

    print("Scraping followers...")
    data = scrape_followers()
    print("Followers scraped successfully.")

    print("Saving followers to CSV...")
    save_followers(data, args.username, args.output_folder)
    print("Followers saved to CSV successfully.")

    # Close the WebDriver instance
    driver.quit()
