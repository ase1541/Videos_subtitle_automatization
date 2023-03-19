import os
import ffmpeg

# Input video file path
video_file_path = input("Enter video file path: ")

# Input subtitle file path
subtitle_file_path = input("Enter subtitle file path: ")

# Output folder path
output_folder = input("Enter output folder path: ")

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Output video file path
output_video_file_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(video_file_path))[0]}_subtitled.mp4")

# Get video stream info
probe = ffmpeg.probe(video_file_path)
video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
if video_stream is None:
    print('No video stream found in input file')
    exit()

# Get subtitle stream info
subtitle_stream = ffmpeg.input(subtitle_file_path)
if subtitle_stream.streams.video:
    print('Subtitle file should not contain any video stream')
    exit()

# Add subtitles to video stream
subtitled_stream = ffmpeg.filter([video_stream['index'], subtitle_stream['index']], 'subtitles', force_style='Fontsize=22')

# Create output file
output = ffmpeg.output(subtitled_stream, f'{output_video_file_path}', vcodec='libx264', crf=18, acodec='copy')
output.run()

print(f"Subtitled video saved to {output_video_file_path}")




import os
import ffmpeg

# Input video file path
video_file_path = input("Enter video file path: ")

# Input subtitle file path
subtitle_file_path = input("Enter subtitle file path: ")

# Output folder path
output_folder = input("Enter output folder path: ")

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Output video file path
output_video_file_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(video_file_path))[0]}_subtitled.mp4")

# Get video stream info
probe = ffmpeg.probe(video_file_path)
video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
if video_stream is None:
    print('No video stream found in input file')
    exit()

# Get subtitle stream info
subtitle_stream = ffmpeg.input(subtitle_file_path)
if subtitle_stream.streams.video:
    print('Subtitle file should not contain any video stream')
    exit()

# Add subtitles to video stream
subtitled_stream = ffmpeg.filter([video_stream['index'], subtitle_stream['index']], 'subtitles', force_style='Fontsize=22')

# Create output file
output = ffmpeg.output(subtitled_stream, f'{output_video_file_path}', vcodec='libx264', crf=18, acodec='copy')
output.run()

print(f"Subtitled video saved to {output_video_file_path}")
