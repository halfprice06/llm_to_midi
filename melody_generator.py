import argparse
import json
import os
import datetime
import asyncio
from typing import List, Optional, Tuple, Dict, Any
from midiutil import MIDIFile
from fractions import Fraction
from baml_client.async_client import b as async_b  # Import the async client
from baml_client.types import NoteDuration, Measure, Phrase, Section, Instrumentation, SongMetadata, SectionPlan, CompositionPlan, CompositionPlanWithMetadata, ModularPiece
from baml_py import ClientRegistry  # Import ClientRegistry

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
            if isinstance(phrase, dict):
                for measure in phrase.get("measures", []):
                    if isinstance(measure, dict):
                        for beat in measure.get("beats", []):
                            if isinstance(beat, dict) and "percussion" in beat and beat["percussion"] is None:
                                del beat["percussion"]
    
    return section_data

# ------------------------------------------------------------------
# 1) Helper functions to convert a ModularPiece to MIDI
# ------------------------------------------------------------------

def get_beats_per_measure(time_signature: str) -> float:
    """
    Calculate the number of beats per measure based on the time signature.
    Assumes a quarter note is one beat.
    """
    try:
        numerator, denominator = map(int, time_signature.split('/'))
        # Beats per measure = numerator * (4 / denominator)
        return numerator * (4 / denominator)
    except Exception as e:
        print(f"Error parsing time signature '{time_signature}': {e}")
        return 4.0  # Default to 4 beats per measure

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

