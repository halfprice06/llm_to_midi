# LLM to MIDI: Procedurally Generated Music

Generate musical compositions using LLMs through a structured, modular approach. Each piece includes multiple voices (bass, tenor, alto, soprano, piano) and optional percussion.

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install requirements:
   ```
   pip install -r requirements.txt
   ```

3. Set up API keys in `.env` file (copy from `.env.example`):
   ```
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-...
   # etc.
   ```

## Usage

### Basic Usage

Run the main script:
```
python main.py
```

You'll be prompted to enter a theme for your composition, such as:
- "Write a cheerful waltz in C major"
- "Create a melancholic nocturne in F minor"

### Command-line Options

The following command-line options are available:

```
python main.py [--theme "Your theme"] [--model MODEL] [--models MODEL1,MODEL2] [--list-models]
```

- `--theme`: Specify the composition theme directly (otherwise you'll be prompted)
- `--model`: Specify which LLM model to use (can be used multiple times for sequential generation)
- `--models`: Comma-separated list of models to run sequentially
- `--list-models`: Display all available models and exit

### Selecting Different Models

You can specify which LLM model to use for generation via the `--model` parameter:

```
python main.py --model AnthropicSonnet37 --theme "Create a jazzy waltz in D minor"
```

To see all available models:

```
python main.py --list-models
```

### Sequential Model Generation

You can generate music with multiple models sequentially using the same theme. This allows you to compare how different models interpret the same prompt:

```
# Use --model multiple times
python main.py --model AnthropicSonnet37 --model OpenAIGPT4o --theme "Create a jazzy waltz"

# OR use comma-separated list with --models
python main.py --models "AnthropicSonnet37,OpenAIGPT4o,AnthropicHaiku" --theme "Create a jazzy waltz"
```

Each model will generate its own composition, and all MIDI files will be saved with the model name included in the filename.

### Recommended Models

Some recommended models:
- `AnthropicSonnet37` (Claude 3.7 Sonnet) - Good overall quality
- `OpenAIo1` (OpenAI o1) - Creative compositions
- `AnthropicHaiku` (Claude 3.5 Haiku) - Faster generation, suitable for simpler pieces

## How It Works

The application uses the Client Registry feature from BAML to dynamically select different LLM models at runtime. This allows you to experiment with different models without changing any code.

The generation process occurs in two steps:
1. First, it creates a composition plan with sections and phrases
2. Then it generates the actual musical content following that plan

Each piece is saved as:
- A multi-track MIDI file in the "outputs/" folder (with date, time, model name, and theme)
- A JSON log file capturing both the composition plan and the final piece data

## Technical Details

This project uses BAML (Basically, A Made-Up Language) to structure LLM prompts for music generation. The models are defined in `baml_src/clients.baml` and can be dynamically selected at runtime.

The Client Registry feature allows changing the model without modifying the BAML functions directly.

## Future Improvements

- Improve prompts with few-shot examples for better chord structure and melodies
- Add support for more musical styles and structures
- Implement control for dynamics and expressive elements
- Add a web interface for easier model selection and theme input

