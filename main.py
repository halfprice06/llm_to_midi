#!/usr/bin/env python3

"""
Procedurally Generated MIDI Melody Generator (Modular Composition Edition)

Generates musical pieces using a two-step process:
1. First generates a composition plan with sections and phrases
2. Then generates the actual musical content following that plan

Each generated piece includes:
- Multiple voices: bass, tenor, alto, soprano, piano, and optional percussion
- A structured approach with clearly defined sections and phrases
- Musical coherence guided by the composition plan

Each piece is saved as:
1. A multi-track MIDI file in the "outputs/" folder
2. A JSON log file capturing both the composition plan and the final piece data

Uses BAML with Anthropic's Claude models for generation.

Requires:
    pip install pydantic MIDIUtil baml-client python-dotenv
"""
import dotenv
import os
import asyncio
from melody_generator import plan_and_generate_modular_song

dotenv.load_dotenv()

async def main():
    # Ensure outputs folder exists
    os.makedirs("outputs", exist_ok=True)

    print("=========================================")
    print("   Procedurally Generated MIDI Maker    ")
    print("        (Modular Composition)           ")
    print("=========================================\n")

    # Get theme from user
    print("Enter your theme/instructions for the composition.")
    print("Examples:")
    print("  - Write a cheerful waltz in C major")
    print("  - Create a melancholic nocturne in F minor")
    theme = input("\nYour theme: ").strip()

    if not theme:
        print("No theme provided. Using default theme.")
        theme = "Write a cheerful waltz in C major"

    print(f"\nGenerating music with theme: {theme}")
    print("\nThis will be done in two steps:")
    print("1. Generating a composition plan")
    print("2. Creating the full piece based on that plan\n")

    # Generate the piece using the new modular approach
    await plan_and_generate_modular_song(theme)

if __name__ == "__main__":
    asyncio.run(main()) 