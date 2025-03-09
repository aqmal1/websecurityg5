------------------------------------------------------
## HOW TO USE:
------------------------------------------------------
```sh
Go to the folder called LATEST then run these commands:
python -m venv venv
venv\scripts\Activate
pip install -r requirements.txt
python start.py
```

**Note:** If `polymorph.py` takes too long, you can just cancel it early by pressing `Ctrl + C`.  
Then you can run the brute force tool separately:

```sh
python brute_csrf.py <URL> <Wordlist>
```

**Example:**
```sh
python brute_csrf.py https://aqmalzulkifli.pythonanywhere.com/ generatedpass.txt
```

--------------------------------------------------------
## SCRAPING FACEBOOK AND INSTAGRAM PROFILES
--------------------------------------------------------

Edit the `.env` files and type in your credentials if you want to do so.
