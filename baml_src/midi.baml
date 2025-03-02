/////////////////////////////
// Existing classes
/////////////////////////////

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
  description string? @description("Textual description for the section's role in the piece. Convey the style techniques, rhythms, harmonies and/or feelings the section is meant to evoke.")
  number_of_phrases int @description("How many phrases are planned in this section.")
  measures_per_phrase int @description("Number of measures each phrase in this section should have")
  harmonic_direction string @description("A textual description of the harmonic structure of the section. This should include the key, the chords, and ideas about how the various parts should interact with each other.")
  rhythmic_direction string @description("A textual description of the rhythmic structure of the section. This should include the feel of the rhythm, the feel of the bass, the feel of the melody, the feel of the harmony, etc.")
  melodic_direction string @description("A textual description of the melodic structure of the section. This should include the feel of the melody, the feel of the bass, the feel of the harmony, etc.")
}

class CompositionPlan {
  plan_title string @description("A short descriptive title for the composition plan.")
  style string? @description("Optional style or genre for the piece, e.g. 'classical waltz', 'jazz ballad', etc.")
  sections SectionPlan[] @description("A list of sections planned for the piece.")
}

class CompositionPlanWithMetadata {
  plan CompositionPlan @description("The composition plan with sections and structure")
  metadata SongMetadata @description("The song metadata including title, tempo, key signature, time signature and instruments")
}

class NoteDuration {
  note int? @description("MIDI note number, null indicates a rest. For percussion (channel 10), this represents the drum/percussion instrument number.")
  duration string @description("Duration in beats, expressed as a fraction like '1/2', '1/3', '2', etc.")
}

class Beat {
  beat_counter string @description("Count of the current beat being written, starting at one  E.g.,Beat 1 of 4")
  bass NoteDuration[] @description("Notes starting at this beat for bass. Leave empty [] when no new note starts.")
  tenor NoteDuration[] @description("Notes starting at this beat for tenor. Leave empty [] when no new note starts.")
  alto NoteDuration[] @description("Notes starting at this beat for alto. Leave empty [] when no new note starts.")
  soprano NoteDuration[] @description("Notes starting at this beat for soprano. Leave empty [] when no new note starts.")
  piano NoteDuration[] @description("Notes starting at this beat for piano. Leave empty [] when no new note starts.")
  percussion NoteDuration[]? @description("Optional percussion notes starting at this beat")
}

class Measure {
  harmony_plan_for_this_measure string @description("Describe how the harmony should develop over the beats of this measure.")
  phrase_measure_number int @description("Measure number within the phrase, starting from 1")
  beats Beat[] @description("List of beats in this measure. The number of beats should match the time signature.")
}

class ModularPhrase {
  phrase_label string @description("A musical phrase is a group of notes that create a musical idea. Phrases are similar to sentences in that they have a beginning and end, and they convey a specific meaning. In common practice (but not always), phrases are often four bars or measures long culminating in a more or less definite cadence.")
  phrase_description string @description("A textual description of the content of the phrase. The kind of chords, the shape of the melody, the intensity, the rhythms, etc.")
  lyrics string? @description("Optional lyrics for the phrase. If provided, the lyrics should be in the same language as the theme.")
  measures Measure[] @description("List of measures in this phrase. Must have exactly measures_per_phrase measures.")
}

class ModularSection {
  section_label string @description("Label for this section, e.g., 'Intro', 'Verse', 'Chorus', Solo/Instrumental Break, Exposition, A, B, C, etc.")
  section_description string @description("Textual description for the section's role in the piece. Convey the style techniques, rhythms, harmonies and/or feelings the section is meant to evoke.")
  harmonic_direction string @description("A textual description of the harmonic structure of the section. This should include the key, the chords, and ideas about how the various parts should interact with each other.")
  rhythmic_direction string @description("A textual description of the rhythmic structure of the section. This should include the feel of the rhythm, the feel of the bass, the feel of the melody, the feel of the harmony, etc.")
  melodic_direction string @description("A textual description of the melodic structure of the section. This should include the feel of the melody, the feel of the bass, the feel of the harmony, etc.")
  phrases ModularPhrase[] @description("A list of phrases planned for this section.")
}

class ModularPiece {
  metadata SongMetadata
  sections ModularSection[]
}

/////////////////////////////
// Functions
/////////////////////////////

function GenerateCompositionPlan(theme: string) -> CompositionPlanWithMetadata {
  client "Gemini20Pro"
  prompt #"
You are an expert music composer and theorist. The user wants to plan the structure of a piece
BEFORE generating any actual note-level content.


They have asked for the following theme or instructions:

"{{ theme }}"

Return a JSON object that follows the schema (CompositionPlanWithMetadata) exactly:
{{ ctx.output_format }}


"#
}

