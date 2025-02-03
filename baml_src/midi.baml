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
  phrase_label string @description("A musical phrase is a group of notes that create a musical idea. Phrases are similar to sentences in that they have a beginning and end, and they convey a specific meaning. In common practice (but not always), phrases are often four bars or measures long culminating in a more or less definite cadence.")
  lyrics string? @description("Optional lyrics for the phrase. If provided, the lyrics should be in the same language as the theme.")
  bass NoteDuration[] @description("Bass line - typically provides harmonic foundation with slower rhythmic movement, often using root notes and fifths")
  tenor NoteDuration[] @description("Tenor voice - provides inner harmony, can move in parallel or contrary motion with other voices, often harmonizes with alto")
  alto NoteDuration[] @description("Alto voice - middle voice that helps fill out harmonies, frequently moves in parallel thirds with soprano or tenor")
  soprano NoteDuration[] @description("Soprano/lead voice - carries the main melody, typically has the highest pitch and most prominent melodic movement")
  piano NoteDuration[] @description("Piano part - can provide harmonic support, melodic lines, or both through a combination of chords and melodic passages. Arpeggios work well here.")
  percussion NoteDuration[]? @description("Optional percussion track (channel 10) - uses General MIDI drum map note numbers for rhythmic accompaniment")
}

class ModularSection {
  section_label string @description("Label for this section, e.g., 'Intro', 'Verse', 'Chorus', Solo/Instrumental Break, Exposition, A, B, C, etc.")
  section_description string @description("Textual description for the section's role in the piece.")
  phrases ModularPhrase[] @description("A list of phrases planned for this section.")
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

"{{ theme }}"

Return a JSON object that follows the schema (CompositionPlan) exactly:
{{ ctx.output_format }}

Guidelines for plan:
- Provide a plan title (plan_title).
- Specify a style or genre (style).
- Provide a list of sections, each with a label, description, and how many phrases it should have.
- The user wants to see the piece broken into any structure you see fit (intro, verse, chorus, coda, etc.).
- Only describe the plan; do NOT generate note-level detail at this step.
"#
}

function GenerateModularSong(plan: CompositionPlan, theme: string) -> ModularPiece {
  client "OpenAIo1"
  prompt #"
You are an expert composer well-versed in music theory. The user has already decided on the piece structure (sections, phrases) via the following plan:

{{ plan }}

The user has also provided the following theme or instructions:

"{{ theme }}"

Now please fill in the actual note-level content for each section and each phrase.

Form:
- Each section in 'plan.sections' must appear in the final output with a matching label
- Follow the modular composition plan exactly
- The final output must match the 'ModularPiece' schema:

IMPORTANT OUTPUT REQUIREMENTS:
- DO NOT include any comments in the output JSON (no /* ... */ style comments)
- The output must be valid JSON that can be parsed directly

Voices:
- bass
- tenor
- alto
- soprano 
- piano
- percussion (channel 10) - optional, only include if it fits the genre and style

Instruments:
- Choose appropriate MIDI instruments for bass, tenor, alto, and soprano voices
- Piano voice is always instrument 0 (Acoustic Grand Piano)
- Percussion track uses General MIDI drum map note numbers on channel 10

Phrases:
- A musical phrase is a series of many notes that create a musical idea. Phrases are similar to sentences in that they have a beginning and end, and they convey a specific meaning. In common practice phrases are often four bars or measures long culminating in a more or less definite cadence.

Composition Guidelines:
- Use varied rhythms for each part
- Keep each part coherent, with independent but harmonically compatible lines
- Use good voice leading between parts, avoid parallel fifths and octaves
- Write interesting motifs and follow rules of Western tonality and music theory
- Ensure variety between phrases
- Parts may rest at times to give other parts a chance to shine and the listeners ears a break
- Use piano and/or percussion track to provide rhythmic foundation if appropriate for genre

Technical Requirements:
- Make phrases extremely long and interesting
- Use MIDI note numbers:
  - For melodic parts (60 = middle C)
  - For percussion (35 = bass drum, 38 = snare, 42 = closed hi-hat, etc.)
  - null indicates a rest
- Duration is in beats (1.0 = quarter note, 0.5 = eighth note, 0.25 = sixteenth note, 0.125 = thirty-second note, etc.)
- End long phrases with interesting cadences or long notes
- Ensure variety of rhythms and counterpoint among voices, limit unison rhythms
- Use piano to keep beat and add interest (e.g. arpeggiated chords)
- Use percussion to enhance rhythm and groove, but only if it fits the genre
- Omit percussion for delicate pieces where it wouldn't fit (e.g. nocturne)
- The metadata (title, tempo, key/time signatures) should be derived from the plan
- Don't complain about the number of notes, just do your best.

Remember to write a cohesive piece that follows the plan's structure. Do not complain about the number of notes - just do your best to create an interesting and musically sound composition.

- THIS IS THE MOST IMPORTANT INSTRUCTION. ENSURE VARIETY OF RHYTHMS AND COUNTERPOINT AMONG VOICES, LIMIT UNISON RHYTHMS.

Output Format:

{{ ctx.output_format }}

Do not return any commentary before or after the JSON output, only the JSON.
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
