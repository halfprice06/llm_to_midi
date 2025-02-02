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
# 1) Define enhanced data models now accommodating up to 5 voices
#    and instrument selection for the four main voices.
# ------------------------------------------------------------------

class NoteDuration(BaseModel):
    note: Optional[int]   # MIDI note number; use None to indicate a rest.
    duration: float       # Duration in beats.

class Instrumentation(BaseModel):
    """
    Holds the program numbers (0..127) for bass, tenor, alto, soprano.
    Piano is fixed to 0, so we don't need to store it here.
    """
    bass: int
    tenor: int
    alto: int
    soprano: int

class SongMetadata(BaseModel):
    title: str                 # A creative title for the piece.
    tempo: int                 # Recommended tempo in BPM.
    key_signature: str         # Key of the piece (e.g., "C Major").
    time_signature: str        # Time signature (e.g., "4/4").
    instruments: Instrumentation  # New field holding chosen instruments for each voice.

class Phrase(BaseModel):
    phrase_label: str
    # Each phrase now can have up to 5 separate melodic lines.
    bass: List[NoteDuration]
    tenor: List[NoteDuration]
    alto: List[NoteDuration]
    soprano: List[NoteDuration]
    piano: List[NoteDuration]
    percussion: List[NoteDuration]

class Section(BaseModel):
    section_label: str                # e.g., "A1", "B1", etc.
    phrases: List[Phrase]            # Each section has one or more phrases.

class RoundedBinaryForm(BaseModel):
    """
    A typical rounded binary form has three overall sections:
      1) A (often repeated)
      2) B (often repeated)
      3) A' (a return of the main theme, possibly varied)

    Each section can be subdivided into subsections (A1, A2, B1, B2, etc.),
    and each subsection can hold multiple phrases. Each phrase can have
    up to 5 voices: bass, tenor, alto, soprano, and piano.

    Now, each of the four main voices (bass, tenor, alto, soprano) can
    have a chosen instrument via SongMetadata.instruments, while piano
    remains fixed to program 0.
    """
    sectionA: List[Section]
    sectionB: List[Section]
    sectionA_prime: List[Section]

class RoundedBinaryPiece(BaseModel):
    metadata: SongMetadata
    form: RoundedBinaryForm

print("Data models for Rounded Binary Form (5 voices + instrumentation) defined successfully.")

# ------------------------------------------------------------------
# 2) Functions that use BAML to generate melodies with different models
# ------------------------------------------------------------------

