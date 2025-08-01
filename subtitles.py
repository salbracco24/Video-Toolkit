import info
import os
import re
import subprocess

SUPPORTED_FILE_EXTENSIONS = ('.mkv', '.mp4')
EPISODE_PATTERN = re.compile(r"(?i)S\d\dE\d\d")
FFS_PATTERN = re.compile(r"(?s)score:\s*(\d+\.\d+).*offset seconds:\s*(-?\d+\.\d+)")

def extract_subtitles_from_media_file(input_media_file, output_subtitle_file):
    ffmpeg_with_args = ['ffmpeg', '-loglevel', '16', '-i', input_media_file, '-c', 'srt', output_subtitle_file]
    return subprocess.run(ffmpeg_with_args, capture_output=True)

def encode_subtitles_into_media_file(input_media_file, input_subtitle_file, output_media_file, subtitle_offset):
    ffmpeg_with_args = ['ffmpeg', '-loglevel', '16', '-i', input_media_file]
    if subtitle_offset:
        ffmpeg_with_args.extend(['-itsoffset', subtitle_offset])  # .extend(['-sub_charenc', 'WINDOWS-1252'])
    ffmpeg_with_args.extend(['-i', input_subtitle_file, '-map', '0:v', '-map', '0:a', '-map', '1:s', '-c', 'copy'])
    if output_media_file.endswith('.mp4'):
        ffmpeg_with_args.extend(['-c:s', 'mov_text'])
    ffmpeg_with_args.extend(['-metadata:s:s:0', 'language=eng', output_media_file])
    return subprocess.run(ffmpeg_with_args, check=True)

def sync_subtitles_with_media_file(input_media_file, input_subtitle_file, output_subtitle_file):
    ffs_with_args = ['ffs', '-i', input_subtitle_file, '-o', output_subtitle_file, input_media_file]
    return subprocess.run(ffs_with_args, capture_output=True, text=True)

def extract_subtitles_from_all_media_files(source_folder=None, destination_folder=None):
    source_folder = source_folder or input('Source folder: ')
    if not os.path.isdir(source_folder): return
    destination_folder = destination_folder or input('Destination folder: ')
    os.makedirs(destination_folder, exist_ok = True)
    print()
    
    media_files = [file for file in os.listdir(source_folder) if file.endswith(SUPPORTED_FILE_EXTENSIONS)]

    for media_file in media_files:
        media_file_path = os.path.join(source_folder, media_file)
        media_file_name, _ = os.path.splitext(media_file)
        episode_identifier_match = EPISODE_PATTERN.search(media_file_name)
        subtitle_file_name = episode_identifier_match[0].upper() if episode_identifier_match else media_file_name
        if not episode_identifier_match: print(f'Error: {media_file_name} does not contain a valid episode identifier, full name used instead.')
        subtitle_file_path = os.path.join(destination_folder, subtitle_file_name + '.srt')
        result = extract_subtitles_from_media_file(media_file_path, subtitle_file_path)
        print(f'Extracted subtitles from {media_file_name}' if not result.returncode else f'Error: Did not extract subtitles from {media_file_name}')

    print('\nAll files processed successfully!')

def encode_subtitles_into_all_media_files(source_folder=None, destination_folder=None, subtitle_offset=None, shift=False):
    source_folder = source_folder or input('Source folder: ')
    if not os.path.isdir(source_folder): return
    destination_folder = destination_folder or input('Destination folder: ')
    os.makedirs(destination_folder, exist_ok = True)
    subtitle_offset = subtitle_offset or input('Subtitle offset: ') or None # example: '100ms'
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

def sync_subtitles_with_all_media_files(media_source_folder=None, subtitles_source_folder=None, subtitles_destination_folder=None):
    media_source_folder = media_source_folder or input('Media source folder: ')
    if not os.path.isdir(media_source_folder): return
    subtitles_source_folder = subtitles_source_folder or input('Subtitles source folder: ')
    if not os.path.isdir(subtitles_source_folder): return
    subtitles_destination_folder = subtitles_destination_folder or media_source_folder or input('Subtitles destination folder: ')
    print(f'Subtitles destination folder: {subtitles_destination_folder}')
    # os.makedirs(subtitles_destination_folder, exist_ok = True)
    print()
    
    media_files = [file for file in os.listdir(media_source_folder) if file.endswith(SUPPORTED_FILE_EXTENSIONS)]

    for media_file in media_files:
        media_file_path = os.path.join(media_source_folder, media_file)
        media_file_name, _ = os.path.splitext(media_file)
        episode_identifier_match = EPISODE_PATTERN.search(media_file_name)
        if not episode_identifier_match:
            print(f'Error: {media_file_name} does not contain a valid episode identifier, skipping.')
            continue
        subtitle_source_file_name = episode_identifier_match[0].upper()
        subtitle_source_file_path = os.path.join(subtitles_source_folder, subtitle_source_file_name + '.srt')
        subtitle_destination_file_path = os.path.join(subtitles_destination_folder, media_file_name + '.srt')
        if os.path.isfile(subtitle_destination_file_path):
            print(f'Skipping since this file already exists: {media_file_name + '.srt'}')
            continue
        
        result = sync_subtitles_with_media_file(media_file_path, subtitle_source_file_path, subtitle_destination_file_path)
        
        if not result.returncode:
            sync_data = FFS_PATTERN.search(result.stderr)
            if sync_data:
                score = float(sync_data[1])
                offset_seconds = float(sync_data[2])
            else:
                raise Exception(f'Unexpected output from ffs\nstdout: {result.stdout}\nstderr: {result.stderr}')
            print(f'Synced subs with {media_file_name:50.50}  Offset: {offset_seconds:6.3f}s  Score: {score:10.3f}')
        else:
            print(f'Error: Did not align subtitles {subtitle_source_file_name} with {media_file_name}\nstderr: {result.stderr}')

    print('\nAll files processed successfully!')

