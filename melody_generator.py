import argparse
import json
import os
import datetime
import asyncio
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel
from midiutil import MIDIFile
from baml_client.async_client import b as async_b  # Import the async client

print("Initializing melody generator...")

# ------------------------------------------------------------------
# 1) Existing data models
# ------------------------------------------------------------------

class NoteDuration(BaseModel):
    note: Optional[int]   # MIDI note number; use None to indicate a rest.
    duration: float       # Duration in beats.

class Instrumentation(BaseModel):
    bass: int
    tenor: int
    alto: int
    soprano: int

class SongMetadata(BaseModel):
    title: str
    tempo: int
    key_signature: str
    time_signature: str
    instruments: Instrumentation

# ------------------------------------------------------------------
# 2) NEW data models for flexible composition plan + final modular piece
# ------------------------------------------------------------------

class SectionPlan(BaseModel):
    label: str
    description: Optional[str]
    number_of_phrases: int

class CompositionPlan(BaseModel):
    plan_title: str
    style: Optional[str]
    sections: List[SectionPlan]

class ModularPhrase(BaseModel):
    phrase_label: str
    bass: List[NoteDuration]
    tenor: List[NoteDuration]
    alto: List[NoteDuration]
    soprano: List[NoteDuration]
    piano: List[NoteDuration]
    percussion: Optional[List[NoteDuration]]

class ModularSection(BaseModel):
    section_label: str
    phrases: List[ModularPhrase]

class ModularPiece(BaseModel):
    metadata: SongMetadata
    sections: List[ModularSection]


# ------------------------------------------------------------------
# 3) Helper functions to convert a ModularPiece to MIDI
# ------------------------------------------------------------------

def remove_c_style_comments(json_str: str) -> str:
    """
    Removes C-style comments (/* ... */) from a JSON string.
    This is needed because sometimes the LLM includes explanatory comments
    which break JSON parsing.
    """
    import re
    # Remove multi-line comments
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    return json_str

def aggregate_modular_piece(piece: ModularPiece) -> Dict[str, List[NoteDuration]]:
    """
    Aggregates all voice lines from each section/phrase into
    a single contiguous list for each voice (Bass, Tenor, Alto,
    Soprano, Piano, Percussion).
    """
    aggregated = {
        "Bass": [],
        "Tenor": [],
        "Alto": [],
        "Soprano": [],
        "Piano": [],
        "Percussion": []
    }

    # Collect notes in the order they appear in each section/phrase
    for section in piece.sections:
        for phrase in section.phrases:
            aggregated["Bass"].extend(phrase.bass)
            aggregated["Tenor"].extend(phrase.tenor)
            aggregated["Alto"].extend(phrase.alto)
            aggregated["Soprano"].extend(phrase.soprano)
            aggregated["Piano"].extend(phrase.piano)
            if phrase.percussion:
                aggregated["Percussion"].extend(phrase.percussion)

    # If no percussion notes were ever added, remove that key
    if not aggregated["Percussion"]:
        del aggregated["Percussion"]

    return aggregated