def save_modular_piece_to_midi(piece: ModularPiece, theme: str, plan: CompositionPlan, model: Optional[str] = None) -> None:
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
    """
    # Validate note durations before processing
    def validate_notes(notes: List[Tuple[float, NoteDuration]], voice_name: str) -> List[Tuple[float, NoteDuration]]:
        validated = []
        for start, nd in notes:
            try:
                # Convert duration to float and validate
                duration_float = float(Fraction(nd.duration))
                if duration_float <= 0:
                    print(f"Warning: Found {voice_name} note at start {start} with invalid duration {nd.duration}. Skipping.")
                    continue
                if nd.note is not None and (nd.note < 0 or nd.note > 127):
                    print(f"Warning: Found {voice_name} note at start {start} with invalid MIDI note number {nd.note}. Skipping.")
                    continue
                # Ensure duration is reasonable to prevent MIDI library issues
                if duration_float > 16:  # Limit to 4 measures in 4/4 time as a safe maximum
                    print(f"Warning: Found {voice_name} note at start {start} with unusually long duration {duration_float}. Truncating to 16 beats.")
                    duration_float = 16
                validated.append((start, NoteDuration(note=nd.note, duration=str(duration_float))))
            except Exception as e:
                print(f"Warning: Error processing {voice_name} note at {start}: {e}. Skipping.")
                continue
        return validated

    # Create the output folder (timestamped + sanitized theme)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H%M%S")
    safe_theme = "".join(c for c in theme if c.isalnum() or c in (' ', '-')).strip().replace(' ', '_')
    theme_folder = os.path.join("outputs", f"{date_str} - {time_str}_{safe_theme}")
    os.makedirs(theme_folder, exist_ok=True)

    # Create a base filename from the piece metadata
    safe_title = "".join(c for c in piece.metadata.title if c.isalnum() or c in (' ', '-')).strip()
    safe_key = "".join(c for c in piece.metadata.key_signature if c.isalnum() or c in (' ', '-')).strip()
    model_str = "default" if not model else "".join(c for c in model if c.isalnum() or c in (' ', '-')).strip()
    base_filename = f"{date_str} - {model_str} - {safe_title} - {safe_key} - {piece.metadata.tempo}bpm"

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
        # Save the JSON log with the raw piece data even if MIDI fails
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
                        duration_float = float(Fraction(nd.duration))
                        # Ensure minimum duration to prevent MIDI library issues
                        midi_file.addNote(
                            track=i,
                            channel=channel,
                            pitch=nd.note,
                            time=start_time,
                            duration=max(0.1, duration_float),
                            volume=100
                        )
                        note_count += 1
                    except Exception as e:
                        print(f"Warning: Failed to add note in {voice_name} at {start_time}: {e}")
            
            # If a track has no notes, add a dummy silence note to prevent MIDI library errors
            if note_count == 0:
                print(f"Warning: No notes added to {voice_name} track. Adding a dummy silent note.")
                midi_file.addNote(
                    track=i,
                    channel=channel,
                    pitch=60,  # Middle C
                    time=0,
                    duration=0.1,
                    volume=0  # Silent
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
        
        # Try to save a simplified version with just one track as fallback
        try:
            print("Attempting to save a simplified MIDI file as fallback...")
            simple_midi = MIDIFile(1)
            simple_midi.addTempo(0, 0, piece.metadata.tempo)
            simple_midi.addProgramChange(0, 0, 0, piano_prog)
            
            # Add a few simple notes to ensure the file is valid
            for t in range(4):
                simple_midi.addNote(0, 0, 60 + t, t, 1, 100)
                
            fallback_midi_filename = os.path.join(theme_folder, f"{base_filename}_fallback.mid")
            with open(fallback_midi_filename, "wb") as f_out:
                simple_midi.writeFile(f_out)
            print(f"Fallback MIDI file saved to: {fallback_midi_filename}")
        except Exception as fallback_error:
            print(f"Fallback MIDI save also failed: {fallback_error}")

    # Save the JSON log with the raw piece data
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

# ------------------------------------------------------------------
# 2) Stepwise generation: plan + generate each section
# ------------------------------------------------------------------

async def plan_and_generate_modular_song(theme: str, model: Optional[str] = None) -> None:
    """
    Generate a modular song based on the given theme.
    
    Args:
        theme: The thematic prompt for the composition.
        model: The model/client to use for generation. If None, uses the default client.
               Examples: "OpenAIGPT4o", "AnthropicSonnet35", "AnthropicHaiku", etc.
    """
    # Set up client registry if a model is specified
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

            # Validation
            for phrase in generated_section.phrases:
                if len(phrase.measures) != plan_section.measures_per_phrase:
                    print(f"Warning: Phrase '{phrase.phrase_label}' has {len(phrase.measures)} measures, expected {plan_section.measures_per_phrase}")
                phrase_end = plan_section.measures_per_phrase * beats_per_measure
                for measure_idx, measure in enumerate(phrase.measures):
                    if len(measure.beats) != int(beats_per_measure):
                        print(f"Warning: Measure {measure.phrase_measure_number} has {len(measure.beats)} beats, expected {beats_per_measure}")
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
            all_sections.append(generated_section)
            print(f"  Section '{generated_section.section_label}' generated with {len(generated_section.phrases)} phrases.")

        except Exception as e:
            print(f"Error generating section: {e}")
            return

    # Final piece creation and saving
    try:
        metadata = SongMetadata.model_validate(plan_with_metadata.metadata.model_dump())
        print("All sections generated, aggregating piece...")
        final_piece = ModularPiece(metadata=metadata, sections=all_sections)
        print("Piece aggregated, saving to MIDI...")
        save_modular_piece_to_midi(final_piece, theme, plan_with_metadata.plan, model)
        print("MIDI saved successfully.")
    except Exception as e:
        print(f"Error creating final piece: {e}")
        import traceback
        traceback.print_exc()
        return

# ------------------------------------------------------------------
# 3) Optional: If you run this file directly, test with a sample theme
# ------------------------------------------------------------------

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
    
    # Process model arguments
    models_to_run = []
    if args.model:
        models_to_run.extend(args.model)
    if args.models:
        models_list = [m.strip() for m in args.models.split(',') if m.strip()]
        models_to_run.extend(models_list)
    
    if not models_to_run:
        # Run with default model
        asyncio.run(plan_and_generate_modular_song(theme, None))
    else:
        # Run sequentially for each model
        print(f"Running generation sequentially for {len(models_to_run)} models: {', '.join(models_to_run)}")
        for idx, model in enumerate(models_to_run):
            print(f"\n=========================================")
            print(f"MODEL {idx+1} of {len(models_to_run)}: {model}")
            print(f"=========================================\n")
            asyncio.run(plan_and_generate_modular_song(theme, model))
            if idx < len(models_to_run) - 1:
                print("\nMoving to next model...\n")