def encode_subtitles_from_others_into_all_media_files(video_source_folder=None, subtitle_source_folder=None, destination_folder=None, subtitle_offset=None, log_file=None):
    log = (lambda msg: print(msg, file=log_file)) if log_file else print
    video_source_folder = video_source_folder or input('Video source folder: ')
    if not os.path.isdir(video_source_folder): return
    subtitle_source_folder = subtitle_source_folder or input('Subtitle source folder: ')
    if not os.path.isdir(subtitle_source_folder): return
    destination_folder = destination_folder or input('Destination folder: ')
    os.makedirs(destination_folder, exist_ok = True)
    original_subtitle_offset = subtitle_offset
    subtitle_offset = subtitle_offset # or input('Subtitle offset: ') or None
    max_difference = 1 # 1s
    max_ignorable_difference = 0.05 # 50ms
    output_media_suffix = ' [Merged]'
    print()

    video_files = [file for file in os.listdir(video_source_folder) if file.endswith(SUPPORTED_FILE_EXTENSIONS)]
    subtitle_files = [file for file in os.listdir(subtitle_source_folder) if file.endswith(SUPPORTED_FILE_EXTENSIONS)]

    for video_file in video_files:
        video_file_path = os.path.join(video_source_folder, video_file)
        video_file_name, video_file_extension = os.path.splitext(video_file)
        match = EPISODE_PATTERN.search(video_file_name)
        if not match:
            log(f'The file {video_file} does not contain a valid episode identifier.')
            continue
        episode_id = match[0]
        corresponding_subtitle_files = [file for file in subtitle_files if episode_id in file]
        if len(corresponding_subtitle_files) != 1:
            raise Exception(f'{len(corresponding_subtitle_files)} corresponding subtitles files were found for {video_file}. There should only be one.')
        subtitle_file = corresponding_subtitle_files[0]
        subtitle_file_name, _ = os.path.splitext(subtitle_file)
        subtitle_file_path = os.path.join(subtitle_source_folder, subtitle_file)

        diff = info.durations_difference(video_file_path, subtitle_file_path)
        if max_ignorable_difference < abs(diff) < max_difference:
            subtitle_offset = str(diff) + 's'
            log(f'Difference <{diff:.3f}> used as subtitle offset for: {video_file_name}')
        if abs(diff) > max_difference:
            log(f'Difference: <{diff:.3f}> is too large to correct. Skipped: {video_file_name}')
            continue

        output_file_extension = '.mkv' if video_file_extension == '.mkv' or info.has_picture_based_subtitles(subtitle_file_path) else '.mp4'
        output_file_name = subtitle_file_name + output_media_suffix if video_source_folder == destination_folder else subtitle_file_name
        output_file_path = os.path.join(destination_folder, output_file_name + output_file_extension)
        encode_subtitles_into_media_file(video_file_path, subtitle_file_path, output_file_path, subtitle_offset)
        success_msg = f'Merged {subtitle_file_name} with offset {subtitle_offset}' if subtitle_offset else f'Merged {subtitle_file_name}'
        print(success_msg)
        subtitle_offset = original_subtitle_offset # reset the offset, in case it was changed
    print('\nAll files processed successfully!')
    log(f'END OF FOLDER {os.path.basename(destination_folder)}')

def encode_subtitles_from_others_into_all_media_files_in_multiple_directories():
    with open('errors.txt', 'a', encoding='utf-8') as f:
        for i in range(0, 21):
            video_source_folder = fr''
            subtitle_source_folder = fr''
            destination_folder = fr''
            encode_subtitles_from_others_into_all_media_files(video_source_folder, subtitle_source_folder, destination_folder, log_file=f)
