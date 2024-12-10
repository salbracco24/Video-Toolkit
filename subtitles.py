import os
import re
import subprocess

SUPPORTED_FILE_EXTENSIONS = ('.mkv', '.mp4')

def encode_subtitles_into_media_file(input_media_file, input_subtitle_file, output_media_file, subtitle_offset):
    ffmpeg_with_args = ['ffmpeg', '-loglevel', '16', '-i', input_media_file]
    if subtitle_offset:
        ffmpeg_with_args.extend(['-itsoffset', subtitle_offset])  # .extend(['-sub_charenc', 'WINDOWS-1252'])
    ffmpeg_with_args.extend(['-i', input_subtitle_file, '-map', '0:v', '-map', '0:a', '-map', '1:s',
                             '-c', 'copy', '-metadata:s:s:0', 'language=eng', output_media_file])
    subprocess.run(ffmpeg_with_args, check=True)

def encode_subtitles_into_all_media_files(shift = False):
    source_folder = input('Source folder: ')
    if not os.path.isdir(source_folder): return
    destination_folder = input('Destination folder: ')
    os.makedirs(destination_folder, exist_ok = True)
    subtitle_offset = input('Subtitle offset: ') or None # example: '100ms'
    operation = 'Fixed' if shift else 'Merged'
    output_media_suffix = f' [{operation}]'
    print()

    media_files = [file for file in os.listdir(source_folder) if file.endswith(SUPPORTED_FILE_EXTENSIONS)]

    for media_file in media_files:
        media_file_path = os.path.join(source_folder, media_file)
        media_file_name, _ = os.path.splitext(media_file)
        subtitle_file_path = media_file_path if shift else os.path.join(source_folder, media_file_name + '.srt')

        if os.path.isfile(subtitle_file_path) or shift:
            output_media_file = media_file_name + output_media_suffix + '.mkv' if source_folder == destination_folder else media_file_name + '.mkv'
            output_file_path = os.path.join(destination_folder, output_media_file)
            encode_subtitles_into_media_file(media_file_path, subtitle_file_path, output_file_path, subtitle_offset)
            print(operation, media_file_name)
        else:
            raise Exception(f'Error: Subtitle not found for {media_file_name}.')

    print('\nAll files processed successfully!')

def encode_subtitles_from_others_into_all_media_files():
    video_source_folder = input('Video source folder: ')
    if not os.path.isdir(video_source_folder): return
    subtitle_source_folder = input('Subtitle source folder: ')
    if not os.path.isdir(subtitle_source_folder): return
    destination_folder = input('Destination folder: ')
    os.makedirs(destination_folder, exist_ok = True)
    subtitle_offset = input('Subtitle offset: ') or None
    output_media_suffix = ' [Merged]'
    pattern = re.compile(r"S\d\dE\d\d")
    print()

    video_files = [file for file in os.listdir(video_source_folder) if file.endswith(SUPPORTED_FILE_EXTENSIONS)]
    subtitle_files = [file for file in os.listdir(subtitle_source_folder) if file.endswith(SUPPORTED_FILE_EXTENSIONS)]

    for video_file in video_files:
        video_file_path = os.path.join(video_source_folder, video_file)
        video_file_name, _ = os.path.splitext(video_file)
        match = pattern.search(video_file_name)
        if not match:
            raise Exception(f'The file {video_file} does not contain a valid episode identifier.')
        episode_id = match[0]
        corresponding_subtitle_files = [file for file in subtitle_files if episode_id in file]
        if len(corresponding_subtitle_files) != 1:
            raise Exception(f'{len(corresponding_subtitle_files)} corresponding subtitles files were found for {video_file}. There should only be one.')
        subtitle_file = corresponding_subtitle_files[0]
        subtitle_file_name, _ = os.path.splitext(subtitle_file)
        subtitle_file_path = os.path.join(subtitle_source_folder, subtitle_file)
        output_media_file = subtitle_file_name + output_media_suffix + '.mkv' if video_source_folder == destination_folder else subtitle_file_name + '.mkv'
        output_file_path = os.path.join(destination_folder, output_media_file)
        encode_subtitles_into_media_file(video_file_path, subtitle_file_path, output_file_path, subtitle_offset)
        print('Merged', subtitle_file_name)
    
    print('\nAll files processed successfully!')
