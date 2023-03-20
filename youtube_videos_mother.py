import os
import ffmpeg
from pytube import YouTube
import pytube
import youtube_transcript_api
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from googletrans import Translator
from extra_data import gsheet_credentials_path, downloads_path
import yt_dlp
from pathlib import Path
import regex as re
import os


class Video:
    """
    Class used to encapsulate all the information related to the
    YouTube videos. Every video has a name, an url and from there,
    we get the video id and the path were we will be storing it.
    """
    videos_list = []

    def __init__(self, url, name):
        # Passed through innit
        self.url = url
        self.name = name

        # Obtained attributes
        self.video_id = self.get_video_id()
        self.folder_video_path = Path(downloads_path).joinpath(self.name)
        self.output_path = self.create_folder_final_videos()
        self.downloaded_video_path = self.folder_video_path.joinpath(self.name + ".mp4")
        self.downloaded_subtitles_path = self.folder_video_path.joinpath(self.name + ".srt")
        Video.videos_list.append(self)  # Store instances in list

    def __del__(self):
        """Erase folder with raw videos upon completion"""
        shutil.rmtree(self.folder_video_path)

    @classmethod
    def initialize_video_instances(cls, df_links: pd.DataFrame) -> None:
        """
        Class method that enables the initialization of all the Video
        objects needed.
        Args:
            df_links: dataframe with names and links to the videos
        """
        for index, row in df_links.iterrows():
            Video(url=row["Link del video"],
                  name=row["Nombre sin espacios"])

    def get_video_id(self) -> str:
        """
        Function that takes the video url and returns
        the video id for the get subtitles function

        Returns:
            video_id: string for the video id
        """
        pattern = r'watch\?v=([^&]*)'
        video_id = re.search(pattern=pattern,
                             string=self.url).group(1)
        return video_id

    @staticmethod
    def create_folder_final_videos() -> Path:
        """
        Function that creates an output video folder for the
        videos with embedded subtitles if it doesn't exist,
        and returns its path.

        Returns:
            final_folder_path: Path for the final folder
        """
        today_str = date.today().strftime("Videos_%d_%m_%Y")
        final_folder_path = Path(downloads_path).joinpath(today_str)
        if not final_folder_path.exists():
            final_folder_path.mkdir(parents=True, exist_ok=True)
        return final_folder_path


def extract_links(credential_path=gsheet_credentials_path) -> pd.DataFrame:
    """
    Function that connects to the google sheets containing the links,
    and downloads its information as a dataframe.
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


def download_video(video: Video) -> None:
    """
    Function that downloads a video given an url and an output
    folder. It gets downloaded in .mp4 format in the provided
    folder.

    Args:
        video: Instantiated video object

    """

    # Create the directory if it doesn't already exist
    if not video.folder_video_path.exists():
        video.folder_video_path.mkdir(parents=True, exist_ok=True)

    # Set options for video download
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': video.downloaded_video_path.as_posix(),
        'merge_output_format': 'mp4',
    }

    # Download video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video.url])

    print(f"Video {video.name} saved to {video.folder_video_path}")


def download_subtitles(video: Video) -> None:
    """
    Function that downloads subtitles for a given video. First try to
    download them in spanish, if not possible, download them in english
    and properly translate them later.

    Args:
        video: Instantiated video object
    """
    transcript_list = YouTubeTranscriptApi.list_transcripts(video.video_id)
    # Try to get Spanish subtitles
    try:
        srt_captions = transcript_list.find_generated_transcript(['es'])
    except NoTranscriptFound:
        print(f"Couldn't download spanish subtitles for {video.name}, trying english and translating")
        srt_captions = None

    # Get English subtitles and translate them to Spanish
    if srt_captions is None:
        try:
            srt_captions = transcript_list.find_generated_transcript(['en']).translate('es').fetch()
        except Exception:
            raise ValueError('No subtitles available for this video')

    # Generate SRT captions file
    with open(video.downloaded_subtitles_path, 'w', encoding='utf-8') as f:
        for i, caption in enumerate(srt_captions):
            f.write(str(i + 1) + '\n')
            start, end = produce_srt_timestamp(start=caption['start'], duration=caption['duration'])
            f.write(f"{start} --> {end}\n")
            f.write(caption['text'] + '\n\n')

    print(f"Video {video.name} subtitles downloaded successfully")


def produce_srt_timestamp(start: float, duration: float) -> tuple[str, str]:
    """
    Function that takes a start and a duration in seconds as a float and
    returns a suitable outcome to build the srt file. The output has to
    be in "%H:%M:%S,%f" format.
    Args:
        start: second caption starts in seconds
        duration: duration of the caption in screen in seconds

    Returns:
        srt_start_timestamp: string with adequate start timestamp for srt file
        srt_end_timestamp: string with adequate end timestamp for srt file
    """
    start_datetime = datetime.strptime('00:00:00', '%H:%M:%S')
    start_datetime = start_datetime + timedelta(seconds=start)
    end_datetime = start_datetime + timedelta(seconds=duration)
    srt_start_timestamp = start_datetime.strftime("%H:%M:%S,%f")
    srt_end_timestamp = end_datetime.strftime("%H:%M:%S,%f")
    return srt_start_timestamp, srt_end_timestamp

# TODO Manage a robust bucle
