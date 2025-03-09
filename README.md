------------------------------------------------------
## HOW TO USE:
------------------------------------------------------

Navigate to the **LATEST** folder and run the following commands:

```sh
python -m venv venv
venv\scripts\Activate
pip install -r requirements.txt
python start.py
```

**Note:** `start.py` will execute three scripts in this order:  
1. `scraper.py`  
2. `polymorph.py`  
3. `brute_csrf.py`  

If `polymorph.py` takes too long, you can cancel it early by pressing `Ctrl + C`.  
You can then run the brute force tool separately:

```sh
python brute_csrf.py <URL> <Wordlist>
```

### **Example:**
```sh
python brute_csrf.py https://aqmalzulkifli.pythonanywhere.com/ generatedpass.txt
```

--------------------------------------------------------
## SCRAPING FACEBOOK AND INSTAGRAM PROFILES
--------------------------------------------------------

Edit the `.env` file and enter your credentials to enable this functionality.
