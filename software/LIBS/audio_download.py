import os
import subprocess

def download_youtube_audio(url, format="mp3"):
    ytdlp_path = os.path.join(os.getcwd(), "module", "yt.exe")

    if not os.path.exists(ytdlp_path):
        raise FileNotFoundError(f"yt-dlp.exe not found at {ytdlp_path}")

    appdata = os.getenv('APPDATA')
    quilla_folder = os.path.join(appdata, '.Quilla', 'audio')
    os.makedirs(quilla_folder, exist_ok=True)

    output_file = os.path.join(quilla_folder, f"audio.{format}")
    cmd = [
        ytdlp_path,
        "-x",
        "--audio-format", format,
        "-o", output_file,
        "--force-overwrites",
        url
    ]

    # 🚫 No console window
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW

    try:
        subprocess.run(cmd, check=True, creationflags=CREATE_NO_WINDOW)
        print("✅ Download complete.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading: {e}")

# Example call
# download_youtube_audio("https://youtu.be/M7u9cVwLnm4?si=n-m_xndylp0THWF9")
