# Automated-Call-Analyzer
A Python script to automate the transcription, analysis, and data entry of customer service calls into a Google Sheet. The tool processes audio files, evaluates manager performance, and categorizes call topics.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone [URL_TO_YOUR_REPOSITORY]
    cd [PROJECT_DIRECTORY_NAME]
    ```

2.  **Install dependencies:**

    **Using a virtual environment is recommended:**
    ```bash
    python -m venv venv
    ```

    **Activate venv (Windows):**
    ```bash
    venv\Scripts\activate
    ```

    **Activate venv (Linux):**
    ```bash
    source venv/bin/activate
    ```

    **Using a virtual environment is recommended:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` File**

    Add the following variables to a `.env` file in your project root:

    ```env
    GEMINI_API_KEY = ""
    GEMINI_MODEL = ""

    GOOGLE_DRIVE_AUDIOFILES_FOLDER_NAME = ""
    GOOGLE_DRIVE_AUDIOFILES_FOLDER_ID= ""
    TABLE_URL = ""
    ```

4.  **Get required API keys**

## Running the Application

Once the dependencies are installed and the configuration is set, you can run the project.

    ```bash
    python3 src/main.py
    ```
