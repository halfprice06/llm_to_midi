/////////////////////////////
// Existing classes
/////////////////////////////

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

/////////////////////////////
// NEW: Flexible modular design
/////////////////////////////


class SectionPlan {
  label string @description("Label for this section, e.g., 'Intro', 'Verse', 'Chorus', Solo/Instrumental Break, Exposition, A, B, C, etc.")
  description string? @description("Textual description for the section's role in the piece.")
  number_of_phrases int @description("How many phrases are planned in this section.")
}

class CompositionPlan {
  plan_title string @description("A short descriptive title for the composition plan.")
  style string? @description("Optional style or genre for the piece, e.g. 'classical waltz', 'jazz ballad', etc.")
  sections SectionPlan[] @description("A list of sections planned for the piece.")
}

class ModularPhrase {
  phrase_label string
  bass NoteDuration[]
  tenor NoteDuration[]
  alto NoteDuration[]
  soprano NoteDuration[]
  piano NoteDuration[]
  percussion NoteDuration[]? @description("Optional percussion track (channel 10) - uses General MIDI drum map note numbers")
}

class ModularSection {
  section_label string @description("Label for this section, e.g., 'Intro', 'Verse', 'Chorus', Solo/Instrumental Break, Exposition, A, B, C, etc.")
  phrases ModularPhrase[] @description("")
}

class ModularPiece {
  metadata SongMetadata
  sections ModularSection[]
}

function GenerateCompositionPlan(theme: string) -> CompositionPlan {
  client "OpenAIo1"
  prompt #"
You are an expert music composer. The user wants to plan the structure of a piece
BEFORE generating any actual note-level content.

They have asked for the following theme or instructions:
{{ theme }}

Return a JSON object that follows the schema (CompositionPlan) exactly:
{{ ctx.output_format }}

Guidelines for plan:
- Provide a plan title (plan_title).
- Optionally specify a style or genre (style).
- Provide a list of sections, each with a label, optional description, and how many phrases it should have.
- The user wants to see the piece broken into any structure you see fit (intro, verse, chorus, coda, etc.).
- Only describe the plan; do NOT generate note-level detail at this step.
"#
}

function GenerateModularSong(plan: CompositionPlan) -> ModularPiece {
  client "OpenAIo1"
  prompt #"
You are an expert composer. A user has already decided on the piece structure (sections, phrases) via the following plan:
{{ plan }}

Now please fill in the actual note-level content for each section and each phrase.

Requirements / guidelines:
- Each section in 'plan.sections' must appear in the final output with a matching label.
- For each planned phrase, generate enough note-level detail in the voices (bass, tenor, alto, soprano, piano, and optionally percussion).
- The final output must match the 'ModularPiece' schema exactly:

{{ ctx.output_format }}

Notes:
- Use valid MIDI note numbers (0..127), or null for rests.
- For percussion (channel 10), use the typical GM drum note numbers (35, 36, 38, 42, etc.) if applicable.
- The 'metadata' can be guessed or derived from the plan. Provide a creative title, a tempo, a key signature, time signature, etc.
- The user wants a cohesive piece but with the plan's structure.
"#
}

test GenerateCompositionPlan {
  functions [GenerateCompositionPlan]
  args {
    theme #"
      Write Twinkle Twinkle Little Star in C
    "#
  }
}

test GenerateModularSong {
  functions [GenerateModularSong]
  args {
    plan {
      plan_title "Twinkle Twinkle Little Star - Traditional Arrangement"
      style "Children's Folk Song"
      sections [
        {
          label "A Section"
          description "First melodic statement ('Twinkle twinkle little star, how I wonder what you are')"
          number_of_phrases 2
        }
        {
          label "B Section" 
          description "Middle contrasting section ('Up above the world so high, like a diamond in the sky')"
          number_of_phrases 2
        }
        {
          label "A' Section"
          description "Return to main melody ('Twinkle twinkle little star, how I wonder what you are')"
          number_of_phrases 2
        }
      ]
    }
  }
}