// New function: GenerateOneSection
function GenerateOneSection(
  previousSections: ModularSection[],
  nextSectionPlan: SectionPlan,
  overallPlan: CompositionPlanWithMetadata,
  theme: string,
  total_duration_per_phrase: float,
  beats_per_measure: float
) -> ModularSection {
  client "Gemini20Pro"
  prompt #"
You are an expert music composer well-versed in music theory. The user has already decided on the piece structure via the following plan:

{{ overallPlan }}

The user also has requested the following theme:
\"{{ theme }}\"

So far, we have completed the following sections:

{{ previousSections }}

Now, generate the **next section** according to the plan:

{{ nextSectionPlan }}

IMPORTANT REQUIREMENTS:

- Do NOT include any comments in the JSON (no /* ... */).
- Only generate this single next section (i.e. do not generate the entire piece or any other sections).
- The new section must contain `phrases` with actual note-level detail in each part (bass, tenor, alto, soprano, piano, and optional percussion).
- For the percussion field in each phrase:
  - If you want percussion, include it as a non-empty list of NoteDuration objects
  - If you don't want percussion, OMIT the field entirely (do not set it to null or empty list)
- Each phrase must have exactly {{ nextSectionPlan.measures_per_phrase }} measures.
- Each measure must contain notes for each voice (bass, tenor, alto, soprano, piano, and optionally percussion) summing to {{ beats_per_measure }} beats.
- Total duration per voice in the phrase must be {{ total_duration_per_phrase }} beats.
- Use fractional durations as strings (e.g., '1/2' for half a beat, '1/3' for a third of a beat) instead of decimal approximations. Do not use smaller than 1/16 notes.

**When generating measures:**
- Keep each measure self-contained; notes should not span across measures.
- Durations must be strings representing fractions (e.g., '1/2', '1/3', '1'). Do not use smaller than 1/16 notes.
- Ensure the total duration of each measure matches {{ beats_per_measure }} exactly.
- For each measure, generate {{ beats_per_measure }} beats.
- For each beat, specify the notes that start precisely at that beat for each voice.
- Notes can have durations that extend beyond the beat or into subsequent measures, but they must not extend beyond the end of the phrase.
- Leave empty [] when no new note starts. 

Voices:
- bass
- tenor
- alto
- soprano
- piano (instrument #0)
- percussion (channel 10) - optional, only include if it fits the genre and style

Instruments:
- Choose appropriate MIDI instruments for bass, tenor, alto, and soprano voices (from overallPlan.metadata.instruments).
- Piano voice is always instrument 0 (Acoustic Grand Piano)
- Percussion track uses General MIDI drum map note numbers on channel 10

Composition Guidelines:
- Use varied rhythms for each part
- Keep each part coherent, with independent but harmonically compatible lines
- Use good voice leading between parts, avoid parallel fifths and octaves
- Write interesting motifs and follow rules of Western tonality and music theory
- Ensure variety between phrases
- Parts may rest at times to give other parts a chance to shine and the listeners ears a break
- Use piano and/or percussion track to provide rhythmic foundation if appropriate for genre

Technical Requirements:
- Each phrase must have a total duration of exactly {{ total_duration_per_phrase }} beats for each voice.
- Ensure that the sum of the durations in each voice's note list (bass, tenor, alto, soprano, piano, and percussion if present) equals exactly {{ total_duration_per_phrase }}.
- For example, if total_duration_per_phrase is 16.0, then each voice should have notes whose durations sum to 16.0 beats.
- Use MIDI note numbers:
  - For melodic parts (60 = middle C)
  - For percussion (35 = bass drum, 38 = snare, 42 = closed hi-hat, etc.)
  - null indicates a rest
- Duration is in beats (1/4 = quarter note, 1/8 = eighth note, 1/16 = sixteenth note. Don't go smaller.)
- End long phrases with interesting cadences or long notes
- Ensure variety of rhythms and counterpoint among voices, limit unison rhythms
- Use piano to keep beat and add interest (e.g. arpeggiated chords)
- Use percussion to enhance rhythm and groove, but only if it fits the genre
- Omit percussion for delicate pieces where it wouldn't fit (e.g. nocturne)
- The metadata (title, tempo, key/time signatures) should be derived from the plan
- Don't complain about the number of notes, just do your best.

Title, tempo, key, etc. are found in overallPlan or you can infer them from prior sections. 
But do not repeat them here; just create the next section and its phrases.

- THIS IS THE MOST IMPORTANT INSTRUCTION. ENSURE VARIETY OF RHYTHMS AND COUNTERPOINT AMONG VOICES, LIMIT UNISON RHYTHMS.

- Return a JSON object matching the 'ModularSection' schema exactly:
{{ ctx.output_format }}

Do not return any text other than the JSON object.

Make sure to contrast busy sections or phrases with quieter ones.

Please make sure that you craft beautiful melodies that are memorable in and of themselves. There should be a clear melody and theme the listener remembers from each section. Don't meander.

Don't forget: 

- Each phrase in this section must have exactly {{ nextSectionPlan.measures_per_phrase }} measures.
- Each measure in this section must contain notes for each voice (bass, tenor, alto, soprano, piano, and optionally percussion) summing to {{ beats_per_measure }} beats.
- Total duration per voice in the phrase in this section must be {{ total_duration_per_phrase }} beats.
- Ensure the total duration of each measure in this section matches {{ beats_per_measure }} exactly.

"#
}
