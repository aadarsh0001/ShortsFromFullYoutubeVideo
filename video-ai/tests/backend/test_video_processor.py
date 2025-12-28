import pytest
from backend.services.video_processor import extract_audio, save_metadata

def test_extract_audio():
    # Test case for extracting audio from a video file
    video_file = "test_video.mp4"
    expected_audio_file = "test_video_audio.wav"
    
    # Call the function to extract audio
    extract_audio(video_file)
    
    # Check if the audio file was created
    assert os.path.exists(expected_audio_file) == True

def test_save_metadata():
    # Test case for saving metadata from a video file
    video_file = "test_video.mp4"
    expected_metadata = {
        "duration": 120,
        "fps": 30
    }
    
    # Call the function to save metadata
    metadata = save_metadata(video_file)
    
    # Check if the metadata matches the expected values
    assert metadata["duration"] == expected_metadata["duration"]
    assert metadata["fps"] == expected_metadata["fps"]