import pytube
import os

def download_video(url, output_path="."):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        print(f"Downloading: {yt.title}...")
        stream.download(output_path)
        print(f"Download completed: {yt.title}")
    except Exception as e:
        print(f"An error occurred: {e}")

def download_playlist(url, output_path="."):
    try:
        playlist = Playlist(url)
        print(f"Downloading playlist: {playlist.title}...")
        for video_url in playlist.video_urls:
            download_video(video_url, output_path)
        print(f"Playlist download completed: {playlist.title}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    choice = input("Do you want to download a single video or a playlist? (video/playlist): ").strip().lower()
    url = input("Enter the URL: ").strip()
    output_path = input("Enter the output directory (leave blank for current directory): ").strip() or "."

    if choice == "video":
        download_video(url, output_path)
    elif choice == "playlist":
        download_playlist(url, output_path)
    else:
        print("Invalid choice. Please enter 'video' or 'playlist'.")

if __name__ == "__main__":
    main()