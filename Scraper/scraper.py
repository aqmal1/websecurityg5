﻿import os
import re
import time
import platform
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# Detect OS and setup WebDriver
if platform.system() == "Linux":
    print("Running on Kali Linux - Using Firefox")
    webdriver_service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=webdriver_service)
elif platform.system() == "Windows":
    print("Running on Windows - Using Chrome")
    webdriver_service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service)
else:
    raise Exception("Unsupported OS. This script supports only Kali Linux (Firefox) and Windows (Chrome).")

# Function to load credentials from an environment file
def load_credentials(env_file):
    """Loads credentials from an environment (.env) file."""
    load_dotenv(env_file)
    username = os.getenv("FB_USERNAME") or os.getenv("IG_USERNAME")
    password = os.getenv("FB_PASSWORD") or os.getenv("IG_PASSWORD")
    
    if not username or not password:
        raise Exception(f"Missing credentials in {env_file}")
    
    return username, password

# Function to log into Facebook
def login_facebook():
    """Logs into Facebook using Selenium and waits for manual 2FA completion."""
    username, password = load_credentials(".env.facebook")

    driver.get("https://www.facebook.com/login")
    time.sleep(3)

    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "pass")
    login_button = driver.find_element(By.NAME, "login")

    email_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()
    time.sleep(5)

    if "checkpoint" in driver.current_url or "two_step_verification" in driver.current_url:
        print("Facebook 2FA detected! Please complete it manually.")
        input("Press Enter after completing 2FA authentication... ")

    print("Logged into Facebook successfully!")
    return True

# Function to log into Instagram
def login_instagram():
    """Logs into Instagram using Selenium and waits for manual 2FA completion."""
    username, password = load_credentials(".env.instagram")

    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)

    email_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

    email_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()
    time.sleep(5)

    if "two_factor" in driver.current_url:
        print("Instagram 2FA Detected! Please complete the verification manually.")
        input("Press Enter after completing the 2FA authentication... ")

    print("Logged into Instagram successfully!")
    return True

# Function to scrape Facebook profile data
def scrape_facebook_profile(profile_url):
    """Scrapes all visible text from a Facebook profile page."""
    driver.get(profile_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_text = soup.get_text(separator="\n", strip=True)

    return format_scraped_text(all_text)

# Function to scrape Instagram profile data
def scrape_instagram_profile(profile_url):
    """Scrapes an Instagram profile page while staying in the logged-in session."""
    
    print(f"Navigating to {profile_url}...")
    driver.get(profile_url)
    time.sleep(5)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h2"))
        )

        profile_name = driver.find_element(By.TAG_NAME, "h2").text.strip()
        bio_section = driver.find_element(By.XPATH, "//div[contains(@class, '_aa_c')]").text.strip()
        followers = driver.find_element(By.XPATH, "//li[contains(@class, '_ac2a')]").text.strip()
        following = driver.find_element(By.XPATH, "//li[contains(@class, '_ac2a')]").text.strip()

        profile_info = f"{profile_name}\n{bio_section}\n{followers} Followers\n{following} Following"
        return format_scraped_text(profile_info)

    except Exception as e:
        print(f"Error scraping Instagram: {e}")
        return []

# Function to scrape general websites (blogs, news, static pages)
def scrape_general_website(url):
    """Scrapes text content from a general website page, including small text like author names."""
    print(f"Navigating to {url}...")
    driver.get(url)
    time.sleep(5)  # Allow page to load

    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract headlines
        headings = [h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3'])]

        # Extract paragraph text
        paragraphs = [p.text.strip() for p in soup.find_all('p')]

        # Extract small text (author names, post credits, etc.)
        small_texts = [s.text.strip() for s in soup.find_all(['small', 'span', 'footer'])]

        # Merge extracted content
        page_text = "\n".join(headings + paragraphs + small_texts)

        print("Website content scraped successfully!")
        return format_scraped_text(page_text)

    except Exception as e:
        print(f"Error scraping website: {e}")
        return []


# Function to format scraped text
def format_scraped_text(text):
    """Formats scraped text to extract meaningful words, names, dates, and numbers."""
    words = re.findall(r'\b[A-Za-z0-9]+\b', text)
    return sorted(set(words))

# Function to save extracted words to a text file
def save_wordlist(words, filename="wordlist.txt"):
    """Saves extracted words to a .txt file."""
    with open(filename, "w", encoding="utf-8") as file:
        for word in words:
            file.write(word + "\n")
    print(f"Wordlist saved to {filename}")

if __name__ == "__main__":
    try:
        choice = input("Choose platform to scrape (facebook/instagram/website): ").strip().lower()
        profile_url = input("Enter the URL to scrape: ").strip()

        if choice == "facebook":
            if login_facebook():
                words = scrape_facebook_profile(profile_url)
        elif choice == "instagram":
            if login_instagram():
                words = scrape_instagram_profile(profile_url)
        elif choice == "website":
            words = scrape_general_website(profile_url)
        else:
            print("Invalid choice. Please restart the script and choose a valid option.")
            exit()

        save_wordlist(words)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Scraping complete!")
