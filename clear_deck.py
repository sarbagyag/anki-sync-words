import requests

ANKI_URL = "http://localhost:8765"
DECK_NAME = "German A1"

def anki_request(action, **params):
    payload = {"action": action, "version": 6, "params": params}
    response = requests.post(ANKI_URL, json=payload)
    return response.json()

# Wrap deck name in quotes to handle spaces
notes = anki_request("findNotes", query=f'deck:"{DECK_NAME}"')
note_ids = notes.get("result", [])

if not note_ids:
    print("No cards found in deck.")
else:
    result = anki_request("deleteNotes", notes=note_ids)
    print(f"🗑️  Deleted {len(note_ids)} cards from '{DECK_NAME}'")
