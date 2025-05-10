# FanVoiceApp

## 1. Project Overview

The **FanVoiceApp** is a project aimed at enhancing fan engagement before and during live shows. Using ElevenLabs’ Voice AI technology, this tool allows artists and DJs to:

1.  Collect voice recordings from fans before a show.
2.  Use ElevenLabs' API to generate custom phrases spoken in the fan's voice. Brainstorm creative phrases with Google's TextFX, integrated via Gemini's API.
3.  Play these clips during live performances to create unforgettable moments for fans, while giving artists a fun, creative way to customize each show to their audience.

### Use Case

Imagine a DJ like Dom Dolla playing his song "San Francisco" at a show. In the original recording of the song, there is a voice that says "San Francisco, where's your disco" right before the beat drops.

Instead, imagine a lucky fan's voice saying that same line, but "San Francisco" is swapped with the city the show is at.

Take it a step further - the fan's voice could say any custom hype phrase that the artist wants, inserted at any point in any song during the show.

This proof-of-concept tool showcases the potential of utilizing voice AI to transform fan experiences and deepen the connection between artists and their audience. It highlights an innovative approach to fan engagement by making each performance interactive, unique, and unforgettable.

### Why This Matters

The music industry is increasingly building products and experiences to serve the "superfan". What are superfans' wildest wishes that artists can make come true? One category of fan wishes is to be able to co-create with their favorite artists. Imagine hearing your voice layered creatively into your favorite artist's live set!

From the artist perspective, this tool opens up new possibilities for marketing and fan engagement. For example, artists can invite fans to submit voice recordings, with the chance to be featured as the lucky voice played during a show. Artists can also crowdsource creative text prompts from fans, further elevating this unique collaboration between the artist and fan. During a performance, voice AI unlocks unprecedented levels of voice customization, creating moments of surprise and delight that fans crave.

Ultimately, voice AI empowers us to explore the limitless magic of music and create unforgettable memories together.

## 2. Tools & Technologies Used

*   **Backend:** Python, Flask
*   **Database:** MySQL
*   **AI Services:**
    *   ElevenLabs API (for voice cloning and text-to-speech)
    *   Google Gemini API (via TextFX for creative text generation)
*   **Frontend:** HTML, CSS, JavaScript (via Flask templates)
*   **Environment Management:** Python Virtual Environment (`venv`)
*   **Dependencies:** Listed in `requirements.txt` (e.g., Flask, SQLAlchemy, PyMySQL, ElevenLabs client, Google Generative AI client)

## 3. Repository Contents

```
/FanVoiceApp
|-- .env.example                # Example environment variables file
|-- .gitignore                  # Specifies intentionally untracked files that Git should ignore
|-- README.md                   # This file: project overview and setup instructions
|-- about_content.md            # Source content for the About page
|-- requirements.txt            # Python package dependencies
|-- src/
|   |-- __init__.py
|   |-- elevenlabs_actions.py     # Functions for interacting with ElevenLabs API
|   |-- gemini_textfx.py          # Functions for interacting with Gemini/TextFX API
|   |-- main.py                   # Main Flask application, entry point, and core routes
|   |-- models/                   # SQLAlchemy database models
|   |   |-- __init__.py
|   |   |-- user.py               # User model
|   |   `-- voice.py              # ClonedVoice model
|   |-- routes/                   # Flask Blueprints for specific routes (e.g., user auth)
|   |   |-- __init__.py
|   |   `-- user.py               # User authentication routes
|   |-- static/                   # Static assets (CSS, JS, images - if any beyond base.html)
|   |   `-- index.html            # (Note: This seems to be a duplicate or old file, main templates are in templates/)
|   `-- templates/                # HTML templates for Flask
|       |-- about.html
|       |-- base.html
|       |-- index.html
|       `-- login.html
|-- uploads/                    # (Not in repo - created locally) Directory for uploaded voice samples
`-- generated_audio/            # (Not in repo - created locally) Directory for generated TTS audio files
```

