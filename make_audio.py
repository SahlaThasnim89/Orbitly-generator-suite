# """Two-voice WAV of the fixture sales call — raw SAPI COM (win32com).

# pyttsx3's save_to_file/runAndWait loop stalls after ~2 utterances; the reliable
# Windows path is SAPI.SpVoice + SpFileStream directly. Male voice = Harry,
# female = Sahla, with distinct speaking rates. Single default voice degrades to
# name-prefixed lines.
# """

# import os
# import re
# import wave
# import array
# import tempfile
# from urllib.parse import quote as _q

# import win32com.client
# import pythoncom

# HERE = os.path.dirname(os.path.abspath(__file__))
# SRC = os.path.join(HERE, "meeting_transcript.md")
# OUT = os.path.join(HERE, "meeting_audio.wav")

# LINE_RE = re.compile(r"^\[(\d{2}:\d{2})\]\s+(Harry|Sahla):\s*(.+)$", re.M)
# SAFT22kHz16BitMono = 22
# SSFMCreateForWrite = 3


# def collect_lines():
#     text = open(SRC, encoding="utf-8").read()
#     lines = [(m.group(1), m.group(2), m.group(3).strip())
#              for m in LINE_RE.finditer(text)]
#     if not lines:
#         raise SystemExit("no transcript lines matched")
#     return lines


# def main():
#     pythoncom.CoInitialize()
#     lines = collect_lines()
#     voice = win32com.client.Dispatch("SAPI.SpVoice")
#     voices = list(voice.GetVoices())
#     names = [v.GetAttribute("name") for v in voices]
#     print("installed SAPI voices:", names)

#     def find(*keys):
#         for v in voices:
#             n = v.GetAttribute("name").lower()
#             if any(k in n for k in keys):
#                 return v
#         return None

#     male, female = find("david", "george", "mark", "male"), find("zira", "hazel", "susan", "female")
#     use_prefix = not (male and female)

#     tmp = []
#     for i, (_ts, who, body) in enumerate(lines):
#         text = f"{who}: {body}" if use_prefix else body
#         v = male if who == "Harry" else female
#         if v:
#             voice.Voice = v
#         voice.Rate = 2 if who == "Harry" else 1

#         stream = win32com.client.Dispatch("SAPI.SpFileStream")
#         stream.Format.Type = SAFT22kHz16BitMono
#         path = os.path.join(tempfile.gettempdir(), f"utt3_{i:04d}.wav")
#         stream.Open(path, SSFMCreateForWrite)
#         voice.AudioOutputStream = stream
#         voice.Speak(text)
#         voice.AudioOutputStream = None
#         stream.Close()
#         tmp.append(path)
#         if i % 10 == 0:
#             print(f"synthesized {i + 1}/{len(lines)}", flush=True)

#     first = wave.open(tmp[0], "rb")
#     params = first.getparams()
#     first.close()
#     out = wave.open(OUT, "wb")
#     out.setparams(params)
#     n_ch, sw, fr = params.nchannels, params.sampwidth, params.framerate
#     gap = array.array("h", [0] * int(0.4 * fr) * n_ch)
#     total = 0.0
#     for p in tmp:
#         try:
#             w = wave.open(p, "rb")
#             out.writeframes(w.readframes(w.getnframes()))
#             total += w.getnframes() / fr
#             w.close()
#         except wave.Error:
#             pass
#         out.writeframes(gap.tobytes())
#         os.remove(p)
#     out.close()
#     print(f"WROTE {OUT} — {total / 60:.1f} min, {len(tmp)} turns, "
#           f"{n_ch}ch {sw * 8}-bit {fr}Hz")


# if __name__ == "__main__":
#     main()

"""Two-voice WAV of a fixture sales call — using gTTS (Google Text-to-Speech).
Works on Linux/Mac/Windows. Perfect for cloud hosting like Render or Railway.
"""

import os
import re
import sys
import wave
import array
import tempfile
from gtts import gTTS
from pydub import AudioSegment

HERE = os.path.dirname(os.path.abspath(__file__))

LINE_RE = re.compile(r"^\[(\d{2}:\d{2})\]\s+([A-Za-z][A-Za-z .'-]*):\s*(.+)$", re.M)

# Google TTS voice codes
# tld='com' is a standard male-ish voice, tld='co.uk' gives a different female-ish voice
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

    # Slow down slightly for better clarity (optional)
    tld_for = {speaker_a: VOICE_A_TLD, speaker_b: VOICE_B_TLD}

    tmp = []
    for i, (_ts, who, body) in enumerate(lines):
        text = f"{who}: {body}"
        tld = tld_for.get(who, "com")
        
        # Generate speech using gTTS
        tts = gTTS(text=text, lang='en', tld=tld, slow=False)
        path = os.path.join(tempfile.gettempdir(), f"utt_{i:04d}.mp3")
        tts.save(path)
        tmp.append(path)
        
        if i % 10 == 0:
            print(f"synthesized {i + 1}/{len(lines)}", flush=True)

    # Combine all MP3s into a single WAV file
    print("Combining audio files...")
    combined = AudioSegment.empty()
    gap = AudioSegment.silent(duration=400) # 0.4 second pause

    for p in tmp:
        audio = AudioSegment.from_mp3(p)
        combined += audio + gap
        os.remove(p)

    # Export as WAV (22kHz 16-bit Mono to match your original specs)
    combined = combined.set_frame_rate(22050).set_channels(1).set_sample_width(2)
    combined.export(OUT, format="wav")
    
    duration_sec = len(combined) / 1000.0
    print(f"WROTE {OUT} — {duration_sec / 60:.1f} min, {len(tmp)} turns")

if __name__ == "__main__":
    main()