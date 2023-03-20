import os
import ffmpeg
from pytube import YouTube
import pytube
import youtube_transcript_api
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from extra_data import gsheet_credentials_path
import yt_dlp
from pathlib import Path


def extract_links(credential_path=gsheet_credentials_path) -> pd.DataFrame:
    """

    Args:
        credential_path: Path to the Gsheet credentials. Remember for next time,
        you need to create an application, then add drive and gsheets apis,
        create service account and finally add json key to it.

    Returns:
        links_df: Dataframe with only Not Done videos to extract

    """
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]

    # Authentication
    creds = ServiceAccountCredentials.from_json_keyfile_name(credential_path, scope)
    client = gspread.authorize(creds)

    # Get current sheet records
    sheet = client.open("Videos_mama")
    Expenses_Log = sheet.worksheet("Videos Mama")
    data = Expenses_Log.get_values()
    links_df = pd.DataFrame(data, columns=["", "", 'Numero',
                                           'Titulo del video',
                                           'Nombre sin espacios',
                                           'Link del video',
                                           'Status',
                                           'Comentario',
                                           'Paid?'])[["Nombre sin espacios", "Link del video", "Status"]]
    return links_df.loc[links_df['Status'] == 'Not DONE']


def download_video(video_url: str, output_folder: Path) -> None:
    """
    Function that downloads a video given an url and an output
    folder. It gets downloaded in .mp4 format in the provided
    folder.
    Args:
        video_url: Url of the video to download
        output_folder: Path to the folder where we want to
        download the video

    Returns:

    """

    # Create the directory if it doesn't already exist
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    # Set options for video download
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': output_folder.joinpath('%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
    }

    # Download video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    print(f"Video saved to {output_folder}")

# TODO Create Video Class
# TODO Create subtitles function
# TODO Manage a robust bucle
