#!/usr/bin/env python3

"""
Procedurally Generated MIDI Melody Player (Rounded Binary Edition, 5-Voice Version)

- Two modes of operation:
  1) **Generation Mode**: On user input, calls the OpenAI-based generate_melodies() to get a musical piece
     in rounded binary form (A, B, A') with up to 5 separate voices (bass, tenor, alto, soprano, piano).
     The user can provide custom instructions (e.g., "make a waltz in A minor").
  2) **Playback-from-JSON Mode**: Reads a local .json file that matches the RoundedBinaryPiece schema,
     parses it, and then plays it back.

- Playback pattern for generated pieces:
    - Section A (all subsections, in order), then repeats,
    - Section B (all subsections), then repeats,
    - Section A' (all subsections), then repeats.
  All are concatenated into one timeline for real-time playback, so all voices (tracks) sound
  simultaneously (true polyphonic playback).
- Saves generated pieces as a multi-track MIDI file into the "outputs/" folder, and also saves a
  JSON log file capturing the raw schema data from the LLM.

Requires:
    pip install pygame openai pydantic MIDIUtil
"""

print("Starting 5-voice Procedurally Generated MIDI Melody Player...")

import pygame
import pygame.midi
import time
import sys
import datetime
import os
import json
from midiutil import MIDIFile
import argparse

print("Importing required modules...")

# Import the custom function and classes for generating the piece
from melody_generator import (
    generate_melodies,
    RoundedBinaryPiece,
    Section,
    Phrase,
    NoteDuration
)

print("Successfully imported melody generator with 5-voice + instrumentation support.")

