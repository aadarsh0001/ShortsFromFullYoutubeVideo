# README for Backend

## Overview

This backend application is designed to process videos by extracting important moments, generating clips, and adding subtitles. It utilizes FastAPI for the web framework and integrates various services for video processing.

## Project Structure

- **main.py**: Entry point of the application, initializes the FastAPI app and includes API routes.
- **api/**: Contains the API routes for video processing.
  - **routes.py**: Defines endpoints for uploading videos, generating clips, and retrieving subtitles.
- **services/**: Implements core functionalities for video processing.
  - **video_processor.py**: Functions for processing video files, extracting audio, and saving metadata.
  - **clip_selector.py**: Logic for selecting important moments based on speech energy and keyword importance.
  - **subtitles.py**: Handles subtitle generation using the Whisper model.
- **utils/**: Utility functions for interacting with FFmpeg.
  - **ffmpeg.py**: Functions for cutting videos and resizing them.
- **models/**: Contains model loading functionalities.
  - **whisper_loader.py**: Loads the Whisper model and provides transcription and language detection functions.
- **requirements.txt**: Lists dependencies required for the backend application.

## Setup Instructions

1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd video-ai/backend
   ```

2. **Install Dependencies**
   Ensure you have Python 3.10+ installed. Then, install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application**
   Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

4. **Access the API**
   Open your browser and navigate to `http://localhost:8000/docs` to view the API documentation and test the endpoints.

## Usage Examples

- **Upload Video**: Use the `/upload` endpoint to upload a video file.
- **Generate Clips**: Call the `/generate-clips` endpoint to create clips from the uploaded video.
- **Retrieve Subtitles**: Access the `/subtitles` endpoint to get the generated subtitles for the video.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.