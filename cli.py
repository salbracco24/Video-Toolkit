import info
import subtitles
import subprocess
import sys

def placeholder():
    print('This temporary placeholder function does nothing.')

def main():
    options = {
        1: ('Print video info', info.print_video_info_for_all),
        2: ('Merge subtitles', subtitles.encode_subtitles_into_all_media_files),
        3: ('Shift subtitles', lambda: subtitles.encode_subtitles_into_all_media_files(shift = True))
    }
    
    print()
    for k, v in options.items():
        print(k, ') ', v[0], sep = '')
    
    try:
        subprocess.run(['ffmpeg', '-version'], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, check = True)
        subprocess.run(['mediainfo', '--Version'], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, check = True)
        optionSelected = int(input('\nChoose an option: '))
        print()
        options.get(optionSelected, ('Exit gracefully', lambda: 0))[1]()
    except KeyboardInterrupt:
        print('\nInterrupted! Exiting gracefully.')
    except Exception as error:
        print(error)
        return 1

if __name__ == '__main__':
    sys.exit(main())
