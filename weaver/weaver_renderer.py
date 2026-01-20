import os
import subprocess

# === CONFIGURATION ===
# Assets and output directories.  Ensures a clean workspace.
assets = "assets"
output = "output"
os.makedirs(output, exist_ok=True)

# Input files
bg_image = os.path.join(assets, "background.jpg")
voiceover = os.path.join(assets, "voiceover.wav")
bg_music = os.path.join(assets, "bg_music.mp3")
subtitles = os.path.join(assets, "subtitle_draft.srt")

# Output files
mixed_audio = os.path.join(output, "mixed_audio.mp3")
output_9x16 = os.path.join(output, "final_9-16.mp4")
output_16x9 = os.path.join(output, "final_16-9.mp4")

# === CHECK FILES ===
for f in [bg_image, voiceover, bg_music, subtitles]:
    if not os.path.exists(f):
        print(f"❌ Missing: {f}")
        exit(1)

# === STEP 1: MIX VOICEOVER + MUSIC ===
# Voice 90%, Music 30%.  Mixing is performed locally via FFmpeg.
mix_cmd = [
    "ffmpeg", "-y",
    "-i", voiceover,
    "-i", bg_music,
    "-filter_complex",
    "[0:a]volume=0.9[a1];[1:a]volume=0.3[a2];[a1][a2]amix=inputs=2:duration=longest:dropout_transition=3[aout]",
    "-map", "[aout]",
    mixed_audio
]
print("🎧 Mixing voiceover and background music...")
subprocess.run(mix_cmd, check=True)

# === STEP 2: CREATE 9:16 VIDEO ===
# Utilizing 'flags=lanczos' for crisp image scaling and '-crf 18' for quality.
render_9x16 = [
    "ffmpeg", "-y",
    "-loop", "1",
    "-i", bg_image,
    "-i", mixed_audio,
    "-vf", f"scale=1080:1920:flags=lanczos,subtitles='{subtitles.replace(os.sep, '/')}'",
    "-c:v", "libx264",
    "-crf", "18",
    "-tune", "stillimage",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    output_9x16
]
print("🎥 Rendering vertical (9:16) video...")
subprocess.run(render_9x16, check=True)

# === STEP 3: CREATE 16:9 VIDEO ===
render_16x9 = [
    "ffmpeg", "-y",
    "-loop", "1",
    "-i", bg_image,
    "-i", mixed_audio,
    "-vf", f"scale=1920:1080:flags=lanczos,subtitles='{subtitles.replace(os.sep, '/')}'",
    "-c:v", "libx264",
    "-crf", "18",
    "-tune", "stillimage",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    output_16x9
]
print("🎞️ Rendering horizontal (16:9) video...")
subprocess.run(render_16x9, check=True)

print("\n✅ All done!  Assets processed with technical accuracy.")
