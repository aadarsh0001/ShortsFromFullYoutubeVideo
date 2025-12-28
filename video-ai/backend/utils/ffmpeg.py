def run_ffmpeg_command(command):
    import subprocess

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running FFmpeg: {e}")

def cut_video(input_file, output_file, start_time, duration):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', str(start_time),
        '-t', str(duration),
        '-c', 'copy',
        output_file
    ]
    run_ffmpeg_command(command)

def resize_video(input_file, output_file, width, height):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-vf', f'scale={width}:{height}',
        output_file
    ]
    run_ffmpeg_command(command)

def extract_audio(input_file, output_file):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-q:a', '0',
        '-map', 'a',
        output_file
    ]
    run_ffmpeg_command(command)