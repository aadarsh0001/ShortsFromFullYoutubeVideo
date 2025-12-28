# Video AI Project

This project is a local desktop/web application designed to process videos by identifying important moments, generating clips, and adding subtitles. It utilizes various technologies and frameworks to provide a seamless user experience.

## Project Structure

The project is organized into several directories and files:

- **backend/**: Contains the server-side code, including API routes and video processing services.
  - **main.py**: Entry point for the FastAPI application.
  - **api/**: Contains API route definitions.
  - **services/**: Contains logic for video processing, clip selection, and subtitle generation.
  - **utils/**: Utility functions for FFmpeg interactions.
  - **models/**: Contains the Whisper model loader.
  - **requirements.txt**: Lists the dependencies for the backend.
  - **README.md**: Documentation for the backend.

- **frontend/**: Contains the client-side code for the user interface.
  - **index.html**: Main HTML file for the frontend application.
  - **style.css**: Styles for the frontend application.
  - **app.js**: JavaScript code for handling user interactions and API calls.
  - **README.md**: Documentation for the frontend.

- **models/**: Contains the Whisper model files.

- **tests/**: Contains unit tests for both backend and frontend components.

- **scripts/**: Contains setup instructions for FFmpeg.

## Setup Instructions

1. **Clone the Repository**: 
   ```
   git clone <repository-url>
   cd video-ai
   ```
11. **how to setup and deactivate the virtual env**: 
    ```
    python3.13 -m venv venv  //OR\\ python -m venv venv 
    ```

    ```
    venv\Scripts\activate
    ```
    ```
    deactivate  [to deactivate the virtual environment]
    ```
2. **Backend Setup**:
   - Navigate to the `backend` directory.
   - Install the required dependencies:
     ```
     pip install -r requirements.txt
     ```
   - Run the FastAPI application:
     ```
     uvicorn main:app --reload
     ```

3. **Frontend Setup**:
   - Open `index.html` in a web browser to access the frontend application.

## How to create requirement.txt
- This is just for knowladge purpuse.
- Run this command in system path or Virtual Environment, according to your need:
    ```
    pip freeze > requirements.txt
    ```


## Usage

- Upload a video file through the frontend interface.
- The application will process the video, generate clips, and add subtitles.
- You can download the generated clips directly from the interface.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.