async def generate_with_openai_o1(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using OpenAI O1 model"""
    try:
        stream = async_b.stream.GenerateMusic_OpenAIo1(theme=theme, prompt=MUSIC_PROMPT)
        result = await stream.get_final_response()
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with OpenAI O1: {e}")
        return None, ""

async def generate_with_openai_o1_mini(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using OpenAI O1 Mini model"""
    try:
        result = await async_b.GenerateMusic_OpenAIo1Mini(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with OpenAI O1 Mini: {e}")
        return None, ""

async def generate_with_openai_o3_mini(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using OpenAI O3 Mini model"""
    try:
        result = await async_b.GenerateMusic_OpenAIo3Mini(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with OpenAI O3 Mini: {e}")
        return None, ""

async def generate_with_openai_gpt4o(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using OpenAI GPT-4o model"""
    try:
        result = await async_b.GenerateMusic_OpenAIGPT4o(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with GPT-4o: {e}")
        return None, ""

async def generate_with_anthropic_sonnet(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using Anthropic Claude 3.5 Sonnet model"""
    try:
        result = await async_b.GenerateMusic_AnthropicSonnet(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with Anthropic Sonnet: {e}")
        return None, ""
    
async def generate_with_deepseek_reasoner(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using Deepseek Reasoner model"""
    try:
        result = await async_b.GenerateMusic_DeepseekReasoner(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with Deepseek Reasoner: {e}")
        return None, ""

async def generate_with_hyperbolic_deepseek_reasoner(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using Hyperbolic Deepseek Reasoner model"""
    try:
        stream = async_b.stream.GenerateMusic_HyperbolicDeepseekReasoner(theme=theme, prompt=MUSIC_PROMPT)
        result = await stream.get_final_response()
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with Hyperbolic Deepseek Reasoner: {e}")
        return None, ""

async def generate_with_anthropic_opus(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using Anthropic Opus model"""
    try:
        result = await async_b.GenerateMusic_AnthropicOpus(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with Anthropic Opus: {e}")
        return None, ""

async def generate_with_anthropic_haiku(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using Anthropic Haiku model"""
    try:
        result = await async_b.GenerateMusic_AnthropicHaiku(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with Anthropic Haiku: {e}")
        return None, ""

async def generate_with_gemini_15_flash(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using Gemini 1.5 Flash model"""
    try:
        result = await async_b.GenerateMusic_Gemini15Flash(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with Gemini 1.5 Flash: {e}")
        return None, ""

async def generate_with_gemini_15_pro(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using Gemini 1.5 Pro model"""
    try:
        result = await async_b.GenerateMusic_Gemini15Pro(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with Gemini 1.5 Pro: {e}")
        return None, ""

async def generate_with_gemini_20_flash_exp(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using Gemini 2.0 Flash Exp model"""
    try:
        result = await async_b.GenerateMusic_Gemini20FlashExp(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with Gemini 2.0 Flash Exp: {e}")
        return None, ""

async def generate_with_gemini_20_flash_thinking_exp(theme: str) -> Tuple[RoundedBinaryPiece, str]:
    """Generate melody using Gemini 2.0 Flash Thinking Exp model"""
    try:
        result = await async_b.GenerateMusic_Gemini20FlashThinkingExp(theme=theme, prompt=MUSIC_PROMPT)
        return result, json.dumps(result.dict(), indent=2)
    except Exception as e:
        print(f"Error with Gemini 2.0 Flash Thinking Exp: {e}")
        return None, ""

# Map model names to their generation functions
MODEL_GENERATORS = {
    "o1": generate_with_openai_o1,
    "o1-mini": generate_with_openai_o1_mini,
    "o3-mini": generate_with_openai_o3_mini,
    # "gpt4o": generate_with_openai_gpt4o,
    "sonnet": generate_with_anthropic_sonnet,
    # "hyperbolic-deepseek": generate_with_hyperbolic_deepseek_reasoner,
    "opus": generate_with_anthropic_opus,
    # "haiku": generate_with_anthropic_haiku,
    # "gemini-15-flash": generate_with_gemini_15_flash,
    "gemini-15-pro": generate_with_gemini_15_pro,
    "gemini-20-flash": generate_with_gemini_20_flash_exp,
    "gemini-20-flash-thinking": generate_with_gemini_20_flash_thinking_exp
}

# The base prompt used for all models
MUSIC_PROMPT = """
# Music Composition Instructions

You are an expert composer well-versed in music theory.

## Form
Compose a short piece in rounded binary form (A, B, A'). Each section (A, B, A') can be further subdivided into one or more subsections (A1, A2, etc.).

## Voices
Each subsection must contain a minimum of two phrases, and each phrase must have these voices:
- bass
- tenor 
- alto
- soprano
- piano
- percussion (channel 10) - optional, only include if it fits the genre and style

## Instruments
Choose an appropriate MIDI instrument for each of the four voices:
- bass
- tenor
- alto 
- soprano

*Note: The piano voice is always instrument 0 (Acoustic Grand).*
*Note: The percussion track uses General MIDI drum map note numbers on channel 10.*

## Composition Guidelines
- Use varied rhythms for each part
- Keep each part coherent, with independent but harmonically compatible lines
- Use good voice leading between the parts, avoid parallel fifths and octaves
- Write interesting motifs and follow the rules of Western tonality and music theory
- Ensure there is a lot of variety between the phrases
- The final A' must restate A's theme
- Parts may rest at times to give other parts a chance to shine and listeners a chance to catch their breath
- Use the percussion track to provide rhythmic foundation and interest (if appropriate for the genre)

## Technical Reminders
- Each section must contain a minimum of two phrases
- Make phrases extremely long and interesting
- "note" is a MIDI note number:
  - For melodic parts (60=middle C)
  - For percussion (35=acoustic bass drum, 38=acoustic snare, 42=closed hi-hat, etc.)
  - null indicates a rest
- "duration" is in beats (1.0=quarter, 0.5=eighth, etc.)
- End each phrase with an interesting cadence or a long note
- The final A' must restate A's theme
- **EXTREMELY IMPORTANT**: Make sure there is a variety of rhythms and counterpoint among the various voices. Limit the amount of unison rhythms.
- Use the piano to help keep the beat and add percussive interest, for example, by arpeggiating the chords
- Use the percussion track to enhance the rhythmic structure and add groove, but only if it fits the genre and style of the piece
- If the percussion track would not fit the genre or style (e.g., for a nocturne or other delicate pieces), you can omit it
- Do not complain that there are too many notes to write, just do your best.
"""

# ------------------------------------------------------------------
# 3) Helper function to save the generated piece to MIDI
# ------------------------------------------------------------------

def save_melodies_to_midi(voices: dict, bpm: int, filename: str, piece: RoundedBinaryPiece):
    """
    Saves multiple voices to a MIDI file, each voice on its own track & channel.
    We read the instrument program numbers from piece.metadata.instruments
    (bass, tenor, alto, soprano), and we fix piano to 0.
    """
    print(f"\nPreparing to save MIDI file as {filename}...")

    # Count how many tracks we need (5 or 6 depending on if percussion is present)
    has_percussion = "Percussion" in voices and voices["Percussion"]
    num_tracks = 6 if has_percussion else 5
    midi_file = MIDIFile(num_tracks)

    for i in range(num_tracks):
        midi_file.addTempo(i, 0, bpm)

    # Gather the user's chosen instruments from metadata.
    # Piano is always 0 (Acoustic Grand).
    # Percussion is always on channel 10.
    instruments = piece.metadata.instruments
    # Program numbers (0..127)
    bass_prog = instruments.bass
    tenor_prog = instruments.tenor
    alto_prog = instruments.alto
    soprano_prog = instruments.soprano
    piano_prog = 0   # fixed

    # Add program changes for all tracks except percussion
    midi_file.addProgramChange(0, 0, 0, bass_prog)     # track=0, channel=0
    midi_file.addProgramChange(1, 1, 0, tenor_prog)    # track=1, channel=1
    midi_file.addProgramChange(2, 2, 0, alto_prog)     # track=2, channel=2
    midi_file.addProgramChange(3, 3, 0, soprano_prog)  # track=3, channel=3
    midi_file.addProgramChange(4, 4, 0, piano_prog)    # track=4, channel=4
    # No program change needed for percussion (channel 10)

    # Now write out the notes per voice.
    voice_order = ["Bass", "Tenor", "Alto", "Soprano", "Piano"]
    if has_percussion:
        voice_order.append("Percussion")

    for i, voice_name in enumerate(voice_order):
        channel = 9 if voice_name == "Percussion" else i  # Channel 10 (index 9) for percussion
        time_pos = 0.0
        track_notes = voices[voice_name]

        if track_notes:  # Only process if we have notes for this voice
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
# 4) Helper function to aggregate voice lines from sections
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
        "Piano": [],
        "Percussion": []
    }
    for sec in section_list:
        for phr in sec.phrases:
            aggregated["Bass"].extend(phr.bass)
            aggregated["Tenor"].extend(phr.tenor)
            aggregated["Alto"].extend(phr.alto)
            aggregated["Soprano"].extend(phr.soprano)
            aggregated["Piano"].extend(phr.piano)
            # Only extend percussion if it exists
            if hasattr(phr, 'percussion') and phr.percussion is not None:
                aggregated["Percussion"].extend(phr.percussion)
    
    # Remove empty percussion track if no percussion was added
    if not aggregated["Percussion"]:
        del aggregated["Percussion"]
        
    return aggregated

# ------------------------------------------------------------------
# 5) Main function to generate and save pieces from all models
# ------------------------------------------------------------------

async def generate_melodies(theme: str, models: List[str] = None) -> None:
    """
    Generate melodies using specified models concurrently and save them to MIDI files.
    If no models specified, use all available models.
    """
    if not models:
        models = list(MODEL_GENERATORS.keys())

    # Create a safe folder name from the theme
    safe_theme = "".join(c for c in theme if c.isalnum() or c in (' ', '-')).strip()
    safe_theme = safe_theme.replace(' ', '_')
    
    # Create timestamp for the batch
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H%M%S")
    
    # Create the theme-specific output folder
    theme_folder = os.path.join("outputs", f"{date_str} - {time_str}_{safe_theme}")
    os.makedirs(theme_folder, exist_ok=True)

    # Track successful and failed generations
    successful_generations = []
    failed_generations = []

    # Create tasks for all model generations
    tasks = []
    for model in models:
        if model not in MODEL_GENERATORS:
            print(f"Warning: Unknown model '{model}' - skipping")
            failed_generations.append((model, "Unknown model"))
            continue

        print(f"\nStarting melody generation using {model}...")
        generator = MODEL_GENERATORS[model]
        tasks.append(generator(theme))

    # Run all tasks concurrently and wait for results
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    for model, result in zip(models, results):
        if isinstance(result, Exception):
            print(f"Error: Generation failed with {model}: {str(result)}")
            failed_generations.append((model, str(result)))
            continue

        if result is None or result[0] is None:
            print(f"Error: No output generated from {model}")
            failed_generations.append((model, "No output generated"))
            continue

        try:
            piece, raw_json = result
            
            # Format the date for filename
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Clean up the title and key for filename use (remove special characters)
            safe_title = "".join(c for c in piece.metadata.title if c.isalnum() or c in (' ', '-')).strip()
            safe_key = "".join(c for c in piece.metadata.key_signature if c.isalnum() or c in (' ', '-')).strip()
            
            # Create filename with the new format
            base_filename = f"{date_str} - {model} - {safe_title} - {safe_key} - {piece.metadata.tempo}bpm"
            
            # Save MIDI file in the theme folder
            midi_filename = os.path.join(theme_folder, f"{base_filename}.mid")

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
            full_sop = (sectionA_voices["Soprano"] + sectionA_voices["Soprano"] +
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
                "Piano": full_piano
            }

            # Only add percussion if it exists in all sections
            if ("Percussion" in sectionA_voices and 
                "Percussion" in sectionB_voices and 
                "Percussion" in sectionAprime_voices):
                full_piece_voices["Percussion"] = (
                    sectionA_voices["Percussion"] + sectionA_voices["Percussion"] +
                    sectionB_voices["Percussion"] + sectionB_voices["Percussion"] +
                    sectionAprime_voices["Percussion"] + sectionAprime_voices["Percussion"]
                )

            save_melodies_to_midi(full_piece_voices, piece.metadata.tempo, midi_filename, piece)

            # Save the raw JSON log in the theme folder
            log_filename = os.path.join(theme_folder, f"{base_filename}.json")
            print(f"Saving raw JSON log to {log_filename}")
            
            # Parse the raw JSON to add metadata
            json_data = json.loads(raw_json)
            json_data["generation_metadata"] = {
                "user_prompt": theme,
                "model_used": model,
                "timestamp": date_str + " " + time_str
            }
            
            with open(log_filename, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)

            successful_generations.append(model)
            
        except Exception as e:
            print(f"Error: Failed to save output from {model}: {str(e)}")
            failed_generations.append((model, f"Failed to save output: {str(e)}"))

    # Print summary
    print("\n=== Generation Summary ===")
    print(f"\nOutput folder: {theme_folder}")
    
    if successful_generations:
        print(f"\nSuccessful generations ({len(successful_generations)}):")
        for model in successful_generations:
            print(f"  ✓ {model}")
    
    if failed_generations:
        print(f"\nFailed generations ({len(failed_generations)}):")
        for model, error in failed_generations:
            print(f"  ✗ {model}: {error}")
    
    if not successful_generations:
        print("\nWarning: No successful generations!")
    
    print("\nGeneration complete!")

if __name__ == "__main__":
    print("\nTesting melody generator (rounded binary form, up to 5 voices + instrumentation)...")
    test_theme = "Write a short test melody in C major"
    print(f"\nGenerating test melody with theme: {test_theme}")
    asyncio.run(generate_melodies(test_theme))
