# YouTube Playlist Downloader (v3.0)

A modern, fast, and reliable YouTube video and playlist downloader built with Django and `yt-dlp`.

> [!CAUTION]
> This project is created for educational purposes only. Please respect YouTube's Terms of Service and only download content for which you have the rights or permission.

## Features

- **Download Single Videos**: Extract video metadata and high-quality download links (360p, 720p).
- **Download Full Playlists**: Fetch all video links from a playlist using the YouTube Data API.
- **Modern Backend**: Powered by `yt-dlp` for superior reliability and extraction speed.
- **Clean UI**: Simple and intuitive interface for quick downloads.

## Tech Stack

- **Backend**: Python 3.13, Django 6.0
- **Extraction**: `yt-dlp`, `google-api-python-client`
- **Frontend**: HTML5, Vanilla CSS

## Getting Started

### Prerequisites

- Python 3.13+
- A Google Cloud Platform project with the **YouTube Data API v3** enabled.

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/iamrk1811/YouTube-Downloader-Site.git
   cd YouTube-Downloader-Site
   ```

2. **Set up a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Secrets**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and add your `YOUTUBE_API_KEY` and `DJANGO_SECRET_KEY`.

### Running the Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## Project Structure

- `YouTube_Playlist_Downloader/`: Core project settings and logic.
- `templates/`: HTML templates for the frontend.
- `asset/`: Static assets (CSS, JS).
- `manage.py`: Django management script.

## Author

**Rakib Hossain** - [LinkedIn](https://www.linkedin.com/in/rakibrk1811/)
