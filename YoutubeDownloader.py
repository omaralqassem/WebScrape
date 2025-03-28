from asyncio import exceptions
import os
import sys
import re
from tqdm import tqdm
from pytubefix import YouTube,Playlist
def sanitize_filename(title):
    """Sanitize filenames by replacing invalid characters"""
    return re.sub(r'[\/:*?"<>|]', '_', title)

def download_video(url, output_path=".", as_mp3=False, preferred_res=None):
    yt = None
    temp_file = None
    try:
        yt = YouTube(url)
        safe_title = sanitize_filename(yt.title)
        
        final_ext = ".mp3" if as_mp3 else ".mp4"
        final_filename = f"{safe_title}{final_ext}"
        final_path = os.path.join(output_path, final_filename)
        
        if os.path.exists(final_path):
            print(f"File already exists: {final_filename}")
            return

        if as_mp3:
            stream = yt.streams.filter(only_audio=True).first()
            if not stream:
                raise ValueError("No audio stream available")
        else:
            if preferred_res:
                stream = yt.streams.filter(
                    progressive=True, 
                    resolution=preferred_res
                ).first()
                if not stream:
                    print(f"Resolution {preferred_res} not available. Using highest.")
                    stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.get_highest_resolution()

        temp_filename = f"{safe_title}.temp"
        temp_path = os.path.join(output_path, temp_filename)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with tqdm(
                    total=stream.filesize,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"Downloading {safe_title}",
                    leave=True,
                ) as pbar:
                    
                    yt.register_on_progress_callback(
                        lambda s, c, rem: pbar.update(stream.filesize - rem - pbar.n)
                    )
                    
                    temp_file = stream.download(
                        output_path=output_path,
                        filename=os.path.basename(temp_path)
                    )
                    
                    os.rename(temp_file, final_path)
                    print(f"\nDownload completed: {safe_title}")
                    return

            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if attempt == max_retries - 1:
                    raise e
                print(f"\nAttempt {attempt+1} failed. Retrying...")

    except exceptions.RegexMatchError:
        print("Invalid YouTube URL")
    except exceptions.VideoUnavailable:
        print("Video is unavailable")
    except Exception as e:
        print(f"Error: {str(e)}")
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(final_path):
            os.remove(final_path)
    finally:
        if 'yt' in locals() and yt:
            yt.register_on_progress_callback(None)

def download_playlist(url, output_path=".", as_mp3=False):
    try:
        playlist = Playlist(url)
        print(f"Downloading playlist: {playlist.title} (may take a while to gather info)")
        
        valid_urls = []
        for video_url in playlist.video_urls:
            try:
                YouTube(video_url).check_availability()
                valid_urls.append(video_url)
            except:
                print(f"Skipping unavailable video: {video_url}")
        
        total = len(valid_urls)
        for i, video_url in enumerate(valid_urls, 1):
            print(f"\nDownloading video {i}/{total}")
            download_video(video_url, output_path, as_mp3)
        
        print(f"\nPlaylist download completed: {playlist.title}")

    except exceptions.RegexMatchError:
        print("Invalid playlist URL")
    except Exception as e:
        print(f"Playlist error: {str(e)}")

def main():
    try:
        choice = input("Download single video or playlist? (video/playlist): ").strip().lower()
        url = input("Enter URL: ").strip()
        output_path = input("Output directory (blank for current): ").strip() or "."
        output_path = os.path.abspath(output_path)
        
        # Validate output directory
        if not os.path.exists(output_path):
            create = input("Directory doesn't exist. Create? (yes/no): ").strip().lower()
            if create == "yes":
                os.makedirs(output_path)
            else:
                sys.exit("Download aborted")
        elif not os.path.isdir(output_path):
            sys.exit("Invalid directory path")

        as_mp3 = input("Download as MP3? (yes/no): ").strip().lower() == "yes"
        preferred_res = None

        if choice == "video":
            select_res = input("Select specific resolution? (yes/no): ").strip().lower()
            if select_res == "yes":
                try:
                    yt = YouTube(url)
                    res_set = {s.resolution for s in yt.streams.filter(progressive=True)}
                    res_list = sorted(res_set, reverse=True) if res_set else []
                    if res_list:
                        print("Available resolutions:", ", ".join(res_list))
                        preferred_res = input("Enter resolution (e.g. 720p): ").strip()
                    else:
                        print("No resolutions found. Using default.")
                except:
                    print("Couldn't fetch resolutions. Using default.")

            download_video(url, output_path, as_mp3, preferred_res)
            
        elif choice == "playlist":
            download_playlist(url, output_path, as_mp3)
            
        else:
            print("Invalid choice. Please enter 'video' or 'playlist'.")

    except KeyboardInterrupt:
        print("\nDownload cancelled by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main()
