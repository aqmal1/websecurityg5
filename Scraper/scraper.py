import os
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

        try:
            profile_name = driver.find_element(By.TAG_NAME, "h2").text.strip()
        except:
            profile_name = "N/A"

        try:
            bio_section = driver.find_element(By.XPATH, "//div[contains(@class, '_aa_c')]")
            bio = bio_section.text.strip()
        except:
            bio = "No bio available"

        try:
            stats = driver.find_elements(By.XPATH, "//li[contains(@class, '_ac2a')]")
            followers = stats[0].text if len(stats) > 0 else "N/A"
            following = stats[1].text if len(stats) > 1 else "N/A"
        except:
            followers = "N/A"
            following = "N/A"

        profile_info = f"{profile_name}\n{bio}\n{followers} Followers\n{following} Following"
        return format_scraped_text(profile_info)

    except Exception as e:
        print(f"Error scraping Instagram: {e}")
        return []

# Function to format scraped text
def format_scraped_text(text):
    """Formats scraped text to extract meaningful words, names, dates, and numbers."""
    words = []

    name_pattern = r"\b([A-Z][a-z]+)\s([A-Z][a-z]+)(?:\s([A-Z][a-z]+))?\b"
    matches = re.findall(name_pattern, text)
    for match in matches:
        name_parts = [part for part in match if part]
        full_name = "".join(name_parts)
        words.extend(name_parts)
        words.append(full_name)

    date_patterns = [
        r"\b(\d{1,2})\s(January|February|March|April|May|June|July|August|September|October|November|December)\b",
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2})\b",
        r"\b(\d{1,2})\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{4})\b",
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            formatted_date = "".join(match)
            words.append(formatted_date)

    general_words = re.findall(r'\b[A-Za-z0-9]+\b', text)
    words.extend(general_words)

    return sorted(set(words))

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
        choice = input("Choose platform to scrape (facebook/instagram): ").strip().lower()

        if choice == "facebook":
            if login_facebook():
                profile_url = input("Enter the Facebook Profile URL: ")
                words = scrape_facebook_profile(profile_url)
        elif choice == "instagram":
            if login_instagram():
                profile_url = input("Enter the Instagram Profile URL: ")
                words = scrape_instagram_profile(profile_url)

        save_wordlist(words)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Scraping complete!")