# ------------------------------------------------------------------
# Utility: Note name helper for printing
# ------------------------------------------------------------------

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_name(midi_note):
    """
    Convert a MIDI note number to a string (e.g., 60 -> 'C4').
    MIDI note 60 is middle C.
    """
    if midi_note is None:
        return "Rest"
    octave = (midi_note // 12) - 1
    note_index = midi_note % 12
    return f"{NOTE_NAMES[note_index]}{octave}"

# ------------------------------------------------------------------
# Fix/Utility: Clamp & Quantize
# ------------------------------------------------------------------

def clamp_and_quantize(piece: RoundedBinaryPiece, step=0.25):
    """
    Clamps all MIDI pitches to the valid range (0..127), turning out-of-range pitches into rests.
    Quantizes all durations to the nearest 'step' in beats (default 0.25 = 16th-note grid).
    """
    def process_line(notes: list):
        for nd in notes:
            if nd.note is not None:
                if nd.note < 0 or nd.note > 127:
                    nd.note = None
            # Quantize duration
            nd.duration = round(nd.duration / step) * step
            if nd.duration < step:
                nd.duration = step

    for section_list in [piece.form.sectionA, piece.form.sectionB, piece.form.sectionA_prime]:
        for sec in section_list:
            for phr in sec.phrases:
                process_line(phr.bass)
                process_line(phr.tenor)
                process_line(phr.alto)
                process_line(phr.soprano)
                process_line(phr.piano)

# ------------------------------------------------------------------
# Build a single timeline of note-on/note-off events for true concurrent playback
# ------------------------------------------------------------------

def build_timeline_for_section(voices_dict, bpm, start_time_sec=0.0, channel_base=0):
    """
    Given a dict of voices {voice_name: [NoteDuration, ...]}, build a list of events:
        (event_time_sec, "on"/"off", note_number, channel)

    'channel_base' is typically 0, so the channels for each voice
    become (0,1,2,3,4). The order is Bass, Tenor, Alto, Soprano, Piano.
    """
    beat_duration_sec = 60.0 / bpm
    events = []

    voice_order = ["Bass", "Tenor", "Alto", "Soprano", "Piano"]
    for voice_index, voice_name in enumerate(voice_order):
        track_data = voices_dict.get(voice_name, [])
        channel = channel_base + voice_index  # each voice on a separate channel
        current_time_sec = start_time_sec
        for note_obj in track_data:
            duration_sec = note_obj.duration * beat_duration_sec
            if note_obj.note is not None:
                events.append((current_time_sec, "on", note_obj.note, channel))
                events.append((current_time_sec + duration_sec, "off", note_obj.note, channel))
            current_time_sec += duration_sec

    return events

# ------------------------------------------------------------------
# Real-time concurrent playback of a timeline of events
# ------------------------------------------------------------------

def play_timeline_events(midi_out, events):
    """
    Given a list of events = (time_sec, type, note, channel), sorted by time_sec.
    """
    events.sort(key=lambda e: (e[0], e[1]))

    start_wall_time = time.time()
    for i, evt in enumerate(events):
        event_time_sec, evt_type, note_num, channel = evt
        while (time.time() - start_wall_time) < event_time_sec:
            time.sleep(0.001)

        if evt_type == "on":
            midi_out.note_on(note_num, 100, channel)
            note_name = note_to_name(note_num)
            print(f"[{event_time_sec:6.2f}s] ON  ch{channel} -> {note_name}")
        else:
            midi_out.note_off(note_num, 100, channel)
            note_name = note_to_name(note_num)
            print(f"[{event_time_sec:6.2f}s] OFF ch{channel} -> {note_name}")

# ------------------------------------------------------------------
# MIDI File Saver (5 separate tracks)
# ------------------------------------------------------------------

def save_melodies_to_midi(voices: dict, bpm: int, filename: str, piece: RoundedBinaryPiece):
    """
    Saves multiple voices to a MIDI file, each voice on its own track & channel.

    We now read the instrument program numbers from piece.metadata.instruments
    (bass, tenor, alto, soprano), and we fix piano to 0.
    """
    print(f"\nPreparing to save MIDI file as {filename}...")

    # We have 5 voices total (bass, tenor, alto, soprano, piano).
    num_tracks = 5
    midi_file = MIDIFile(num_tracks)

    for i in range(num_tracks):
        midi_file.addTempo(i, 0, bpm)

    # Gather the user's chosen instruments from metadata.
    # Piano is always 0 (Acoustic Grand).
    instruments = piece.metadata.instruments
    # Program numbers (0..127)
    bass_prog = instruments.bass
    tenor_prog = instruments.tenor
    alto_prog = instruments.alto
    soprano_prog = instruments.soprano
    piano_prog = 0   # fixed

    # 5 tracks: track 0 = bass, 1 = tenor, 2 = alto, 3 = soprano, 4 = piano
    midi_file.addProgramChange(0, 0, 0, bass_prog)     # track=0, channel=0
    midi_file.addProgramChange(1, 1, 0, tenor_prog)    # track=1, channel=1
    midi_file.addProgramChange(2, 2, 0, alto_prog)     # track=2, channel=2
    midi_file.addProgramChange(3, 3, 0, soprano_prog)  # track=3, channel=3
    midi_file.addProgramChange(4, 4, 0, piano_prog)    # track=4, channel=4

    # Now write out the notes per voice.
    voice_order = ["Bass", "Tenor", "Alto", "Soprano", "Piano"]
    for i, voice_name in enumerate(voice_order):
        channel = i
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

    print("Saving MIDI file...")
    with open(filename, "wb") as outf:
        midi_file.writeFile(outf)
    print(f"Successfully saved MIDI file: {filename}")

# ------------------------------------------------------------------
# Helper: gather all lines from each section to produce a single list
# ------------------------------------------------------------------

def aggregate_voice_lines(section_list: list) -> dict:
    """
    Given a list of sections (A or B or A'), aggregates
    each voice line into a single contiguous list of NoteDuration objects
    in the order encountered.
    """
    aggregated = {
        "Bass": [],
        "Tenor": [],
        "Alto": [],
        "Soprano": [],
        "Piano": []
    }
    for sec in section_list:
        for phr in sec.phrases:
            aggregated["Bass"].extend(phr.bass)
            aggregated["Tenor"].extend(phr.tenor)
            aggregated["Alto"].extend(phr.alto)
            aggregated["Soprano"].extend(phr.soprano)
            aggregated["Piano"].extend(phr.piano)
    return aggregated

# ------------------------------------------------------------------
# New: Load an existing JSON file, parse, and play
# ------------------------------------------------------------------

def load_piece_from_json(json_path: str) -> RoundedBinaryPiece:
    """
    Reads a .json file containing data for a RoundedBinaryPiece, returns the validated object.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        raw = f.read()
    data = json.loads(raw)
    piece = RoundedBinaryPiece(**data)
    return piece

def play_piece(piece: RoundedBinaryPiece, midi_out):
    """
    Takes a RoundedBinaryPiece object, clamps & quantizes it,
    builds the final timeline (A->A repeat->B->B repeat->A'->A' repeat),
    and does real-time playback. Also returns the final note events list.
    """
    # 1) Clamp pitches & quantize durations
    clamp_and_quantize(piece, step=0.25)  # snap durations to 16th-note grid

    bpm = piece.metadata.tempo
    print(f"Playing back piece at {bpm} BPM.")

    # 2) Summaries
    print("\n--- Piece Metadata ---")
    print(f"Title: {piece.metadata.title}")
    print(f"Key Signature: {piece.metadata.key_signature}")
    print(f"Time Signature: {piece.metadata.time_signature}")
    print(f"Tempo: {piece.metadata.tempo} BPM")
    print(f"Bass Instrument: {piece.metadata.instruments.bass}")
    print(f"Tenor Instrument: {piece.metadata.instruments.tenor}")
    print(f"Alto Instrument: {piece.metadata.instruments.alto}")
    print(f"Soprano Instrument: {piece.metadata.instruments.soprano}")
    print("Piano Instrument: 0 (fixed)")
    print("----------------------\n")

    # 3) Summarize sections
    print("Section A breakdown:")
    for sec in piece.form.sectionA:
        print(f"  Subsection: {sec.section_label}")
        for phr in sec.phrases:
            print(f"    Phrase: {phr.phrase_label} "
                  f"(bass={len(phr.bass)}, tenor={len(phr.tenor)}, "
                  f"alto={len(phr.alto)}, sop={len(phr.soprano)}, piano={len(phr.piano)})")

    print("\nSection B breakdown:")
    for sec in piece.form.sectionB:
        print(f"  Subsection: {sec.section_label}")
        for phr in sec.phrases:
            print(f"    Phrase: {phr.phrase_label} "
                  f"(bass={len(phr.bass)}, tenor={len(phr.tenor)}, "
                  f"alto={len(phr.alto)}, sop={len(phr.soprano)}, piano={len(phr.piano)})")

    print("\nSection A' breakdown:")
    for sec in piece.form.sectionA_prime:
        print(f"  Subsection: {sec.section_label}")
        for phr in sec.phrases:
            print(f"    Phrase: {phr.phrase_label} "
                  f"(bass={len(phr.bass)}, tenor={len(phr.tenor)}, "
                  f"alto={len(phr.alto)}, sop={len(phr.soprano)}, piano={len(phr.piano)})")

    # 4) Build timeline for real-time playback
    sectionA_voices = aggregate_voice_lines(piece.form.sectionA)
    sectionB_voices = aggregate_voice_lines(piece.form.sectionB)
    sectionAprime_voices = aggregate_voice_lines(piece.form.sectionA_prime)

    events = []
    current_start_sec = 0.0

    def append_events_for_section(voices, start):
        new_events = build_timeline_for_section(voices, bpm, start)
        if not new_events:
            return new_events, start
        events_end_time = max(evt[0] for evt in new_events)
        return new_events, events_end_time

    # A
    A_events, current_start_sec = append_events_for_section(sectionA_voices, current_start_sec)
    events.extend(A_events)

    # repeat A
    A_events_2, current_start_sec = append_events_for_section(sectionA_voices, current_start_sec)
    events.extend(A_events_2)

    # B
    B_events, current_start_sec = append_events_for_section(sectionB_voices, current_start_sec)
    events.extend(B_events)

    # repeat B
    B_events_2, current_start_sec = append_events_for_section(sectionB_voices, current_start_sec)
    events.extend(B_events_2)

    # A'
    Aprime_events, current_start_sec = append_events_for_section(sectionAprime_voices, current_start_sec)
    events.extend(Aprime_events)

    # repeat A'
    Aprime_events_2, current_start_sec = append_events_for_section(sectionAprime_voices, current_start_sec)
    events.extend(Aprime_events_2)

    # 5) Real-time playback
    print("\n=== Starting concurrent playback of entire piece ===")
    play_timeline_events(midi_out, events)
    print("\n=== Playback complete ===")

    return events

# ------------------------------------------------------------------
# Main routine
# ------------------------------------------------------------------

def main():
    print("\nInitializing pygame and MIDI systems...")
    pygame.init()
    pygame.midi.init()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate and play procedural MIDI melodies')
    parser.add_argument('--model', type=str, default='o1',
                      help='OpenAI model to use (default: o1)')
    args = parser.parse_args()

    # Ensure outputs folder exists
    os.makedirs("outputs", exist_ok=True)

    try:
        print("Looking for MIDI output device...")
        device_id = pygame.midi.get_default_output_id()
        if device_id == -1:
            print("No MIDI output device found. Exiting.")
            sys.exit(1)
        midi_out = pygame.midi.Output(device_id)
        print(f"Successfully connected to MIDI device {device_id}")

        # We'll wait to set instruments until we have the piece data
        # (because the piece might contain instrumentation choices).
        print("=========================================")
        print("   Procedurally Generated MIDI Player   ")
        print("      (Rounded Binary Form, 5 voices)   ")
        print("=========================================\n")
        print("Available modes:")
        print("  1) Type an instruction to generate a new piece. (e.g. 'make a waltz in A minor')")
        print("  2) Type 'json' to load and play from a local JSON file matching the schema.")
        print("  3) Type 'model' to change the OpenAI model.")
        print("  4) Type 'q' to quit.\n")

        current_model = args.model

        while True:
            print(f"\nCurrent model: {current_model}")
            choice = input("Enter your command ('json', 'model', any text for generation, or 'q'): ").strip()

            if choice.lower() == 'q':
                print("Goodbye!")
                break

            elif choice.lower() == 'model':
                new_model = input("Enter new model name (or press Enter to keep current): ").strip()
                if new_model:
                    current_model = new_model
                    print(f"Model changed to: {current_model}")
                continue

            elif choice.lower() == 'json':
                # Load from existing JSON
                json_path = input("Enter path to your .json file: ").strip()
                if not os.path.isfile(json_path):
                    print(f"File not found: {json_path}")
                    continue

                try:
                    piece = load_piece_from_json(json_path)

                    # Set instruments for real-time playback
                    instruments = piece.metadata.instruments
                    midi_out.set_instrument(instruments.bass, 0)     # Bass
                    midi_out.set_instrument(instruments.tenor, 1)    # Tenor
                    midi_out.set_instrument(instruments.alto, 2)     # Alto
                    midi_out.set_instrument(instruments.soprano, 3)  # Soprano
                    midi_out.set_instrument(0, 4)                    # Piano fixed to 0

                    play_piece(piece, midi_out)
                except Exception as e:
                    print(f"Error loading or playing JSON file: {e}")

            else:
                # Generate new piece from instructions
                print("\nGenerating new musical piece in rounded binary form (5 voices + instrumentation)...")
                piece, raw_json = generate_melodies(model_name=current_model, additional_instructions=choice)

                # Configure instruments for real-time playback
                instruments = piece.metadata.instruments
                midi_out.set_instrument(instruments.bass, 0)     # Bass
                midi_out.set_instrument(instruments.tenor, 1)    # Tenor
                midi_out.set_instrument(instruments.alto, 2)     # Alto
                midi_out.set_instrument(instruments.soprano, 3)  # Soprano
                midi_out.set_instrument(0, 4)                    # Piano

                # Playback
                events = play_piece(piece, midi_out)

                # 6) Save to MIDI file & also save a log of the raw JSON
                timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                midi_filename = os.path.join("outputs", f"generated_5voice_{timestamp_str}.mid")

                # Build final contiguous voice lines for saving (A->A->B->B->A'->A'):
                sectionA_voices = aggregate_voice_lines(piece.form.sectionA)
                sectionB_voices = aggregate_voice_lines(piece.form.sectionB)
                sectionAprime_voices = aggregate_voice_lines(piece.form.sectionA_prime)

                full_bass = (sectionA_voices["Bass"] + sectionA_voices["Bass"] +
                             sectionB_voices["Bass"] + sectionB_voices["Bass"] +
                             sectionAprime_voices["Bass"] + sectionAprime_voices["Bass"])
                full_tenor = (sectionA_voices["Tenor"] + sectionA_voices["Tenor"] +
                              sectionB_voices["Tenor"] + sectionB_voices["Tenor"] +
                              sectionAprime_voices["Tenor"] + sectionAprime_voices["Tenor"])
                full_alto = (sectionA_voices["Alto"] + sectionA_voices["Alto"] +
                             sectionB_voices["Alto"] + sectionB_voices["Alto"] +
                             sectionAprime_voices["Alto"] + sectionAprime_voices["Alto"])
                full_sop =  (sectionA_voices["Soprano"] + sectionA_voices["Soprano"] +
                             sectionB_voices["Soprano"] + sectionB_voices["Soprano"] +
                             sectionAprime_voices["Soprano"] + sectionAprime_voices["Soprano"])
                full_piano = (sectionA_voices["Piano"] + sectionA_voices["Piano"] +
                              sectionB_voices["Piano"] + sectionB_voices["Piano"] +
                              sectionAprime_voices["Piano"] + sectionAprime_voices["Piano"])

                full_piece_voices = {
                    "Bass": full_bass,
                    "Tenor": full_tenor,
                    "Alto": full_alto,
                    "Soprano": full_sop,
                    "Piano": full_piano,
                }

                save_melodies_to_midi(full_piece_voices, piece.metadata.tempo, midi_filename, piece)

                # Save the raw JSON log
                log_filename = os.path.join("outputs", f"log_5voice_{timestamp_str}.json")
                print(f"Saving raw JSON log to {log_filename}")
                
                # Parse the raw JSON to add metadata
                json_data = json.loads(raw_json)
                json_data["generation_metadata"] = {
                    "user_prompt": choice,
                    "model_used": current_model,
                    "timestamp": timestamp_str
                }
                
                with open(log_filename, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2)

                print("\nPlayback and saving complete!\n")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        pygame.midi.quit()
        pygame.quit()

if __name__ == "__main__":
    main()