**Note:** `uploads/` and `generated_audio/` directories are created by the application at runtime if they don't exist and are included in `.gitignore` so they are not committed to the repository.

## 4. How to Use (Setup and Installation)

Follow these steps to set up and run the FanVoiceApp locally on your computer:

### Prerequisites

*   Python 3.8 or higher
*   `pip` (Python package installer)
*   Git
*   A running MySQL server instance

### Installation Steps

1.  **Clone the repository:**
    Open your terminal or command prompt and run:
    ```bash
    git clone https://github.com/yourusername/FanVoiceApp.git 
    cd FanVoiceApp
    ```
    (Replace `yourusername/FanVoiceApp.git` with the actual URL of your GitHub repository if you fork it.)

2.  **Set up a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python3 -m venv venv
    ```
    Activate the virtual environment:
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    You should see `(venv)` at the beginning of your terminal prompt.

3.  **Install Dependencies:**
    With the virtual environment activated, install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    The application requires API keys and database credentials, which are managed through an `.env` file.
    *   Copy the example file:
        ```bash
        cp .env.example .env
        ```
    *   Open the newly created `.env` file in a text editor and fill in your actual credentials. **Do not commit your actual `.env` file to GitHub.**

    Here are the variables you need to set:

    | Variable           | Description                                                                 | Example Value (Replace with your own) |
    |--------------------|-----------------------------------------------------------------------------|---------------------------------------|
    | `ELEVENLABS_API_KEY` | Your API key for the ElevenLabs service.                                    | `sk_yourxxxxxxxxxxxxxxxxxxxxxxx`      |
    | `GEMINI_API_KEY`   | Your API key for the Google Gemini service.                                 | `AIzaSyBxxxxxxxxxxxxxxxxxxxxxxx`    |
    | `FLASK_SECRET_KEY` | A secret key for Flask session management. Use a long, random string.       | `super-secret-random-string-12345`    |
    | `DB_USERNAME`      | Your MySQL database username.                                               | `root`                                |
    | `DB_PASSWORD`      | Your MySQL database password.                                               | `your_db_password`                    |
    | `DB_HOST`          | The hostname or IP address of your MySQL server.                            | `localhost`                           |
    | `DB_PORT`          | The port your MySQL server is running on.                                   | `3306`                                |
    | `DB_NAME`          | The name of the database to use for this application.                       | `fanvoice_db`                         |

5.  **Set up the MySQL Database:**
    *   Ensure your MySQL server is running.
    *   Connect to your MySQL server using a client (e.g., MySQL Workbench, DBeaver, command line).
    *   Create the database specified in your `.env` file (e.g., `fanvoice_db` if you used the example).
        ```sql
        CREATE DATABASE fanvoice_db;
        ```
    *   The application will automatically create the necessary tables (`user`, `cloned_voice`) when it first starts if they don't already exist in this database.

6.  **Run the Application:**
    With the virtual environment still active and your `.env` file configured, start the Flask development server:
    ```bash
    python3 src/main.py
    ```
    You should see output indicating the server is running, typically on `http://127.0.0.1:5000/`.

7.  **Access the Application:**
    Open your web browser and navigate to `http://127.0.0.1:5000/`.

### Usage Guide

*   **Login/Register:** The application has separate views for 'Fans' and 'Artists'. Use the default credentials provided on the login page (`fan`/`fanpw` or `artist`/`artistpw`).
*   **Fan View:**
    *   Upload a short audio file of your voice (best practice is at least 1 minute of you talking about anything, but for proof of concept, even 10 seconds could work)
    *   Give your voice clone a name.
    *   The application will use ElevenLabs to clone your voice.
*   **Artist View:**
    *   View available cloned voices from fans.
    *   Select a cloned voice.
    *   Enter text you want the voice to say.
    *   Use the Gemini/TextFX integration to brainstorm creative phrases (optional).
    *   Generate the audio using ElevenLabs.
    *   Listen to or download the generated audio clip.

