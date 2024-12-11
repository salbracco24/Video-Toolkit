import json
import os
import subprocess
from utils import to_truth_label

SUPPORTED_VIDEO_FILE_EXTENSIONS = ('.avi', '.flv', '.m4v', '.mkv', '.mov', '.mp4', '.wmv')

def get_media_info(file_path):
    mediainfo_command = ['mediainfo', '-f', '--Output=JSON', file_path]
    result = subprocess.run(mediainfo_command, capture_output=True, check=True, encoding='utf8', text=True)
    return json.loads(result.stdout)

def get_track_by_type(media_info_result, track_type):
    return next((item for item in media_info_result['media']['track'] if item.get("@type") == track_type), None)

def durations_difference(video_file_path, subtitle_file_path):
    video_file_audio_duration = float(get_track_by_type(get_media_info(video_file_path), 'Audio')['Duration'])
    subtitle_file_audio_duration = float(get_track_by_type(get_media_info(subtitle_file_path), 'Audio')['Duration'])
    return video_file_audio_duration - subtitle_file_audio_duration

def has_picture_based_subtitles(video_file_path):
    subtitle_codec_id_info = get_track_by_type(get_media_info(video_file_path), 'Text')['CodecID_Info']
    return 'Picture' in subtitle_codec_id_info

def print_video_info_for_all():
    directory = input('Directory: ')
    print()
    for root, _, files in os.walk(directory):
        if files: print(os.path.basename(root), '-' * 150, sep = '\n')
        for file in files:
            if file.endswith(SUPPORTED_VIDEO_FILE_EXTENSIONS):
                media_info = get_media_info(os.path.join(root, file))
                subtitles_present = any(track['@type'] == 'Text' and track.get('Language') in ('en', 'en-US') for track in media_info['media']['track'])
                video_info = get_track_by_type(media_info, 'Video')
                print('{:75.75}  Width: {:6} Height: {:6} Codec: {:7.7} BitDepth: {:3} Subtitles: {}'
                    .format(file, video_info['Width'], video_info['Height'], video_info['Format'], video_info.get('BitDepth', ''), to_truth_label(subtitles_present)))
        if files: print('-' * 150)
