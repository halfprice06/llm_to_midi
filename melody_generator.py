import argparse
import json
import os
import datetime
import asyncio
import re
from typing import List, Optional, Tuple, Dict, Any
from midiutil import MIDIFile
from fractions import Fraction
from baml_client.async_client import b as async_b  # Import the async client
from baml_client.types import NoteDuration, Section, SongMetadata, CompositionPlan, ModularPiece, Beat
from baml_py import ClientRegistry  # Import ClientRegistry

# Import the new service
try:
    from sheet_music_generator import convert_midi_to_musicxml, convert_musicxml_to_image
except ImportError:
    print("Warning: sheet_music_generator.py not found. Sheet music image generation will be unavailable.")
    convert_midi_to_musicxml = None
    convert_musicxml_to_image = None

print("Initializing melody generator...")

# New function to convert note names to MIDI numbers
def note_name_to_midi(note_name: str) -> int:
    """
    Convert a musical note name (e.g., 'C4', 'A#5', 'Bb3') to its MIDI note number.
    
    Args:
        note_name: The note name as a string.
    
    Returns:
        The corresponding MIDI note number (0-127).
    
    Raises:
        ValueError: If the note name is invalid or out of MIDI range.
    """
    match = re.match(r'([A-Ga-g])(#|b)?(\d+)', note_name)
    if not match:
        raise ValueError(f"Invalid note name: {note_name}")
    letter, accidental, octave_str = match.groups()
    letter = letter.upper()
    octave = int(octave_str)
    base_offset = {
        'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
    }[letter]
    if accidental == '#':
        offset = base_offset + 1
    elif accidental == 'b':
        offset = base_offset - 1
    else:
        offset = base_offset
    midi_number = 12 * (octave + 1) + offset
    if not 0 <= midi_number <= 127:
        raise ValueError(f"MIDI number {midi_number} out of range for note {note_name}")
    return midi_number

