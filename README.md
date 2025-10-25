# Automated-Call-Analyzer
A Python script to automate the transcription, analysis, and data entry of customer service calls into a Google Sheet. The tool processes audio files, evaluates manager performance, and categorizes call topics.

## Setup

**Important Environment Notes:**

* **Python:** This project was developed and tested using **Python 3.12.3**.
* **Operating System:** This project was developed on a **Linux** environment.

While other Python 3.x versions might work, **Python 3.12.3** is strongly recommended. Running the project on other operating systems (like Windows or macOS) is **not guaranteed** to be fully compatible, as dependency behavior may differ.

1.  **Clone the repository:**

    ```bash
    git clone git@github.com:OleksandrPro/Automated-Call-Analyzer.git
    ```

    ```bash
    cd Automated-Call-Analyzer/
    ```

2.  **Install dependencies:**

    **Using a virtual environment is recommended:**
    ```bash
    python -m venv venv
    ```

    **Activate venv (Linux):**
    ```bash
    source venv/bin/activate
    ```

    **Install packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration Steps

Setting up this project involves three main parts:
1.  **Getting Google AI (Gemini) credentials.**
2.  **Getting Google Drive & Sheets credentials (OAuth 2.0).**
3.  **Setting up the `.env` file.**

## Part 1: Get Gemini API Key

You need a simple API key to use the Gemini API.

1.  Go to [Google AI Studio](https://aistudio.google.com/).
2.  Log in with your Google account.
3.  Click on **"Get API key"** and create a new key.
4.  Copy this key. You will paste it into your `.env` file as `GEMINI_API_KEY`.

---

## Part 2: Google Drive & Sheets Configuration

Before you can run the application, you need to set up your Google services and get the necessary IDs.

### 1. Get Google Drive & Sheets Credentials (OAuth 2.0)

This project accesses Google Drive and Sheets on your behalf (as a "personal" account), which requires **OAuth 2.0**.

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project (or select an existing one).
3.  **Enable APIs:** In your project's dashboard, go to "APIs & Services" > "Library".
4.  Search for and **enable** the following two APIs:
    * **Google Drive API**
    * **Google Sheets API**
5.  **Set up OAuth Consent Screen:**
    * Go to "APIs & Services" > "OAuth consent screen".
    * Choose **"External"** and click "Create".
    * Fill in the required fields (App name, User support email).
    * On the "Scopes" page, you don't need to add anything.
    * On the "Test users" page, **add your own Google email address**. This authorizes your account to use the app before it's "published".
6.  **Create Credentials:**
    * Go to "APIs & Services" > "Credentials".
    * Click "Create Credentials" > **"OAuth client ID"**.
    * For "Application type", select **"Desktop app"**. (This is the simplest for local scripts).
    * Click "Create".
    * A window will pop up showing your "Client ID" and "Client Secret". Click **"Download JSON"**.
7.  **Save Credentials:**
    * Rename the downloaded file to **`client_secret.json`**.
    * Place this `client_secret.json` file in the `app_data/` directory.


### 2. Get Your Google Sheet URL

1.  Create a new Google Sheet or locate the one you want to use.

2.  **Check File Format (Crucial!):** This script only works with native Google Sheets, not Microsoft Excel (.xlsx) files.

    * If your file is currently an .xlsx file, you must convert it.
    * Open the .xlsx file in your Google Drive.
    * Click File -> Save as Google Sheets.
    * This will create a new, separate file (it will have a green Google Sheets icon). You must use this new file for the next step.

3.  Copy the full URL of the native Google Sheet (the converted one) from your browser's address bar.
    * *Example:* `https://docs.google.com/spreadsheets/d/1abc-123_YOUR_ID_HERE/edit`

### 3. Get Your Google Drive Folder IDs

You will need to specify at least one folder ID:

* **Audio Files Folder:** Where the script will look for `.mp3` files.
* **Transcript Folder (Optional):** Where the script will save the `.json` transcripts.

**Note:** Specifying a separate Transcript Folder is optional. If you leave the GOOGLE_DRIVE_TRANSCRIPTION_FOLDER_ID variable blank in your .env file, the script will automatically save all transcripts to the main Audio Files Folder.

To get an ID:

1.  Create the folder in Google Drive (e.g., "Call Audio") or use the existing one.
2.  Open the folder. The URL in your browser will look like this:
    `https://drive.google.com/drive/u/1/folders/`**`13MKq82OEhenoFlOnuHalenH9fxTsj1Nl`**
3.  The final string of random characters is the **Folder ID**.
4.  Copy this ID. Repeat the process only if you want to use a separate transcripts folder.

---

## Part 3: Environment Variables (.env)

Now, create your local environment file.

1.  Create `.env` file in the project's root.
2.  Open the `.env` file and fill in the variables as described below.

    ```env
    # From Part 1 (Google AI Studio)
    GEMINI_API_KEY = "your_gemini_api_key_here"
    GEMINI_MODEL = "gemini-2.5-flash" # I used this model
    
    # --- Google Drive & Sheets ---
    
    # The name of the folder in your Google Drive (for reference)
    GOOGLE_DRIVE_AUDIOFILES_FOLDER_NAME = "YourAudioFolderName"
    
    GOOGLE_DRIVE_AUDIOFILES_FOLDER_ID = "your_folder_id_from_url"

    # (Optional) The ID of the folder to save transcripts.
    # If left blank, transcripts will be saved in the AUDIOFILES_FOLDER.
    GOOGLE_DRIVE_TRANSCRIPTION_FOLDER_ID = ""  
    
    TABLE_URL=""
    ```



## Running the Application

### First-Time Authentication (Required)

The first time you run the script, it will need to get your permission to access Drive/Sheets.

1.  Run the application:
    ```bash
    python src/main.py
    ```
    or

    ```bash
    python3 src/main.py
    ```
2.  A **browser window will open**, or a **URL will be printed** to your console.
3.  Open this URL. Log in with the **same personal Google account** you added as a "Test user" in Part 2.
4.  Google will ask you to grant permission (e.g., "See, edit, create, and delete your Google Drive files"). Click **"Allow"**.
5.  After you grant permission, you will be redirected to a confirmation page, and the script will continue.

The application will automatically create a new file (often named `token.json` or similar) in `app_data/` directory. This file stores your authorization and will be used for all future runs.


### Subsequent Runs

After the first run, you can start the application normally, and it will automatically use the saved `token.json` to authenticate.


```bash
python src/main.py
```
or

```bash
python3 src/main.py
```

