# -*- coding: utf-8 -*-
"""Refactored version of the scraper script which uses manual
authentication and scrapes only followers"""
import argparse
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os

# Initialize a global variable for the WebDriver
driver = ''

USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')


# Function to create the WebDriver instance
def create_driver(username, option):
    global driver

    # Configure Chrome options, including a custom extension
    options = webdriver.ChromeOptions()

    service = Service(ChromeDriverManager().install())
    # Create the WebDriver instance with the configured options
    driver = webdriver.Chrome(service=service, options=options)

    # Navigate to Twitter login page and enter credentials
    driver.get('https://x.com/i/flow/login')
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@name="text"]'))
    )
    username_input.send_keys(USERNAME)
    username_input.send_keys(Keys.RETURN)
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@name="password"]'))
    )
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)

    driver.get(f"https://x.com/{username}/{option}")


# Function to scrape followers or following
def scrape_users():
    start_time = time.time()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, f'//div[@aria-label="Timeline: Followers"]')))

    followers = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        names = driver.find_elements(By.XPATH, '//div[@data-testid="cellInnerDiv"]')
        followers.extend([name_div.text for name_div in names])
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

        last_height = new_height

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Scrolling took {execution_time} seconds to execute.")
    return followers


# Function to save followers or following to a CSV file
def save_users(data, username, output_folder, option):
    start_time1 = time.time()

    # Create the specified output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save data to a file within the specified output folder
    file_path = os.path.join(output_folder, f'{username}_{option}.txt')

    usernames = []
    for line in data:
        parts = line.split('\n')
        for part in parts:
            if part.startswith('@'):
                usernames.append(part)
    print(f"len of usernames: {len(usernames)}")
    usernames = list(set(usernames))
    with open(file_path, 'w') as file:
        for line in usernames:
            file.write(line + '\n')

    end_time1 = time.time()
    execution_time = end_time1 - start_time1
    print(f"Writing took {execution_time} seconds to execute.")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Scrape Twitter users.')
    parser.add_argument('--username', required=True, help='Twitter username to scrape')
    parser.add_argument('--output_folder', required=True, help='Output folder to store the CSV file')

    args = parser.parse_args()

    print("Creating the driver: It may take some time if it's the first time.")
    create_driver(args.username, args.cookie)
    print("Driver created successfully.")

    print(f"Scraping {args.option}...")
    data = scrape_users()
    print(f"{args.option.capitalize()} scraped successfully.")

    print(f"Saving {args.option} to file...")
    save_users(data, args.username, args.output_folder, args.option)
    print(f"{args.option.capitalize()} saved to file successfully.")

    # Close the WebDriver instance
    driver.quit()