def save_modular_piece_to_midi(piece: ModularPiece, theme: str, plan: CompositionPlan) -> None:
    """
    Saves the given ModularPiece to:
      1) A MIDI file in 'outputs/<DATE> - <TIME>_<SAFE_THEME>/'
      2) A JSON log file in the same folder
    Using naming conventions consistent with the older code.

    The MIDI file has multiple tracks:
      - Bass (track 0, channel 0)
      - Tenor (track 1, channel 1)
      - Alto (track 2, channel 2)
      - Soprano (track 3, channel 3)
      - Piano (track 4, channel 4)
      - Percussion (track 5, channel 9) if present
    """

    # 1) Create the output folder (timestamped + sanitized theme)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H%M%S")

    safe_theme = "".join(c for c in theme if c.isalnum() or c in (' ', '-')).strip()
    safe_theme = safe_theme.replace(' ', '_')
    theme_folder = os.path.join("outputs", f"{date_str} - {time_str}_{safe_theme}")
    os.makedirs(theme_folder, exist_ok=True)

    # 2) Create a base filename from the piece metadata
    safe_title = "".join(c for c in piece.metadata.title if c.isalnum() or c in (' ', '-')).strip()
    safe_key = "".join(c for c in piece.metadata.key_signature if c.isalnum() or c in (' ', '-')).strip()
    base_filename = f"{date_str} - modular - {safe_title} - {safe_key} - {piece.metadata.tempo}bpm"

    # 3) Aggregate all notes in a dict of voice -> List[NoteDuration]
    voices = aggregate_modular_piece(piece)
    has_percussion = "Percussion" in voices

    # 4) Create the MIDI file
    num_tracks = 6 if has_percussion else 5
    midi_file = MIDIFile(num_tracks)

    # Add the tempo to each track
    for i in range(num_tracks):
        midi_file.addTempo(i, 0, piece.metadata.tempo)

    # Program changes (instrumentation)
    # Bass: track=0/channel=0, Tenor: track=1/channel=1, Alto:2, Soprano:3, Piano:4
    bass_prog = piece.metadata.instruments.bass
    tenor_prog = piece.metadata.instruments.tenor
    alto_prog = piece.metadata.instruments.alto
    soprano_prog = piece.metadata.instruments.soprano
    piano_prog = 0  # piano is always 0

    midi_file.addProgramChange(0, 0, 0, bass_prog)
    midi_file.addProgramChange(1, 1, 0, tenor_prog)
    midi_file.addProgramChange(2, 2, 0, alto_prog)
    midi_file.addProgramChange(3, 3, 0, soprano_prog)
    midi_file.addProgramChange(4, 4, 0, piano_prog)
    # Percussion does not need a program change (channel 9 for track #5)

    # 5) Write out the notes for each voice
    voice_order = ["Bass", "Tenor", "Alto", "Soprano", "Piano"]
    if has_percussion:
        voice_order.append("Percussion")

    for i, voice_name in enumerate(voice_order):
        channel = 9 if voice_name == "Percussion" else i  # channel 9 for percussion
        time_pos = 0.0
        track_notes = voices[voice_name]

        for nd in track_notes:
            if nd.note is not None:
                midi_file.addNote(
                    track=i,
                    channel=channel,
                    pitch=nd.note,
                    time=time_pos,
                    duration=nd.duration,
                    volume=100
                )
            time_pos += nd.duration

    # 6) Save the MIDI file
    midi_filename = os.path.join(theme_folder, f"{base_filename}.mid")
    print(f"\nSaving MIDI file to: {midi_filename}")
    with open(midi_filename, "wb") as f_out:
        midi_file.writeFile(f_out)
    print("MIDI file saved successfully.")

    # 7) Save the JSON log with the raw piece data
    piece_dict = piece.dict()
    log_filename = os.path.join(theme_folder, f"{base_filename}.json")
    print(f"Saving JSON log to: {log_filename}")

    # You can add extra info if desired:
    piece_dict["generation_metadata"] = {
        "user_prompt": theme,
        "model_used": "modular",  # or specify if you prefer
        "timestamp": date_str + " " + time_str,
        "composition_plan": plan.dict()  # Include the composition plan
    }

    with open(log_filename, "w", encoding="utf-8") as f_json:
        json.dump(piece_dict, f_json, indent=2)
    print("JSON log saved successfully.")


# ------------------------------------------------------------------
# 4) Example usage of the new plan + generate approach
# ------------------------------------------------------------------

async def plan_and_generate_modular_song(theme: str) -> None:
    """
    Example function that:
      1) Calls the new BAML function to generate a CompositionPlan
      2) Then calls the second BAML function to fill in the note details
         as a ModularPiece
      3) Saves the final piece to MIDI + JSON, using the naming conventions
         from our older code
    """

    print("\n==== Step 1: Generating the composition plan... ====")
    try:
        plan: CompositionPlan = await async_b.GenerateCompositionPlan(theme=theme)
        print("Successfully got CompositionPlan:")
        print(json.dumps(plan.dict(), indent=2))
    except Exception as e:
        print(f"Error generating composition plan: {e}")
        return

    print("\n==== Step 2: Generating the final modular piece from plan... ====")
    try:
        piece_json = await async_b.GenerateModularSong(plan=plan, theme=theme)
        # If we got a string, clean any C-style comments and parse
        if isinstance(piece_json, str):
            piece_json = remove_c_style_comments(piece_json)
            piece = ModularPiece.parse_raw(piece_json)
        # If we got a dict or BAML client's ModularPiece, convert to dict and parse
        else:
            # Convert to dict if it's not already one
            if not isinstance(piece_json, dict):
                piece_json = piece_json.dict()
            piece = ModularPiece.parse_obj(piece_json)
            
        print("Successfully got final ModularPiece with notes:")
        print(json.dumps(piece.dict(), indent=2))
    except Exception as e:
        print(f"Error generating final modular piece: {e}")
        return

    # Finally, save this piece to MIDI + JSON with old naming conventions
    save_modular_piece_to_midi(piece, theme, plan)


# ------------------------------------------------------------------
# 5) Optional: If you run this file directly, test with a sample theme
# ------------------------------------------------------------------

if __name__ == "__main__":
    print("\nNow testing the two-step modular composition approach...")
    asyncio.run(plan_and_generate_modular_song("Create a jazzy piece with an intro and a chorus"))
