# Twitter Followers Scraper

## Overview

This Python script is designed to scrape a user's Twitter followers using Selenium and Chrome WebDriver. It navigates to a user's followers page on Twitter, scrolls through the followers list, and saves the data to a CSV file.

## Prerequisites

- [Python 3.x](https://www.python.org/downloads/)
- [Chrome browser](https://www.google.com/chrome/) installed
- Required Python packages (install using `pip install -r requirements.txt`):
  - `selenium`
  - `webdriver_manager`
  - `chromedriver-autoinstaller`
  - `packaging`

  
## Usage

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/twitter-followers-scraper.git
   cd twitter-followers-scraper

2. **Install the required packages:**

    ```bash
    pip install -r requirements.txt

3. **Run the script:**

    ```bash
    python scraper.py --cookie YOUR_TWITTER_COOKIE --username TARGET_USERNAME --output_folder OUTPUT_FOLDER

### Command-Line Arguments
--cookie: Twitter auth_token cookie value (required)

--username: Twitter username to scrape followers (required)

--output_folder: Output folder to store the CSV file (required)

--option: Specify either "followers" or "following" (required)

### Output
The script will create a CSV file named TARGET_USERNAME_followers.csv or TARGET_USERNAME_following.csv in the specified output folder. The CSV file contains two columns: 'Name' and 'Username'.

### Notes
The script may take some time, especially during the first run, as it creates a WebDriver instance and navigates through the followers list.

### Disclaimer
This script is for educational purposes only. Use it responsibly and respect the terms of service of the websites you are scraping.
