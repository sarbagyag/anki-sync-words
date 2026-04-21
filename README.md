# Anki Sync — German Vocabulary

Syncs a Google Sheet of German vocabulary words into Anki flashcards, with auto-generated pronunciation audio.

## How it works

1. Reads rows from a Google Sheet (Word, Type, English translation, German example, English example)
2. Generates an MP3 pronunciation via gTTS and stores it in Anki's media collection
3. Creates a flashcard in the configured deck with the word, audio, and example sentence on the front; translation on the back
4. Marks synced rows with `yes` in column G so they're skipped on subsequent runs

## Setup

### Requirements

- [Anki](https://apps.ankiweb.net/) with the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on installed and running
- Python 3.9+

```bash
pip install requests gspread google-auth gtts
```

### Google Sheets credentials

1. Create a service account in [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Enable the **Google Sheets API** for your project
3. Download the JSON key and save it as `google_creds.json` next to the script
4. Share your Google Sheet with the service account's email address (Viewer is enough)

### Sheet format

| Word | Type | English | Example (DE) | Example (EN) | (unused) | Synced |
|------|------|---------|--------------|--------------|----------|--------|
| die Katze | noun | the cat | Die Katze schläft. | The cat sleeps. | | yes |

Column G (`Synced`) is written automatically — leave it blank for new rows.

### Config

Edit the constants at the top of `anki_sync.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SHEET_ID` | `1tQ8n...` | Your Google Sheet ID (from the URL) |
| `DECK_NAME` | `German A2` | Target Anki deck |
| `MODEL_NAME` | `Basic` | Anki note type |
| `CREDS_FILE` | `google_creds.json` | Path to your service account key |

## Usage

```bash
# Sync new words from the sheet to Anki
python anki_sync.py

# Delete all cards from the deck (destructive — use with care)
python clear_deck.py
```

Anki must be open when you run either script.

## Card format

**Front:** Word + word type + pronunciation audio + German example sentence  
**Back:** English translation + English example sentence
