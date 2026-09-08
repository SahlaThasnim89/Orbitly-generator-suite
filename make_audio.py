"""Two-voice WAV of a fixture sales call — using gTTS (Google Text-to-Speech) with multithreading for speed.
"""

import os
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

from gtts import gTTS
from pydub import AudioSegment
import imageio_ffmpeg

# Tell pydub to use the automatically downloaded ffmpeg executable
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

HERE = os.path.dirname(os.path.abspath(__file__))

LINE_RE = re.compile(r"^\[(\d{2}:\d{2})\]\s+([A-Za-z][A-Za-z .'-]*):\s*(.+)$", re.M)

# Google TTS voice codes
VOICE_A_TLD = "com"   # First speaker
VOICE_B_TLD = "co.uk"  # Second speaker

def collect_lines(src_path):
    text = open(src_path, encoding="utf-8").read()
    lines = [(m.group(1), m.group(2).strip(), m.group(3).strip())
             for m in LINE_RE.finditer(text)]
    if not lines:
        raise SystemExit(f"no transcript lines matched in {src_path}")
    return lines

def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python make_audio.py <transcript.md>")

    src_arg = sys.argv[1]
    SRC = src_arg if os.path.isabs(src_arg) else os.path.join(HERE, src_arg)
    base = os.path.splitext(os.path.basename(SRC))[0]
    OUT = os.path.join(HERE, f"{base}_audio.wav")

    lines = collect_lines(SRC)

    # Auto-detect the two speaker names
    speakers = []
    for _ts, who, _body in lines:
        if who not in speakers:
            speakers.append(who)
        if len(speakers) == 2:
            break
    if len(speakers) < 2:
        raise SystemExit(f"expected 2 distinct speakers, found: {speakers}")
    
    speaker_a, speaker_b = speakers[0], speakers[1]
    print(f"detected speakers: A={speaker_a!r}, B={speaker_b!r}")

    tld_for = {speaker_a: VOICE_A_TLD, speaker_b: VOICE_B_TLD}

    # --- MULTITHREADING SPEED BOOST ---
    def process_line(index, line_data):
        _ts, who, body = line_data
        text = f"{who}: {body}"
        tld = tld_for.get(who, "com")
        
        tts = gTTS(text=text, lang='en', tld=tld, slow=False)
        path = os.path.join(tempfile.gettempdir(), f"utt_{index:04d}.mp3")
        tts.save(path)
        return path

    print(f"Synthesizing {len(lines)} lines in parallel (30 at a time)...")
    tmp = []
    # Increased from 15 to 30 workers for faster downloads
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_line, i, line) for i, line in enumerate(lines)]
        for future in futures:
            tmp.append(future.result())

    print("Combining audio files...")
    # Optimized pydub stitching to use less CPU memory
    combined = AudioSegment.silent(duration=0)
    gap = AudioSegment.silent(duration=400) # 0.4 second pause

    for p in tmp:
        audio = AudioSegment.from_mp3(p)
        combined = combined.append(audio, crossfade=0)
        combined = combined.append(gap, crossfade=0)
        os.remove(p)

    # Export as WAV (22kHz 16-bit Mono)
    combined = combined.set_frame_rate(22050).set_channels(1).set_sample_width(2)
    combined.export(OUT, format="wav")
    
    duration_sec = len(combined) / 1000.0
    print(f"WROTE {OUT} — {duration_sec / 60:.1f} min, {len(tmp)} turns")

if __name__ == "__main__":
    main()