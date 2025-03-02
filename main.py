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

Uses BAML with various LLM models for generation.
The model can be specified via command-line argument.

Requires:
    pip install pydantic MIDIUtil baml-client python-dotenv
"""
import dotenv
import os
import asyncio
import argparse
import sys
from melody_generator import plan_and_generate_modular_song

dotenv.load_dotenv()

# Function to handle listing available models
def list_available_models():
    try:
        from list_models import extract_clients_from_baml
        
        baml_file = os.path.join("baml_src", "clients.baml")
        clients = extract_clients_from_baml(baml_file)
        
        if not clients:
            print("No clients found or error parsing the BAML file.")
            sys.exit(1)
        
        print("\n===== Available Models for Melody Generation =====\n")
        print(f"{'Client Name':<25} {'Provider':<20} {'Model':<30}")
        print("-" * 75)
        
        for client_name, provider, model in sorted(clients, key=lambda x: x[0]):
            print(f"{client_name:<25} {provider:<20} {model:<30}")
            
        print()
        sys.exit(0)
    except ImportError:
        print("Could not import list_models. Make sure list_models.py is in the current directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error listing models: {e}")
        sys.exit(1)

async def generate_with_model(theme: str, model: str, idx: int, total: int):
    """
    Generate a piece with a specific model, with appropriate console output.
    """
    try:
        print(f"\n=========================================")
        print(f"MODEL {idx+1} of {total}: {model}")
        print(f"=========================================\n")
        
        print("This will be done in two steps:")
        print("1. Generating a composition plan")
        print("2. Creating the full piece based on that plan\n")
        
        await plan_and_generate_modular_song(theme, model)
        
        print(f"\nCompleted generation with model: {model}")
        return (True, model, None)
    except Exception as e:
        print(f"\nError generating with model {model}: {e}")
        import traceback
        traceback.print_exc()
        return (False, model, str(e))

async def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate music based on a theme.")
    parser.add_argument("--theme", type=str, 
                        help="Theme for the composition")
    parser.add_argument("--model", type=str, action="append",
                        help="Model to use (can specify multiple times)")
    parser.add_argument("--models", type=str,
                        help="Comma-separated list of models to run sequentially")
    parser.add_argument("--list-models", action="store_true",
                        help="List all available models and exit")
    parser.add_argument("--concurrent", action="store_true",
                        help="Run models concurrently instead of sequentially")
    args = parser.parse_args()
    
    # If --list-models flag is set, show available models and exit
    if args.list_models:
        list_available_models()

    # Ensure outputs folder exists
    os.makedirs("outputs", exist_ok=True)

    print("=========================================")
    print("   Procedurally Generated MIDI Maker    ")
    print("        (Modular Composition)           ")
    print("=========================================\n")

    # Get theme from user if not provided via command line
    theme = args.theme
    if not theme:
        print("Enter your theme/instructions for the composition.")
        print("Examples:")
        print("  - Write a cheerful waltz in C major")
        print("  - Create a melancholic nocturne in F minor")
        theme = input("\nYour theme: ").strip()

        if not theme:
            print("No theme provided. Using default theme.")
            theme = "Write a cheerful waltz in C major"
    
    # Process model arguments to create a list of models to run
    models_to_run = []
    
    # Add models from --model arguments (can be specified multiple times)
    if args.model:
        models_to_run.extend(args.model)
    
    # Add models from --models argument (comma-separated list)
    if args.models:
        models_list = [m.strip() for m in args.models.split(',') if m.strip()]
        models_to_run.extend(models_list)
    
    # Remove duplicates while preserving order
    models_to_run = list(dict.fromkeys(models_to_run))
    
    # If no models specified, run with default
    if not models_to_run:
        # Run with default model
        print(f"\nGenerating music with theme: {theme}")
        print("Using default model")
        print("\nThis will be done in two steps:")
        print("1. Generating a composition plan")
        print("2. Creating the full piece based on that plan\n")
        
        await plan_and_generate_modular_song(theme, None)
    else:
        # Run with specified models
        print(f"\nGenerating music with theme: {theme}")
        total_models = len(models_to_run)
        
        if args.concurrent:
            print(f"Running generation concurrently for {total_models} models: {', '.join(models_to_run)}")
            
            # Create tasks for all models
            tasks = [
                generate_with_model(theme, model, idx, total_models)
                for idx, model in enumerate(models_to_run)
            ]
            
            # Run all tasks concurrently and wait for completion
            results = await asyncio.gather(*tasks, return_exceptions=False)
            
            # Summarize results
            print("\n=========================================")
            print("GENERATION SUMMARY")
            print("=========================================")
            
            success_count = 0
            failure_count = 0
            
            for success, model, error in results:
                if success:
                    success_count += 1
                    print(f"✓ {model}: Successfully generated")
                else:
                    failure_count += 1
                    print(f"✗ {model}: Failed - {error}")
            
            print(f"\nCompleted: {success_count}/{total_models} successful, {failure_count}/{total_models} failed")
            print("Check the outputs folder for the generated MIDI files.")
        else:
            print(f"Running generation sequentially for {total_models} models: {', '.join(models_to_run)}")
            
            # Run models one at a time
            for idx, model in enumerate(models_to_run):
                result = await generate_with_model(theme, model, idx, total_models)
                
                if idx < len(models_to_run) - 1:
                    print("\nMoving to next model...\n")

if __name__ == "__main__":
    asyncio.run(main()) 