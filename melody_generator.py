import openai
import argparse
from typing import List, Optional, Tuple
from pydantic import BaseModel

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
# 2) The function that calls the OpenAI API with advanced music theory instructions.
#    Now also instructs the model to fill in instrumentation choices for bass/tenor/alto/soprano.
# ------------------------------------------------------------------

def generate_melodies(model_name: str = "o3-mini", additional_instructions: str = "") -> Tuple[RoundedBinaryPiece, str]:
    """
    Calls the OpenAI API to generate a short classical-style piece in rounded binary form,
    up to 5 voices (bass, tenor, alto, soprano, and piano). Also requests that the model
    specify an instrument (MIDI program number) for bass, tenor, alto, and soprano.
    The piano voice is always instrument 0.

    Args:
        model_name: The OpenAI model to use (default: "o3-mini")
        additional_instructions: Optional instructions for the composition

    Returns: (RoundedBinaryPiece, raw_json_str)
    """
    print("\nGenerating new musical piece in rounded binary form with 5 voices + instrumentation...")
    try:
        print(f"Using OpenAI model: {model_name}")

        # System message: instructions for multi-voice classical composition.
        system_msg = """
You are an expert composer well-versed in music theory.
Compose a short piece in rounded binary form (A, B, A').
Each section (A, B, A') can be further subdivided into one or more subsections (A1, A2, etc.).
Each subsection must contain a minimum of two phrases, and each phrase can have up to 5 voices:
  - bass
  - tenor
  - alto
  - soprano
  - piano

Additionally, choose an appropriate MIDI instrument for each of the four voices:
  - bass
  - tenor
  - alto
  - soprano
The piano voice is always instrument 0 (Acoustic Grand).

Use varied rhythms for each part. Keep each part coherent, with independent but harmonically compatible lines. Use good voice leading between the parts, avoid parallel fifths and octaves, write interesting motifs, and follow the rules of Western tonality and music theory. 

Ensure there is a lot of variety between the phrases. The final A' must restate A's theme.
It is ok to allow parts to rest at times to give the other parts a chance to shine and the listener a chance to catch their breath.

"""



        # User message: explicit JSON schema instructions, including the new instrumentation field,
        # plus any optional user instructions appended.
        user_msg = f"""
Generate a short musical piece in rounded binary form, JSON only, matching this schema:

{{
  "metadata": {{
    "title": <string>,
    "tempo": <integer>,
    "key_signature": <string>,
    "time_signature": <string>,
    "instruments": {{
      "bass": <int>,       # MIDI program number (0..127)
      "tenor": <int>,
      "alto": <int>,
      "soprano": <int>
    }}
  }},
  "form": {{
    "sectionA": [
      {{
        "section_label": <string>,
        "phrases": [
          {{
            "phrase_label": <string>,
            "bass": [
              {{"note": <int or null>, "duration": <float>}}, ...
            ],
            "tenor": [
              {{"note": <int or null>, "duration": <float>}}, ...
            ],
            "alto": [
              {{"note": <int or null>, "duration": <float>}}, ...
            ],
            "soprano": [
              {{"note": <int or null>, "duration": <float>}}, ...
            ],
            "piano": [
              {{"note": <int or null>, "duration": <float>}}, ...
            ]
          }},
          ...
        ]
      }},
      ...
    ],
    "sectionB": [...],
    "sectionA_prime": [...]
  }}
}}

Notes:
- Fill in a program number for each of bass, tenor, alto, soprano.
  Piano is fixed to program 0.
- Each section must contain a minimum of two phrases.
- Use up to 5 voices (bass, tenor, alto, soprano, piano).
- "note" is a MIDI note number (60=middle C) or null for rest.
- "duration" is in beats (1.0=quarter, 0.5=eighth, etc.).
- End each phrase with an interesting cadence or a long note.
- The final A' must restate A's theme.
- DO NOT give all parts the same rhythms; create variety and counterpoint.
- The piano is used to help keep the beat or add percussive interest.
- Additional user instructions:
{additional_instructions}
"""

        print("Sending request to OpenAI API...")
        completion = openai.beta.chat.completions.parse(
            model=model_name,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            reasoning_effort="high",
            response_format=RoundedBinaryPiece,
            temperature=1,
        )

        print("Successfully received response from OpenAI")
        # Store both the parsed object and the raw JSON string
        raw_json_str = completion.choices[0].message.content
        result = completion.choices[0].message.parsed
        return result, raw_json_str

    except Exception as e:
        print("OpenAI API error or parsing error:", e)
        print("Falling back to default 5-voice piece with default instruments...")

        # Fallback instruments (like the old defaults):
        fallback_instruments = Instrumentation(
            bass=32,     # Acoustic Bass
            tenor=42,    # Cello
            alto=71,     # Clarinet
            soprano=73   # Flute
        )
        fallback_metadata = SongMetadata(
            title="Untitled Rounded Binary",
            tempo=120,
            key_signature="C Major",
            time_signature="4/4",
            instruments=fallback_instruments
        )
        fallback_form = RoundedBinaryForm(
            sectionA=[Section(section_label="A1", phrases=[])],
            sectionB=[Section(section_label="B1", phrases=[])],
            sectionA_prime=[Section(section_label="A1_prime", phrases=[])]
        )
        fallback_piece = RoundedBinaryPiece(metadata=fallback_metadata, form=fallback_form)

        # Return the fallback piece plus an empty string for raw JSON
        return fallback_piece, ""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate melodies using OpenAI')
    parser.add_argument('--model', type=str, default='o3-mini',
                      help='OpenAI model to use (default: o3-mini)')
    args = parser.parse_args()

    print("\nTesting melody generator (rounded binary form, up to 5 voices + instrumentation)...")
    piece_obj, raw_json = generate_melodies(model_name=args.model, additional_instructions="Sample user instructions.")
    print("\nGenerated piece details:")

    print("METADATA:", piece_obj.metadata)
    for sec in piece_obj.form.sectionA:
        print(f"\nSection A subsection label: {sec.section_label}")
        for phr in sec.phrases:
            print(f"  Phrase label: {phr.phrase_label}")
            print(f"    Bass: {phr.bass}")
            print(f"    Tenor: {phr.tenor}")
            print(f"    Alto: {phr.alto}")
            print(f"    Soprano: {phr.soprano}")
            print(f"    Piano: {phr.piano}")

    for sec in piece_obj.form.sectionB:
        print(f"\nSection B subsection label: {sec.section_label}")
        for phr in sec.phrases:
            print(f"  Phrase label: {phr.phrase_label}")
            print(f"    Bass: {phr.bass}")
            print(f"    Tenor: {phr.tenor}")
            print(f"    Alto: {phr.alto}")
            print(f"    Soprano: {phr.soprano}")
            print(f"    Piano: {phr.piano}")

    for sec in piece_obj.form.sectionA_prime:
        print(f"\nSection A' subsection label: {sec.section_label}")
        for phr in sec.phrases:
            print(f"  Phrase label: {phr.phrase_label}")
            print(f"    Bass: {phr.bass}")
            print(f"    Tenor: {phr.tenor}")
            print(f"    Alto: {phr.alto}")
            print(f"    Soprano: {phr.soprano}")
            print(f"    Piano: {phr.piano}")
