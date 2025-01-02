# Tradingview API
## 1. Setup new packages
```
peotry add uvicorn fastapi pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

## 2. Setup connect to google sheet
1. Create a Google Cloud Project:

    Go to the Google Cloud Console.

    Create a new project or use an existing one.

2. Enable the Sheets API:

    In the Google Cloud Console, go to APIs & Services > Library.

    Search for "Google Sheets API" and enable it.

    Create Service Account and Download Credentials:

3. Navigate to APIs & Services > Credentials.
    Click Create Credentials > Service Account.
    
    Follow the prompts to set up a service account and download the JSON key file.
    
    Share the Sheet with the Service Account:

Open the Google Sheet you want to write to.
Share it with the service account email (found in the JSON key file).

## 3. Config env file
```
sudo cp .env.example .env
```
Change value 
```
PORT=<port you want expose to local> | ex: 8000
CREDENTIALS_FILE=<directory to secret json file> | ex: secret.json
REDIRECT_URI=http://<url your web>/oauth2callback | ex: http://127.0.0.1:8000/oauth2callback
```

## 4. Run project
```
docker compose up --build -d
```