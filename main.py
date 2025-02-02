#!/usr/bin/env python3

"""
Procedurally Generated MIDI Melody Generator (Rounded Binary Edition, 5-Voice Version)

Generates musical pieces in rounded binary form (A, B, A') with up to 5 separate voices
(bass, tenor, alto, soprano, piano) using various LLM models through BAML.

Each generated piece is saved as:
1. A multi-track MIDI file in the "outputs/" folder
2. A JSON log file capturing the raw schema data from the LLM

Available models are automatically determined from the melody generator's MODEL_GENERATORS.

Requires:
    pip install pydantic MIDIUtil baml-py
"""
import dotenv
import os
import asyncio

dotenv.load_dotenv()

from melody_generator import generate_melodies, MODEL_GENERATORS

async def main():
    # Ensure outputs folder exists
    os.makedirs("outputs", exist_ok=True)

    print("=========================================")
    print("   Procedurally Generated MIDI Maker    ")
    print("      (Rounded Binary Form, 5 voices)   ")
    print("=========================================\n")

    # Show available models
    print("Available models:")
    for model in MODEL_GENERATORS.keys():
        print(f"  - {model}")
    print()

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
    print("Using all available models...")

    # Generate the melodies using all available models concurrently
    await generate_melodies(theme)

if __name__ == "__main__":
    asyncio.run(main()) 