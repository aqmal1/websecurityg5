from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import re

# Set up WebDriver for Firefox (Ensure Geckodriver is installed)
service = Service("/usr/bin/geckodriver")
driver = webdriver.Firefox(service=service)

# Facebook Login Credentials (Replace with your actual credentials)
USERNAME = "email"
PASSWORD = "password"

# Facebook Login URL
FB_LOGIN_URL = "https://www.facebook.com/login"

# Function to log into Facebook
def login_facebook():
    """Logs into Facebook using Selenium and waits for manual 2FA completion."""
    driver.get(FB_LOGIN_URL)
    time.sleep(3)

    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "pass")
    login_button = driver.find_element(By.NAME, "login")

    email_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)
    login_button.click()
    time.sleep(5)  # Wait for login process

    # Handle 2FA if detected
    if "checkpoint" in driver.current_url or "two_step_verification" in driver.current_url:
        print("Facebook 2FA/CAPTCHA detected. Please complete it manually.")
        input("Press Enter after completing 2FA/CAPTCHA... ")

    print("Logged into Facebook successfully!")
    return True

# Function to extract all text from a profile page
def scrape_profile_text(profile_url):
    """Scrapes all visible text from a Facebook profile page."""
    driver.get(profile_url)
    time.sleep(5)  # Wait for page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract all visible text from the page
    all_text = soup.get_text(separator="\n", strip=True)

    # Filter out common Facebook words
    words = re.findall(r'\b[A-Za-z0-9_]+\b', all_text)
    unique_words = sorted(set(words))  # Remove duplicates and sort

    return unique_words

# Function to save extracted words to a text file
def save_wordlist(words, filename="wordlist.txt"):
    """Saves extracted words to a .txt file."""
    with open(filename, "w", encoding="utf-8") as file:
        for word in words:
            file.write(word + "\n")
    print(f"Wordlist saved to {filename}")

# Main Execution Block
if __name__ == "__main__":
    try:
        # 🔹 Step 1: Log into Facebook
        if login_facebook():
            print("Facebook Login Successful!")

            # 🔹 Step 2: Ask the user for a profile URL
            profile_url = input("Enter the Facebook Profile URL: ")

            # 🔹 Step 3: Scrape all text from the profile page
            words = scrape_profile_text(profile_url)

            # 🔹 Step 4: Save words to a .txt file
            save_wordlist(words)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Scraping complete!")
