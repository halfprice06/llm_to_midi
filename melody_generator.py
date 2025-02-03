import argparse
import json
import os
import datetime
import asyncio
from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field
from midiutil import MIDIFile
from baml_client.async_client import b as async_b  # Import the async client

print("Initializing melody generator...")

def preprocess_section_json(section_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocesses the section data to handle null percussion values before validation.
    If percussion is null, removes it from the phrase entirely.
    """
    if not isinstance(section_data, dict):
        return section_data
        
    if "phrases" in section_data and isinstance(section_data["phrases"], list):
        for phrase in section_data["phrases"]:
            if isinstance(phrase, dict) and "percussion" in phrase and phrase["percussion"] is None:
                del phrase["percussion"]
    
    return section_data

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
    harmonic_direction: str
    rhythmic_direction: str
    melodic_direction: str

class CompositionPlan(BaseModel):
    plan_title: str
    style: Optional[str]
    sections: List[SectionPlan]

class CompositionPlanWithMetadata(BaseModel):
    plan: CompositionPlan
    metadata: SongMetadata

class ModularPhrase(BaseModel):
    phrase_label: str
    phrase_description: str
    lyrics: Optional[str]
    bass: List[NoteDuration]
    tenor: List[NoteDuration]
    alto: List[NoteDuration]
    soprano: List[NoteDuration]
    piano: List[NoteDuration]
    percussion: Optional[List[NoteDuration]] = Field(default=None)

class ModularSection(BaseModel):
    section_label: str
    section_description: str
    harmonic_direction: str
    rhythmic_direction: str
    melodic_direction: str
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

    The MIDI file has multiple tracks:
      - Bass (track 0, channel 0)
      - Tenor (track 1, channel 1)
      - Alto (track 2, channel 2)
      - Soprano (track 3, channel 3)
      - Piano (track 4, channel 4)
      - Percussion (track 5, channel 9) if present
    """

    # Validate note durations before processing
    def validate_notes(notes: List[NoteDuration], voice_name: str) -> List[NoteDuration]:
        validated = []
        for i, nd in enumerate(notes):
            if nd.duration <= 0:
                print(f"Warning: Found {voice_name} note at position {i} with invalid duration {nd.duration}. Skipping.")
                continue
            if nd.note is not None and (nd.note < 0 or nd.note > 127):
                print(f"Warning: Found {voice_name} note at position {i} with invalid MIDI note number {nd.note}. Skipping.")
                continue
            validated.append(nd)
        return validated

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

    # Validate all notes before proceeding
    for voice_name in list(voices.keys()):
        voices[voice_name] = validate_notes(voices[voice_name], voice_name)
        if not voices[voice_name]:
            print(f"Warning: {voice_name} track has no valid notes after validation. Removing track.")
            del voices[voice_name]

    # 4) Create the MIDI file
    num_tracks = len(voices)  # Only create tracks for voices that have valid notes
    if num_tracks == 0:
        raise ValueError("No valid notes found in any voice part after validation.")
        
    midi_file = MIDIFile(num_tracks)

    # Add the tempo to each track
    for i in range(num_tracks):
        midi_file.addTempo(i, 0, piece.metadata.tempo)

    # Program changes (instrumentation)
    bass_prog = piece.metadata.instruments.bass
    tenor_prog = piece.metadata.instruments.tenor
    alto_prog = piece.metadata.instruments.alto
    soprano_prog = piece.metadata.instruments.soprano
    piano_prog = 0  # piano is always 0

    # Track to channel mapping (excluding any removed voices)
    track_info = []
    if "Bass" in voices:
        track_info.append(("Bass", 0, bass_prog))
    if "Tenor" in voices:
        track_info.append(("Tenor", 1, tenor_prog))
    if "Alto" in voices:
        track_info.append(("Alto", 2, alto_prog))
    if "Soprano" in voices:
        track_info.append(("Soprano", 3, soprano_prog))
    if "Piano" in voices:
        track_info.append(("Piano", 4, piano_prog))
    if "Percussion" in voices:
        track_info.append(("Percussion", 9, None))  # No program change for percussion

    # Add program changes for each track
    for i, (voice_name, channel, program) in enumerate(track_info):
        if program is not None:  # Skip program change for percussion
            midi_file.addProgramChange(i, channel, 0, program)

    # 5) Write out the notes for each voice
    for i, (voice_name, channel, _) in enumerate(track_info):
        time_pos = 0.0
        track_notes = voices[voice_name]

        for nd in track_notes:
            if nd.note is not None:
                try:
                    midi_file.addNote(
                        track=i,
                        channel=channel,
                        pitch=nd.note,
                        time=time_pos,
                        duration=max(0.1, nd.duration),  # Ensure minimum duration
                        volume=100
                    )
                except Exception as e:
                    print(f"Warning: Failed to add note in {voice_name} track at position {time_pos}: {e}")
            time_pos += nd.duration

    # 6) Save the MIDI file
    midi_filename = os.path.join(theme_folder, f"{base_filename}.mid")
    print(f"\nSaving MIDI file to: {midi_filename}")
    with open(midi_filename, "wb") as f_out:
        try:
            midi_file.writeFile(f_out)
            print("MIDI file saved successfully.")
        except Exception as e:
            print(f"Error saving MIDI file: {e}")
            raise

    # 7) Save the JSON log with the raw piece data
    piece_dict = piece.dict()
    log_filename = os.path.join(theme_folder, f"{base_filename}.json")
    print(f"Saving JSON log to: {log_filename}")

    piece_dict["generation_metadata"] = {
        "user_prompt": theme,
        "model_used": "modular-stepwise",
        "timestamp": date_str + " " + time_str,
        "composition_plan": plan.dict()
    }

    with open(log_filename, "w", encoding="utf-8") as f_json:
        json.dump(piece_dict, f_json, indent=2)
    print("JSON log saved successfully.")

# ------------------------------------------------------------------
# 4) Stepwise generation: plan + generate each section
# ------------------------------------------------------------------

async def plan_and_generate_modular_song(theme: str) -> None:
    """
    1) Calls BAML function to generate a CompositionPlan
    2) Iterates through the plan sections one by one:
       - For each section, calls the new BAML function GenerateOneSection
         with the previously generated sections (for context).
    3) Constructs the final piece from the incremental sections
    4) Saves the piece to MIDI + JSON
    """

    print("\n==== Step 1: Generating the composition plan... ====")
    try:
        plan_with_metadata = await async_b.GenerateCompositionPlan(theme=theme)
        print("Successfully got CompositionPlan with metadata:")
        print(json.dumps(plan_with_metadata.dict(), indent=2))
    except Exception as e:
        print(f"Error generating composition plan: {e}")
        return

    print("\n==== Step 2: Generating the final piece section-by-section... ====")

    # We'll accumulate the final sections in a list
    all_sections: List[ModularSection] = []

    # For each section in the plan, call GenerateOneSection
    for idx, plan_section in enumerate(plan_with_metadata.plan.sections):
        print(f"\n-- Generating Section #{idx+1}: {plan_section.label} --")
        try:
            # We pass along what we've generated so far for context
            previous_sections = [s.dict() for s in all_sections]  # convert to dict for BAML
            section_plan_dict = plan_section.dict()
            plan_dict = plan_with_metadata.dict()

            # Ensure section_description is set from the plan's description
            if plan_section.description:
                section_plan_dict["description"] = plan_section.description
            else:
                section_plan_dict["description"] = f"Section {plan_section.label}"

            # BAML call with streaming:
            stream = async_b.stream.GenerateOneSection(
                previousSections=previous_sections,
                nextSectionPlan=section_plan_dict,
                overallPlan=plan_dict,
                theme=theme
            )
            result = await stream.get_final_response()

            # Could come back as a dict or a JSON string. Handle both.
            if isinstance(result, str):
                result = remove_c_style_comments(result)
                # Preprocess to handle null percussion before parsing
                result_dict = json.loads(result)
                processed_result = preprocess_section_json(result_dict)
                generated_section = ModularSection.parse_obj(processed_result)
            else:
                # If it's already a dict, still preprocess it
                processed_result = preprocess_section_json(result.dict())
                generated_section = ModularSection.parse_obj(processed_result)

            # Save to all_sections
            all_sections.append(generated_section)
            print(f"  Section '{generated_section.section_label}' generated with {len(generated_section.phrases)} phrases.")
        except Exception as e:
            print(f"Error generating section: {e}")
            return

    # Create the final piece using the metadata from the plan
    try:
        # Parse the metadata from the plan
        if isinstance(plan_with_metadata.metadata, dict):
            metadata_dict = plan_with_metadata.metadata
        else:
            metadata_dict = plan_with_metadata.metadata.dict()

        # Create the SongMetadata object directly from the dictionary
        metadata = SongMetadata.parse_obj(metadata_dict)

        final_piece = ModularPiece(
            metadata=metadata,
            sections=all_sections
        )

        # Save the piece
        save_modular_piece_to_midi(final_piece, theme, plan_with_metadata.plan)
    except Exception as e:
        print(f"Error creating final piece: {e}")
        print("Raw metadata structure:", json.dumps(plan_with_metadata.metadata if isinstance(plan_with_metadata.metadata, dict) else plan_with_metadata.metadata.dict(), indent=2))
        return

# ------------------------------------------------------------------
# 5) Optional: If you run this file directly, test with a sample theme
# ------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(plan_and_generate_modular_song("Create a jazzy piece with an intro, verse, and ending"))
