"""
Standalone TTS helper script. Run as:
    python speak_subprocess.py "Text to speak"
This runs pyttsx3 in an isolated process with no Qt/COM conflicts.
"""
import sys
import pyttsx3

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    if not text.strip():
        sys.exit(0)

    try:
        engine = pyttsx3.init('sapi5')
        engine.setProperty('rate', 175)
        engine.setProperty('volume', 1.0)

        voices = engine.getProperty('voices')
        if voices:
            chosen = voices[0].id
            for v in voices:
                if 'zira' in v.name.lower():
                    chosen = v.id
                    break
            engine.setProperty('voice', chosen)

        engine.say(text)
        engine.runAndWait()
        sys.exit(0)
    except Exception as e:
        print(f"pyttsx3 error: {e}", file=sys.stderr)
        # Fallback: try PowerShell SAPI5
        import subprocess
        safe = text.replace("'", "").replace('"', "").replace("\n", " ")
        ps = (
            f'powershell -Command "Add-Type -AssemblyName System.Speech; '
            f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
            f'$s.Rate = 1; $s.Volume = 100; $s.Speak(\'{safe}\')"'
        )
        r = subprocess.run(ps, shell=True)
        sys.exit(r.returncode)

if __name__ == "__main__":
    main()
