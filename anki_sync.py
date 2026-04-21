import requests
import gspread
import base64
import os
import builtins
from datetime import datetime
from gtts import gTTS
from google.oauth2.service_account import Credentials

# --- Timestamped print ---
_original_print = builtins.print
def print(*args, **kwargs):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    _original_print(timestamp, *args, **kwargs)

# --- Config ---
SHEET_ID = "1tQ8nvi6yzmWtEEyIy_515UzEMU36T4fz7RX2rXXS7Gg"
ANKI_URL = "http://localhost:8765"
DECK_NAME = "German A2"
MODEL_NAME = "Basic"
CREDS_FILE = "/Users/sarbagya/scripts/google_creds.json"
AUDIO_TMP_DIR = "/tmp/anki_audio"


def anki_request(action, **params):
    payload = {"action": action, "version": 6, "params": params}
    response = requests.post(ANKI_URL, json=payload)
    return response.json()


def generate_audio(word):
    """Generate German pronunciation audio and store in Anki media collection."""
    # Clean filename — remove articles and special chars
    safe_name = word.replace(" ", "_").replace("/", "_")
    filename = f"german_{safe_name}.mp3"
    filepath = os.path.join(AUDIO_TMP_DIR, filename)

    # Generate audio file
    tts = gTTS(word, lang="de")
    tts.save(filepath)

    # Read and encode as base64
    with open(filepath, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode()

    # Store in Anki's media collection
    anki_request("storeMediaFile", filename=filename, data=audio_data)

    # Cleanup temp file
    os.remove(filepath)

    return f"[sound:{filename}]"


def add_anki_card(word, word_type, english, example_de, example_en):
    # Generate pronunciation audio
    audio_tag = generate_audio(word)

    front = (
        f"<b>{word}</b>&nbsp;&nbsp;<i>[{word_type}]</i><br>"
        f"{audio_tag}<br><br>"
        f"<i>{example_de}</i>"
    )
    back = f"<b>{english}</b><br><br>{example_en}"

    result = anki_request(
        "addNote",
        note={
            "deckName": DECK_NAME,
            "modelName": MODEL_NAME,
            "fields": {
                "Front": front,
                "Back": back
            },
            "tags": ["german", "a1", "daily", word_type]
        }
    )
    return result


def main():
    # Create temp audio directory
    os.makedirs(AUDIO_TMP_DIR, exist_ok=True)

    print("🔄 Connecting to Google Sheets...")
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.sheet1

    rows = ws.get_all_records()
    print(f"📊 Found {len(rows)} rows in sheet")

    synced_cells = []
    synced_count = 0
    skipped_count = 0

    for i, row in enumerate(rows, start=2):
        # Skip empty rows or already synced
        if not row.get("Word") or row.get("Synced") == "yes":
            continue

        word = row.get("Word", "").strip()
        word_type = row.get("Type", "").strip()
        english = row.get("English", "").strip()
        example_de = row.get("Example (DE)", "").strip()
        example_en = row.get("Example (EN)", "").strip()

        # Skip separator blank rows
        if not word:
            continue

        result = add_anki_card(word, word_type, english, example_de, example_en)

        if result.get("error") is None:
            synced_cells.append(gspread.Cell(i, 7, "yes"))
            synced_count += 1
            print(f"✅ Added: {word} [{word_type}] 🔊")
        else:
            error = result.get("error", "unknown error")
            # Duplicate notes are fine, just mark as synced
            if "duplicate" in str(error).lower():
                synced_cells.append(gspread.Cell(i, 7, "yes"))
                print(f"⏭️  Duplicate (already in Anki): {word}")
            else:
                skipped_count += 1
                print(f"⚠️  Skipped {word}: {error}")

    # Batch write all synced marks in ONE API call
    if synced_cells:
        print(f"\n📝 Marking {len(synced_cells)} rows as synced...")
        ws.update_cells(synced_cells)

    print(f"\n✅ Done! {synced_count} new cards added to Anki with pronunciation.")
    if skipped_count > 0:
        print(f"⚠️  {skipped_count} cards skipped (check errors above)")


if __name__ == "__main__":
    main()
