------------------------------------------------------
HOW TO USE:
------------------------------------------------------
python -m venv venv
venv\scripts\Activate
pip install -r requirements.txt
python start.py

------------------------------------------------------------------------------------------------------------
Note: If polymorph.py takes too long, you can just cancel it early by pressing Ctrl + C
Then you can run the brute force tool separately
------------------------------------------------------------------------------------------------------------
python brute_csrf.py <URL> <Wordlist>
Example:
python brute_csrf.py https://aqmalzulkifli.pythonanywhere.com/ generatedpass.txt