def preprocess_section_json(section_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocesses the section data to handle null percussion values before validation.
    If percussion is null, removes it from the phrase entirely.
    """
    if not isinstance(section_data, dict):
        return section_data
        
    if "phrases" in section_data and isinstance(section_data["phrases"], list):
        for phrase in section_data["phrases"]:
            if isinstance(phrase, dict):
                for measure in phrase.get("measures", []):
                    if isinstance(measure, dict):
                        for beat in measure.get("beats", []):
                            if isinstance(beat, dict) and "percussion" in beat and beat["percussion"] is None:
                                del beat["percussion"]
    
    return section_data

def fix_incomplete_measures(piece: ModularPiece) -> ModularPiece:
    """
    Fixes incomplete measures by adding missing beats with rests.
    This ensures MIDI generation doesn't fail due to missing beats.
    Also adds missing measures if needed.
    
    Args:
        piece: The ModularPiece to fix
    
    Returns:
        The fixed ModularPiece
    """
    beats_per_measure = get_beats_per_measure(piece.metadata.time_signature)
    print(f"\nFixing incomplete measures (expected {beats_per_measure} beats per measure)...")
    
    measures_fixed = 0
    beats_added = 0
    measures_added = 0
    
    # Create an empty beat template with empty lists for each voice
    def create_empty_beat(beat_number: int, harmony: str = "No harmony (auto-added beat)"):
        return Beat(
            harmony_description=harmony,
            beat_counter=f"Beat {beat_number} of {int(beats_per_measure)}",
            bass=[],
            tenor=[],
            alto=[],
            soprano=[],
            piano=[],
            percussion=None  # Start with no percussion by default
        )
    
    # Process each section
    for section_idx, section in enumerate(piece.sections):
        for phrase_idx, phrase in enumerate(section.phrases):
            # Check if phrase description mentions expected measure count
            expected_measure_count = None
            phrase_description = getattr(phrase, 'phrase_description', '')
            measure_counter_regex = r'Measure \d+ of (\d+)'
            
            # Find all measure counters and extract the total expected measures
            for measure in phrase.measures:
                measure_counter = getattr(measure, 'measure_counter', '')
                match = re.search(measure_counter_regex, measure_counter)
                if match:
                    expected_measure_count = int(match.group(1))
                    break
            
            if expected_measure_count is None:
                # Default to the number of measures we have
                expected_measure_count = len(phrase.measures)
                print(f"  No measure count found in section {section_idx+1}, phrase {phrase_idx+1}. Using current count: {expected_measure_count}")
            
            # Fix incomplete measures first
            for measure_idx, measure in enumerate(phrase.measures):
                expected_beats = int(beats_per_measure)
                actual_beats = len(measure.beats)
                
                if actual_beats < expected_beats:
                    measures_fixed += 1
                    current_beats = actual_beats
                    
                    # Check if the last beat has a proper counter, fix it if not
                    if actual_beats > 0 and hasattr(measure.beats[-1], 'beat_counter'):
                        last_beat_counter = measure.beats[-1].beat_counter
                        if not last_beat_counter or last_beat_counter.endswith("of "):
                            measure.beats[-1].beat_counter = f"Beat {actual_beats} of {expected_beats}"
                            print(f"  Fixed incomplete beat counter in section {section_idx+1}, phrase {phrase_idx+1}, measure {measure_idx+1}")
                    
                    # Add missing beats
                    for i in range(current_beats, expected_beats):
                        beats_added += 1
                        new_beat = create_empty_beat(i+1)
                        
                        # If any previous beat had percussion, add empty percussion to the new beat
                        has_percussion = False
                        for beat in measure.beats:
                            if hasattr(beat, 'percussion') and beat.percussion is not None:
                                has_percussion = True
                                break
                        
                        if has_percussion:
                            new_beat.percussion = []
                            
                        measure.beats.append(new_beat)
                    
                    print(f"  Added {expected_beats - actual_beats} missing beats to section {section_idx+1}, " 
                          f"phrase {phrase_idx+1}, measure {measure_idx+1} (was {actual_beats}, now {len(measure.beats)})")
            
            # Now add missing measures if needed
            actual_measure_count = len(phrase.measures)
            if actual_measure_count < expected_measure_count:
                measures_added += (expected_measure_count - actual_measure_count)
                print(f"  Adding {expected_measure_count - actual_measure_count} missing measures to section {section_idx+1}, phrase {phrase_idx+1}")
                
                # Get the last measure for reference
                last_measure = phrase.measures[-1] if phrase.measures else None
                
                # Create template for each missing measure
                for i in range(actual_measure_count, expected_measure_count):
                    # Create empty beats for this measure
                    new_beats = []
                    for j in range(int(beats_per_measure)):
                        new_beat = create_empty_beat(j+1, "Added harmony (auto-added measure)")
                        new_beats.append(new_beat)
                    
                    # Create the new measure object
                    from pydantic import BaseModel
                    class MeasureModel(BaseModel):
                        measure_counter: str
                        harmony_plan_for_this_measure: str
                        beats: list
                    
                    new_measure = MeasureModel(
                        measure_counter=f"Measure {i+1} of {expected_measure_count}",
                        harmony_plan_for_this_measure="Auto-added measure for continuity",
                        beats=new_beats
                    )
                    
                    # Add it to the phrase
                    phrase.measures.append(new_measure)
    
    if measures_fixed > 0 or measures_added > 0:
        print(f"Fixed {measures_fixed} incomplete measures by adding {beats_added} missing beats.")
        print(f"Added {measures_added} missing measures.")
    else:
        print("No incomplete measures found.")
        
    return piece

def ensure_voice_continuity(piece: ModularPiece) -> ModularPiece:
    """
    Ensures all voices that appear in a piece maintain continuity.
    If a voice appears in one beat but not in another, add an empty list for that voice.
    
    Args:
        piece: The ModularPiece to fix
    
    Returns:
        The fixed ModularPiece with consistent voice structure
    """
    print("\nEnsuring voice continuity across beats...")
    
    voice_names = ["bass", "tenor", "alto", "soprano", "piano", "percussion"]
    voices_present = {voice: False for voice in voice_names}
    fixes_applied = 0
    
    # First, identify which voices are present anywhere in the piece
    for section in piece.sections:
        for phrase in section.phrases:
            for measure in phrase.measures:
                for beat in measure.beats:
                    for voice in voice_names:
                        if hasattr(beat, voice) and getattr(beat, voice) is not None:
                            if voice == "percussion":
                                # Special handling for percussion which might be None
                                if getattr(beat, voice) is not None:
                                    voices_present[voice] = True
                            else:
                                voices_present[voice] = True
    
    # Now ensure all beats have all the voices that are present in the piece
    for section in piece.sections:
        for phrase in section.phrases:
            for measure in phrase.measures:
                for beat in measure.beats:
                    for voice in voice_names:
                        if voices_present[voice] and (not hasattr(beat, voice) or getattr(beat, voice) is None):
                            if voice == "percussion":
                                setattr(beat, voice, [])
                            else:
                                setattr(beat, voice, [])
                            fixes_applied += 1
    
    if fixes_applied > 0:
        print(f"Added {fixes_applied} missing voice placeholders to ensure continuity")
    else:
        print("No voice continuity issues found")
    
    return piece

# Helper functions to convert a ModularPiece to MIDI

def get_beats_per_measure(time_signature: str) -> float:
    """
    Calculate the number of beats per measure based on the time signature.
    Assumes a quarter note is one beat.
    """
    try:
        numerator, denominator = map(int, time_signature.split('/'))
        return numerator * (4 / denominator)
    except Exception as e:
        print(f"Error parsing time signature '{time_signature}': {e}")
        return 4.0  # Default to 4 beats per measure

def remove_c_style_comments(json_str: str) -> str:
    """
    Removes C-style comments (/* ... */) from a JSON string.
    """
    import re
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    return json_str

def aggregate_modular_piece(piece: ModularPiece) -> Dict[str, List[Tuple[float, NoteDuration]]]:
    """
    Aggregates all notes in the ModularPiece into a dictionary where each voice
    maps to a list of (start_time, NoteDuration) tuples.
    """
    aggregated = {
        "Bass": [],
        "Tenor": [],
        "Alto": [],
        "Soprano": [],
        "Piano": [],
        "Percussion": []
    }
    beats_per_measure = get_beats_per_measure(piece.metadata.time_signature)
    current_time = 0.0

    for section in piece.sections:
        for phrase in section.phrases:
            for measure in phrase.measures:
                for beat_idx, beat in enumerate(measure.beats):
                    beat_start = current_time + beat_idx
                    for voice_name in ["bass", "tenor", "alto", "soprano", "piano"]:
                        notes = getattr(beat, voice_name)
                        for note in notes:
                            aggregated[voice_name.capitalize()].append((beat_start, note))
                    if hasattr(beat, 'percussion') and beat.percussion:
                        for note in beat.percussion:
                            aggregated["Percussion"].append((beat_start, note))
                current_time += beats_per_measure

    if not aggregated["Percussion"]:
        del aggregated["Percussion"]
    return aggregated

def validate_notes(notes: List[Tuple[float, NoteDuration]], voice_name: str) -> List[Tuple[float, NoteDuration]]:
    """
    Validates notes by checking if they can be converted to valid MIDI numbers and have valid durations.
    
    Args:
        notes: List of (start_time, NoteDuration) tuples.
        voice_name: The name of the voice (e.g., 'Bass', 'Percussion').
    
    Returns:
        List of validated (start_time, NoteDuration) tuples.
    """
    validated = []
    for start, nd in notes:
        try:
            if nd.note is None:
                # Rest, keep as is
                validated.append((start, nd))
                continue
            if voice_name != "Percussion":
                _ = note_name_to_midi(nd.note)  # Check if convertible
            else:
                midi_note = int(nd.note)
                if not 0 <= midi_note <= 127:
                    print(f"Warning: Percussion note {midi_note} out of range at {start}. Skipping.")
                    continue
            
            # Handle duration validation
            try:
                duration_float = float(Fraction(nd.duration))
                
                # Check for unreasonably long durations that span multiple measures
                if duration_float > 16:
                    print(f"Warning: Unusually long duration {duration_float} for {voice_name} at {start}. Truncating to 4 beats.")
                    nd.duration = '4'  # Truncate to a whole note (4 beats)
                    duration_float = 4.0
                
                # Check for durations of 0 or negative
                if duration_float <= 0:
                    print(f"Warning: Invalid duration {nd.duration} for {voice_name} at {start}. Skipping.")
                    continue
                
                validated.append((start, nd))
            except ValueError:
                print(f"Warning: Cannot convert duration '{nd.duration}' to a number for {voice_name} at {start}. Using default of 1 beat.")
                nd.duration = '1'
                validated.append((start, nd))
                
        except ValueError as e:
            print(f"Warning: Invalid note '{nd.note}' for {voice_name} at {start}: {e}. Skipping.")
        except Exception as e:
            print(f"Warning: Error processing {voice_name} note at {start}: {e}. Skipping.")
    return validated

def fix_long_notes(piece: ModularPiece) -> ModularPiece:
    """
    Fixes notes with durations that span multiple beats by splitting them into
    separate notes tied across beats.
    
    Args:
        piece: The ModularPiece to fix
        
    Returns:
        The fixed ModularPiece
    """
    print("\nChecking for notes with durations spanning multiple beats...")
    
    beats_per_measure = get_beats_per_measure(piece.metadata.time_signature)
    notes_fixed = 0
    
    for section in piece.sections:
        for phrase in section.phrases:
            for measure in phrase.measures:
                for beat_idx, beat in enumerate(measure.beats):
                    for voice_name in ["bass", "tenor", "alto", "soprano", "piano"]:
                        if not hasattr(beat, voice_name):
                            continue
                            
                        voice = getattr(beat, voice_name)
                        if not voice:
                            continue
                            
                        fixed_notes = []
                        for note in voice:
                            try:
                                duration_float = float(Fraction(note.duration))
                                remaining_beats = len(measure.beats) - beat_idx
                                
                                if duration_float <= 1 or duration_float <= remaining_beats:
                                    fixed_notes.append(note)
                                    continue
                                
                                # Split the note - keep the first beat in this position
                                print(f"  Splitting {note.note} with duration {duration_float} across multiple beats")
                                fixed_notes.append({"note": note.note, "duration": "1"})
                                notes_fixed += 1
                                
                                # Add trailing parts of the note to subsequent beats
                                remaining_duration = duration_float - 1
                                current_beat_idx = beat_idx + 1
                                
                                while remaining_duration > 0 and current_beat_idx < len(measure.beats):
                                    current_beat = measure.beats[current_beat_idx]
                                    if not hasattr(current_beat, voice_name):
                                        setattr(current_beat, voice_name, [])
                                    
                                    current_voice = getattr(current_beat, voice_name)
                                    duration_for_this_beat = min(1, remaining_duration)
                                    
                                    # Add continuation note to the next beat
                                    current_voice.append({
                                        "note": note.note,
                                        "duration": str(duration_for_this_beat)
                                    })
                                    
                                    remaining_duration -= duration_for_this_beat
                                    current_beat_idx += 1
                            except ValueError:
                                # If we can't parse the duration, just keep the note as is
                                fixed_notes.append(note)
                            except Exception as e:
                                print(f"  Error fixing note duration: {e}")
                                fixed_notes.append(note)
                                
                        # Replace with the fixed notes
                        setattr(beat, voice_name, fixed_notes)
    
    if notes_fixed > 0:
        print(f"Fixed {notes_fixed} notes with durations spanning multiple beats")
    else:
        print("No notes with problematic durations found")
        
    return piece

def fill_empty_final_measure(piece: ModularPiece) -> ModularPiece:
    """
    Check if the final measure is mostly empty and fill it with appropriate notes
    to ensure the piece has a proper conclusion.
    
    Args:
        piece: The ModularPiece to fix
        
    Returns:
        The fixed ModularPiece
    """
    print("\nChecking for empty final measures...")
    
    measures_fixed = 0
    notes_added = 0
    
    for section in piece.sections:
        for phrase in section.phrases:
            if not phrase.measures:
                continue
                
            # Get the final measure
            final_measure = phrase.measures[-1]
            
            # Count how many beats have notes
            beats_with_notes = 0
            total_notes = 0
            
            for beat in final_measure.beats:
                beat_has_notes = False
                for voice_name in ["bass", "tenor", "alto", "soprano", "piano"]:
                    if hasattr(beat, voice_name) and getattr(beat, voice_name):
                        beat_has_notes = True
                        total_notes += len(getattr(beat, voice_name))
                
                if beat_has_notes:
                    beats_with_notes += 1
            
            # If fewer than 2 beats have notes or fewer than 4 total notes, consider it sparse
            if beats_with_notes < 2 or total_notes < 4:
                print(f"  Found sparse final measure with only {beats_with_notes} beats containing notes " 
                      f"and {total_notes} total notes. Adding closure notes.")
                
                # Look for the key signature to determine the tonic note
                key_sig = piece.metadata.key_signature if hasattr(piece.metadata, 'key_signature') else "C Major"
                
                # Extract the tonic note
                tonic = key_sig.split()[0] if len(key_sig.split()) > 0 else "C"
                
                # Add appropriate notes to empty beats
                for beat_idx, beat in enumerate(final_measure.beats):
                    # Check if this beat is already populated
                    beat_populated = False
                    for voice_name in ["bass", "tenor", "alto", "soprano", "piano"]:
                        if hasattr(beat, voice_name) and getattr(beat, voice_name):
                            beat_populated = True
                            break
                    
                    if not beat_populated:
                        # Add basic tonic chord
                        if not hasattr(beat, "bass") or not beat.bass:
                            beat.bass = [{"note": f"{tonic}3", "duration": "1"}]
                            notes_added += 1
                            
                        if not hasattr(beat, "tenor") or not beat.tenor:
                            # Add third of the chord for tenor (major third)
                            third_note = {
                                "C": "E3", "G": "B3", "D": "F#3", "A": "C#4", "E": "G#3", "B": "D#4", "F": "A3",
                                "F#": "A#3", "Bb": "D4", "Eb": "G3", "Ab": "C4", "Db": "F4", "Gb": "Bb3"
                            }.get(tonic, "E3")
                            beat.tenor = [{"note": third_note, "duration": "1"}]
                            notes_added += 1
                            
                        if not hasattr(beat, "alto") or not beat.alto:
                            # Add fifth of the chord for alto
                            fifth_note = {
                                "C": "G3", "G": "D4", "D": "A3", "A": "E4", "E": "B3", "B": "F#4", "F": "C4",
                                "F#": "C#4", "Bb": "F4", "Eb": "Bb3", "Ab": "Eb4", "Db": "Ab3", "Gb": "Db4"
                            }.get(tonic, "G3")
                            beat.alto = [{"note": fifth_note, "duration": "1"}]
                            notes_added += 1
                            
                        if not hasattr(beat, "soprano") or not beat.soprano:
                            # Add tonic for soprano, one octave higher
                            beat.soprano = [{"note": f"{tonic}4", "duration": "1"}]
                            notes_added += 1
                            
                        if not hasattr(beat, "piano") or not beat.piano:
                            # Add a piano chord
                            beat.piano = [
                                {"note": f"{tonic}2", "duration": "1/4"},
                                {"note": f"{tonic}3", "duration": "1/4"},
                                {"note": fifth_note, "duration": "1/4"},
                                {"note": f"{tonic}4", "duration": "1/4"}
                            ]
                            notes_added += 4
                
                measures_fixed += 1
    
    if measures_fixed > 0:
        print(f"Fixed {measures_fixed} sparse final measures by adding {notes_added} notes for proper closure")
    else:
        print("No sparse final measures found")
    
    return piece

def save_modular_piece_to_midi(piece: ModularPiece, theme: str, plan: CompositionPlan, model: Optional[str] = None, generate_images: bool = False) -> None:
    """
    Saves the ModularPiece to a MIDI file and a JSON log file in a timestamped folder.
    
    MIDI Tracks:
      - Bass (track 0, channel 0)
      - Tenor (track 1, channel 1)
      - Alto (track 2, channel 2)
      - Soprano (track 3, channel 3)
      - Piano (track 4, channel 4)
      - Percussion (track 5, channel 9) if present
    
    Args:
        piece: The ModularPiece to save
        theme: The theme used to generate the piece
        plan: The composition plan
        model: The model used for generation (optional)
        generate_images: Whether to generate sheet music images (default: False)
    """
    # Create the output folder
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H%M%S")
    safe_theme = "".join(c for c in theme if c.isalnum() or c in (' ', '-')).strip().replace(' ', '_')
    model_str = "default" if not model else "".join(c for c in model if c.isalnum() or c in (' ', '-')).strip()
    theme_folder = os.path.join("outputs", f"{date_str} - {time_str} - {model_str} - {safe_theme}")
    os.makedirs(theme_folder, exist_ok=True)

    # Create a base filename
    safe_title = "".join(c for c in piece.metadata.title if c.isalnum() or c in (' ', '-')).strip()
    safe_key = "".join(c for c in piece.metadata.key_signature if c.isalnum() or c in (' ', '-')).strip()
    base_filename = f"{date_str} - {model_str} - {safe_title} - {safe_key} - {piece.metadata.tempo}bpm"

    # Apply more aggressive fixes for AnthropicSonnet37 issues
    try:
        # First add any missing measures and ensure voice continuity (existing fixes)
        piece = fix_incomplete_measures(piece)
        piece = ensure_voice_continuity(piece)
        
        # Add new fixes for AnthropicSonnet37 specific issues
        if model and "AnthropicSonnet37" in model:
            print("Applying additional fixes specific to AnthropicSonnet37 output...")
            piece = fix_long_notes(piece)
            piece = fill_empty_final_measure(piece)
        else:
            # Still apply these fixes, but they're especially important for AnthropicSonnet37
            piece = fix_long_notes(piece)
            piece = fill_empty_final_measure(piece)
            
    except Exception as fix_error:
        print(f"Warning: Error during structure fixing: {fix_error}")
        print("Continuing with original piece structure...")
        import traceback
        traceback.print_exc()

    # Aggregate all notes with start times
    voices = aggregate_modular_piece(piece)

    # Validate all notes before proceeding
    for voice_name in list(voices.keys()):
        voices[voice_name] = validate_notes(voices[voice_name], voice_name)
        if not voices[voice_name]:
            print(f"Warning: {voice_name} track has no valid notes after validation. Removing track.")
            del voices[voice_name]

    if not voices:
        print("Warning: No valid notes found in any voice part after validation. Saving empty JSON log.")
        piece_dict = piece.model_dump()
        log_filename = os.path.join(theme_folder, f"{base_filename}_error.json")
        piece_dict["generation_metadata"] = {
            "user_prompt": theme,
            "model_used": model or "default",
            "timestamp": date_str + " " + time_str,
            "composition_plan": plan.model_dump(),
            "error": "No valid notes found in any voice part after validation."
        }
        with open(log_filename, "w", encoding="utf-8") as f_json:
            json.dump(piece_dict, f_json, indent=2)
        print(f"JSON log saved to: {log_filename}")
        return

    # Create the MIDI file
    num_tracks = len(voices)
    midi_file = MIDIFile(num_tracks)

    # Add the tempo to each track
    for i in range(num_tracks):
        midi_file.addTempo(i, 0, piece.metadata.tempo)

    # Program changes (instrumentation)
    bass_prog = piece.metadata.instruments.bass
    tenor_prog = piece.metadata.instruments.tenor
    alto_prog = piece.metadata.instruments.alto
    soprano_prog = piece.metadata.instruments.soprano
    piano_prog = 0  # Piano is always 0

    # Track to channel mapping
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

    # Write out the notes for each voice
    try:
        for i, (voice_name, channel, _) in enumerate(track_info):
            note_count = 0
            for start_time, nd in voices[voice_name]:
                if nd.note is not None:
                    try:
                        if voice_name != "Percussion":
                            midi_note = note_name_to_midi(nd.note)
                        else:
                            midi_note = int(nd.note)
                        duration_float = float(Fraction(nd.duration))
                        midi_file.addNote(
                            track=i,
                            channel=channel,
                            pitch=midi_note,
                            time=start_time,
                            duration=max(0.1, duration_float),
                            volume=100
                        )
                        note_count += 1
                    except ValueError as e:
                        print(f"Warning: Invalid note '{nd.note}' for {voice_name} at {start_time}: {e}. Skipping.")
                    except Exception as e:
                        print(f"Warning: Failed to add note in {voice_name} at {start_time}: {e}")
            
            if note_count == 0:
                print(f"Warning: No notes added to {voice_name} track. Adding a dummy silent note.")
                midi_file.addNote(
                    track=i,
                    channel=channel,
                    pitch=60,
                    time=0,
                    duration=0.1,
                    volume=0
                )
    except Exception as e:
        print(f"Error preparing MIDI notes: {e}")
        import traceback
        traceback.print_exc()

    # Save the MIDI file
    midi_filename = os.path.join(theme_folder, f"{base_filename}.mid")
    print(f"\nSaving MIDI file to: {midi_filename}")
    
    try:
        with open(midi_filename, "wb") as f_out:
            midi_file.writeFile(f_out)
        print("MIDI file saved successfully.")
    except Exception as e:
        print(f"Error saving MIDI file: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            print("Attempting to save a simplified MIDI file as fallback...")
            # Try to extract at least some notes from the original data
            simple_midi = MIDIFile(1)
            simple_midi.addTempo(0, 0, piece.metadata.tempo)
            simple_midi.addProgramChange(0, 0, 0, piano_prog)
            
            # Try to salvage some notes from the original piece
            notes_added = 0
            for voice_name in voices:
                for start_time, nd in voices[voice_name][:20]:  # Limit to first 20 notes
                    if nd.note is not None:
                        try:
                            if voice_name != "Percussion":
                                midi_note = note_name_to_midi(nd.note)
                            else:
                                midi_note = int(nd.note)
                            duration_float = float(Fraction(nd.duration))
                            simple_midi.addNote(0, 0, midi_note, start_time, max(0.1, duration_float), 100)
                            notes_added += 1
                        except Exception:
                            continue  # Skip problematic notes
            
            # If no notes could be salvaged, add some default ones
            if notes_added == 0:
                for t in range(4):
                    simple_midi.addNote(0, 0, 60 + t, t, 1, 100)
                    
            fallback_midi_filename = os.path.join(theme_folder, f"{base_filename}_fallback.mid")
            with open(fallback_midi_filename, "wb") as f_out:
                simple_midi.writeFile(f_out)
            print(f"Fallback MIDI file saved to: {fallback_midi_filename}")
        except Exception as fallback_error:
            print(f"Fallback MIDI save also failed: {fallback_error}")

    # Generate sheet music images if requested
    if generate_images and convert_midi_to_musicxml and convert_musicxml_to_image:
        try:
            print(f"\nGenerating sheet music images for: {midi_filename}")
            xml_path = convert_midi_to_musicxml(midi_filename)
            image_files = convert_musicxml_to_image(xml_path)
            if image_files:
                print(f"Generated sheet music images: {', '.join(image_files)}")
            else:
                print("No sheet music images were generated.")
        except Exception as e:
            print(f"Error generating sheet music images: {e}")
    elif generate_images:
        print("Sheet music generation skipped: Required modules not available.")
    
    # Save the JSON log
    piece_dict = piece.model_dump()
    log_filename = os.path.join(theme_folder, f"{base_filename}.json")
    print(f"Saving JSON log to: {log_filename}")

    piece_dict["generation_metadata"] = {
        "user_prompt": theme,
        "model_used": model or "default",
        "timestamp": date_str + " " + time_str,
        "composition_plan": plan.model_dump()
    }

    with open(log_filename, "w", encoding="utf-8") as f_json:
        json.dump(piece_dict, f_json, indent=2)
    print("JSON log saved successfully.")

async def plan_and_generate_modular_song(theme: str, model: Optional[str] = None, generate_images: bool = False) -> None:
    """
    Generate a modular song based on the given theme.
    
    Args:
        theme: The thematic prompt for the composition.
        model: The model/client to use for generation. If None, uses the default client.
        generate_images: Whether to generate sheet music images (default: False)
    """
    client_registry = None
    if model:
        client_registry = ClientRegistry()
        client_registry.set_primary(model)
        print(f"Using model: {model}")
    
    print("\n==== Step 1: Generating the composition plan... ====")
    baml_options = {"client_registry": client_registry} if client_registry else {}
    plan_with_metadata = await async_b.GenerateCompositionPlan(theme=theme, baml_options=baml_options)
    print("Successfully got CompositionPlan with metadata:")
    print(json.dumps(plan_with_metadata.model_dump(), indent=2))

    print("\n==== Step 2: Generating the final piece section-by-section... ====")
    all_sections: List[Section] = []
    beats_per_measure = get_beats_per_measure(plan_with_metadata.metadata.time_signature)

    for idx, plan_section in enumerate(plan_with_metadata.plan.sections):
        try:
            print(f"\n-- Generating Section #{idx+1}: {plan_section.label} --")
            previous_sections = [s.model_dump() for s in all_sections]
            section_plan_dict = plan_section.model_dump()
            plan_dict = plan_with_metadata.model_dump()
            section_plan_dict["description"] = plan_section.description or f"Section {plan_section.label}"
            total_duration_per_phrase = plan_section.measures_per_phrase * beats_per_measure

            stream = async_b.stream.GenerateOneSection(
                previousSections=previous_sections,
                nextSectionPlan=section_plan_dict,
                overallPlan=plan_dict,
                theme=theme,
                total_duration_per_phrase=total_duration_per_phrase,
                beats_per_measure=beats_per_measure,
                baml_options=baml_options
            )

            result = await stream.get_final_response()
            if isinstance(result, str):
                result = remove_c_style_comments(result)
                result_dict = json.loads(result)
                processed_result = preprocess_section_json(result_dict)
                generated_section = Section.model_validate(processed_result)
            elif hasattr(result, 'model_dump'):
                processed_result = preprocess_section_json(result.model_dump())
                generated_section = Section.model_validate(processed_result)
            else:
                raise TypeError(f"Unexpected result type: {type(result)}")

            # Validation (but don't throw errors, just print warnings)
            for phrase in generated_section.phrases:
                if len(phrase.measures) != plan_section.measures_per_phrase:
                    print(f"Warning: Phrase '{phrase.phrase_label}' has {len(phrase.measures)} measures, expected {plan_section.measures_per_phrase}")
                    
                    # We'll continue processing with the actual measures we have rather than expecting the planned amount
                    # This is a workaround to prevent crashes when the model doesn't generate the exact number

                phrase_end = plan_section.measures_per_phrase * beats_per_measure
                for measure_idx, measure in enumerate(phrase.measures):
                    try:
                        if len(measure.beats) != int(beats_per_measure):
                            print(f"Warning: Measure {measure.measure_counter} has {len(measure.beats)} beats, expected {beats_per_measure}")
                        measure_start = measure_idx * beats_per_measure
                        for beat_idx, beat in enumerate(measure.beats):
                            beat_start = measure_start + beat_idx
                            for voice_name in ["bass", "tenor", "alto", "soprano", "piano"]:
                                for nd in getattr(beat, voice_name):
                                    end_time = beat_start + float(Fraction(nd.duration))
                                    if end_time > phrase_end:
                                        print(f"Warning: Note in {voice_name} at beat {beat_idx} of measure {measure_idx + 1} extends beyond phrase end ({end_time} > {phrase_end})")
                            if hasattr(beat, 'percussion') and beat.percussion:
                                for nd in beat.percussion:
                                    end_time = beat_start + float(Fraction(nd.duration))
                                    if end_time > phrase_end:
                                        print(f"Warning: Percussion note at beat {beat_idx} of measure {measure_idx + 1} extends beyond phrase end ({end_time} > {phrase_end})")
                    except AttributeError as attr_err:
                        print(f"Warning: Attribute error in measure: {attr_err}. Continuing with processing.")
                    except Exception as ex:
                        print(f"Warning: Error validating measure: {ex}. Continuing with processing.")
            all_sections.append(generated_section)
            print(f"  Section '{generated_section.section_label}' generated with {len(generated_section.phrases)} phrases.")

        except Exception as e:
            print(f"Error generating section: {e}")
            import traceback
            traceback.print_exc()
            return

    try:
        metadata = SongMetadata.model_validate(plan_with_metadata.metadata.model_dump())
        print("All sections generated, aggregating piece...")
        final_piece = ModularPiece(metadata=metadata, sections=all_sections)
        print("Piece aggregated, saving to MIDI...")
        
        save_modular_piece_to_midi(final_piece, theme, plan_with_metadata.plan, model, generate_images=generate_images)
        print("MIDI saved successfully.")
    except Exception as e:
        print(f"Error creating final piece: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate music based on a theme.")
    parser.add_argument("--theme", type=str, default="Create a jazzy piece with an intro, verse, and ending",
                        help="Theme for the composition")
    parser.add_argument("--model", type=str, action="append",
                        help="Model to use (can specify multiple times)")
    parser.add_argument("--models", type=str,
                        help="Comma-separated list of models to run sequentially")
    args = parser.parse_args()
    
    theme = args.theme
    
    models_to_run = []
    if args.model:
        models_to_run.extend(args.model)
    if args.models:
        models_list = [m.strip() for m in args.models.split(',') if m.strip()]
        models_to_run.extend(models_list)
    
    if not models_to_run:
        asyncio.run(plan_and_generate_modular_song(theme, None))
    else:
        print(f"Running generation sequentially for {len(models_to_run)} models: {', '.join(models_to_run)}")
        for idx, model in enumerate(models_to_run):
            print(f"\n=========================================")
            print(f"MODEL {idx+1} of {len(models_to_run)}: {model}")
            print(f"=========================================\n")
            asyncio.run(plan_and_generate_modular_song(theme, model))
            if idx < len(models_to_run) - 1:
                print("\nMoving to next model...\n")