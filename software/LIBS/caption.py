import os
import subprocess
import sys
import requests
from pydub import AudioSegment
import concurrent.futures
import speech_recognition as sr
import time
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog


class Transcriber:
    def __init__(self, video_file_path=None, audio_file_path=None, show_details=None):
        self.video_file_path = video_file_path
        self.audio_file_path = audio_file_path
        self.show_details = show_details
        self.srt_entries = []  # store subtitles (index, start, end, text)

        print(f"Video file path: {video_file_path}\nAudio file path: {audio_file_path}\n")

        # ffmpeg/ffprobe setup
        module_path = os.path.join(os.getcwd(), "module")
        self.ffmpeg_path = os.path.join(module_path, "ffmpeg.exe")
        self.ffprobe_path = os.path.join(module_path, "ffprobe.exe")
        if not os.path.exists(self.ffmpeg_path):
            self.ffmpeg_path = "ffmpeg"  # fallback to system PATH
        if not os.path.exists(self.ffprobe_path):
            self.ffprobe_path = "ffprobe"

        # Windows hide subprocess window
        self.startupinfo = None
        if sys.platform == "win32":
            self.startupinfo = subprocess.STARTUPINFO()
            self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # Speech recognizer
        self.r = sr.Recognizer()

        # Configurable parameters
        self.min_chunk_ms = 15000
        self.max_chunk_ms = 60000
        self.target_chunks = 20
        self.max_workers = 8

    def _calculate_chunk_size(self, duration_ms: int) -> int:
        if duration_ms <= 5 * 60 * 1000:
            return max(self.min_chunk_ms, min(self.max_chunk_ms, duration_ms))
        chunk_size = duration_ms // self.target_chunks
        return max(self.min_chunk_ms, min(self.max_chunk_ms, chunk_size))

    def _format_srt_time(self, ms):
        """Convert milliseconds to SRT timestamp format"""
        seconds, ms = divmod(ms, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

    def transcribe_audio_chunk(self, chunk_path, retries=3, delay=2):
        for attempt in range(retries):
            try:
                with sr.AudioFile(chunk_path) as source:
                    audio = self.r.record(source)
                    return self.r.recognize_google(audio)
            except Exception as e:
                print(f"[Error] Chunk {chunk_path} failed: {e} (Attempt {attempt+1}/{retries})")
                time.sleep(delay)
        return ""

    def transcribe_audio_google_parallel(self, mode="balance"):
        sound = AudioSegment.from_file(self.audio_file_path)
        duration_ms = len(sound)

        chunk_length_ms = self._calculate_chunk_size(duration_ms)
        workers = self.max_workers

        if mode == "high":
            chunk_length_ms = min(self.max_chunk_ms * 2, duration_ms)
            workers = min(16, self.max_workers * 2)
            print(f"[Info] Mode: HIGH SPEED | {chunk_length_ms/1000:.1f} sec chunks | {workers} workers")
        elif mode == "accuracy":
            chunk_length_ms = max(self.min_chunk_ms // 2, 10000)
            workers = max(4, self.max_workers // 2)
            print(f"[Info] Mode: HIGH ACCURACY | {chunk_length_ms/1000:.1f} sec chunks | {workers} workers")
        else:
            print(f"[Info] Mode: BALANCE | {chunk_length_ms/1000:.1f} sec chunks | {workers} workers")

        # Create chunks with timestamps
        folder_name = tempfile.mkdtemp(prefix="audio_chunks_")
        chunk_paths = []
        start = 0
        i = 0
        while start < duration_ms:
            end = min(start + chunk_length_ms, duration_ms)
            chunk = sound[start:end]
            path = os.path.join(folder_name, f"chunk{i}.wav")
            chunk.export(path, format="wav")
            chunk_paths.append((i, path, start, end))  # store timing info
            start = end
            i += 1

        # Parallel transcription
        self.srt_entries.clear()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self.transcribe_audio_chunk, path[1]): path for path in chunk_paths}
            total = len(chunk_paths)
            for idx, future in enumerate(concurrent.futures.as_completed(futures)):
                (index, path, start_ms, end_ms) = futures[future]
                try:
                    text = future.result()
                    if text.strip():
                        self.srt_entries.append(
                            (index + 1, self._format_srt_time(start_ms), self._format_srt_time(end_ms), text)
                        )
                except Exception as e:
                    print(f"[Error] Failed transcription for chunk {index}: {e}")
                progress = (idx + 1) / total * 100
                if self.show_details:
                    self.show_details.configure(text=f"Progress — {progress:.2f}%")
                print(f"Progress: {progress:.2f}%")

        shutil.rmtree(folder_name)  # clean temp chunks

        # Build SRT text string
        srt_text = ""
        for idx, start, end, text in sorted(self.srt_entries, key=lambda x: x[0]):
            srt_text += f"{idx}\n{start} --> {end}\n{text}\n\n"

        return srt_text

    def generate_srt(self):
        """Ask user where to save .srt file and then write captions."""

        file_path = filedialog.asksaveasfilename(
            title="Save SRT File",
            defaultextension=".srt",
            filetypes=[("Subtitle files", "*.srt"), ("All files", "*.*")]
        )

        if not file_path:
            print("[Info] Save cancelled.")
            return None

        with open(file_path, "w", encoding="utf-8") as f:
            for idx, start, end, text in sorted(self.srt_entries, key=lambda x: x[0]):
                f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")

        print(f"[Info] SRT saved to {file_path}")
        return file_path

    def _force_convert_to_wav(self, input_path):
        temp_wav = tempfile.mktemp(suffix=".wav")
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-sample_fmt", "s16",
            temp_wav
        ]
        subprocess.run(cmd, check=True, startupinfo=self.startupinfo)
        return temp_wav

    def video_to_text(self, mode="balance"):
        if not self.video_file_path:
            return "[Error] No video file provided."

        self.audio_file_path = tempfile.mktemp(suffix=".wav")
        try:
            subprocess.run(
                [self.ffmpeg_path, "-y", "-i", self.video_file_path,
                 "-vn", "-ar", "16000", "-ac", "1", "-sample_fmt", "s16", self.audio_file_path],
                check=True, startupinfo=self.startupinfo
            )
        except subprocess.CalledProcessError as e:
            return f"[Error] FFmpeg failed: {e}"

        return self.transcribe_audio_google_parallel(mode=mode)

    def audio_to_text(self, mode="balance"):
        if not self.audio_file_path:
            return "[Error] No audio file provided."

        if not self.audio_file_path.lower().endswith(".wav"):
            self.audio_file_path = self._force_convert_to_wav(self.audio_file_path)

        return self.transcribe_audio_google_parallel(mode=mode)


# ============================
# Example Usage
# ============================
'''if __name__ == "__main__":
    t = Transcriber(audio_file_path="audio.mp3")
    srt_result = t.audio_to_text(mode="balance")

    print("\nGenerated SRT:\n")
    print(srt_result)  # prints SRT-format subtitles

    # Save via file dialog
    t.generate_srt()'''