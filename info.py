import json
import os
import subprocess
from utils import to_truth_label

SUPPORTED_VIDEO_FILE_EXTENSIONS = ('.avi', '.flv', '.m4v', '.mkv', '.mov', '.mp4', '.wmv')

def get_media_info(file_path):
    mediainfo_command = ['mediainfo', '--Output=JSON', file_path]
    result = subprocess.run(mediainfo_command, capture_output=True, check=True, encoding='utf8', text=True)
    return json.loads(result.stdout)

def print_video_info_for_all():
    directory = input('Directory: ')
    print()
    for root, _, files in os.walk(directory):
        if files: print(os.path.basename(root), '-' * 150, sep = '\n')
        for file in files:
            if file.endswith(SUPPORTED_VIDEO_FILE_EXTENSIONS):
                media_info = get_media_info(os.path.join(root, file))
                subtitles_present = any(track['@type'] == 'Text' and track.get('Language') in ('en', 'en-US') for track in media_info['media']['track'])
                video_info = media_info['media']['track'][1]
                print('{:75.75}  Width: {:6} Height: {:6} Codec: {:7.7} BitDepth: {:3} Subtitles: {}'
                    .format(file, video_info['Width'], video_info['Height'], video_info['Format'], video_info.get('BitDepth', ''), to_truth_label(subtitles_present)))
        if files: print('-' * 150)
