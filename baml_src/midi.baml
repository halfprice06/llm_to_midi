// Represents the duration and pitch of a musical note
class NoteDuration {
  note int? @description("MIDI note number, null indicates a rest. For percussion (channel 10), this represents the drum/percussion instrument number.")
  duration float @description("Duration in beats")
}


// Holds program numbers (0-127) for different voices
class Instrumentation {
  bass int @description("Program number for bass voice")
  tenor int @description("Program number for tenor voice")
  alto int @description("Program number for alto voice")
  soprano int @description("Program number for soprano voice")
}

class SongMetadata {
  title string @description("Creative title for the piece")
  tempo int @description("Recommended tempo in BPM")
  key_signature string @description("Key of the piece (e.g., 'C Major')")
  time_signature string @description("Time signature (e.g., '4/4')")
  instruments Instrumentation
}

class Phrase {
  phrase_label string
  bass NoteDuration[]
  tenor NoteDuration[]
  alto NoteDuration[]
  soprano NoteDuration[]
  piano NoteDuration[]
  percussion NoteDuration[] @description("Percussion track (channel 10) - uses General MIDI drum map note numbers")
}

class Section {
  section_label string @description("e.g., 'A1', 'B1', etc.")
  phrases Phrase[]
}

// Represents a musical piece in rounded binary form (A-B-A') structure
class RoundedBinaryForm {
  sectionA Section[]
  sectionB Section[]
  sectionA_prime Section[]
}

class RoundedBinaryPiece {
  metadata SongMetadata
  form RoundedBinaryForm
}

function GenerateMusic_OpenAIo1(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "OpenAIo1"
  prompt #"
{{ prompt }}

{{ ctx.output_format }}

Additional user instructions:

{{ theme }}
  "#
}

function GenerateMusic_OpenAIo1Mini(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "OpenAIo1Mini" 
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_OpenAIo3Mini(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "OpenAIo3Mini"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_OpenAIGPT4o(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "OpenAIGPT4o"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_HyperbolicDeepseekReasoner(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "HyperbolicDeepseekReasoner"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_DeepseekReasoner(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "DeepseekReasoner"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_AnthropicSonnet(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "AnthropicSonnet"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_AnthropicOpus(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "AnthropicOpus"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_AnthropicHaiku(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "AnthropicHaiku"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_Gemini15Flash(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "Gemini15Flash"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_Gemini15Pro(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "Gemini15Pro"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_Gemini20FlashExp(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "Gemini20FlashExp"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}

function GenerateMusic_Gemini20FlashThinkingExp(theme: string, prompt: string) -> RoundedBinaryPiece {
  client "Gemini20FlashThinkingExp"
  prompt #"
{{ prompt }}

Additional user instructions:

{{ theme }}

{{ ctx.output_format }}
  "#
}


test TestName {
  functions [GenerateMusic_DeepseekReasoner]
  args {
    theme #"
      Write a waltz in A Minor
    "#
    prompt #"
# Music Composition Instructions

You are an expert composer well-versed in music theory.

## Form
Compose a short piece in rounded binary form (A, B, A'). Each section (A, B, A') can be further subdivided into one or more subsections (A1, A2, etc.).

## Voices
Each subsection must contain a minimum of two phrases, and each phrase can have up to 5 voices:
- bass
- tenor 
- alto
- soprano
- piano

## Instruments
Choose an appropriate MIDI instrument for each of the four voices:
- bass
- tenor
- alto 
- soprano

*Note: The piano voice is always instrument 0 (Acoustic Grand).*

## Composition Guidelines
- Use varied rhythms for each part
- Keep each part coherent, with independent but harmonically compatible lines
- Use good voice leading between the parts, avoid parallel fifths and octaves
- Write interesting motifs and follow the rules of Western tonality and music theory
- Ensure there is a lot of variety between the phrases
- The final A' must restate A's theme
- Parts may rest at times to give other parts a chance to shine and listeners a chance to catch their breath

## Technical Reminders
- Each section must contain a minimum of two phrases
- Make phrases extremely long and interesting
- "note" is a MIDI note number (60=middle C) or null for rest
- "duration" is in beats (1.0=quarter, 0.5=eighth, etc.)
- End each phrase with an interesting cadence or a long note
- The final A' must restate A's theme
- **EXTREMELY IMPORTANT**: Make sure there is a variety of rhythms and counterpoint among the various voices. Limit the amount of unison rhythms.
- Use the piano to help keep the beat and add percussive interest, for example, by arpeggiating the chords
    "#
  }
}
