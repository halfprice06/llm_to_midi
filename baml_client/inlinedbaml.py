###############################################################################
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml-py
#
###############################################################################

# This file was generated by BAML: please do not edit it. Instead, edit the
# BAML files and re-generate this code.
#
# ruff: noqa: E501,F401
# flake8: noqa: E501,F401
# pylint: disable=unused-import,line-too-long
# fmt: off

file_map = {
    
    "../c:\\Users\\danielp\\llm_to_midi\\baml_src\\clients.baml": "// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview\r\n\r\nclient<llm> OpenAIGPT45 {\r\n  provider openai\r\n  retry_policy Exponential\r\n\r\n  options {\r\n    temperature 1\r\n    model \"gpt-4.5-latest\"\r\n    api_key env.OPENAI_API_KEY\r\n\r\n  }\r\n}\r\n\r\nclient<llm> OpenAIo1 {\r\n  provider openai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"o1\"\r\n    reasoning_effort \"low\"\r\n    temperature 1\r\n    api_key env.OPENAI_API_KEY\r\n\r\n  }\r\n}\r\n\r\nclient<llm> OpenAIo1Mini {\r\n  provider openai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"o1-mini\"\r\n    temperature 1\r\n    api_key env.OPENAI_API_KEY\r\n\r\n  }\r\n\r\n}\r\n\r\nclient<llm> OpenAIo3Mini {\r\n  provider openai\r\n  retry_policy Exponential\r\n\r\n  options {\r\n    reasoning_effort \"low\"\r\n    model \"o3-mini\"\r\n    temperature 1\r\n    api_key env.OPENAI_API_KEY\r\n  }\r\n}\r\n\r\nclient<llm> OpenAIGPT4o {\r\n  provider openai\r\n  retry_policy Exponential\r\n\r\n  options {\r\n    temperature 1\r\n    model \"gpt-4o\"\r\n    api_key env.OPENAI_API_KEY\r\n\r\n  }\r\n}\r\n\r\nclient<llm> OpenAIGPT4oMini {\r\n  provider openai\r\n  retry_policy Exponential\r\n\r\n  options {\r\n    temperature 1\r\n    model \"gpt-4o-mini\"\r\n    api_key env.OPENAI_API_KEY\r\n\r\n  }\r\n}\r\n\r\n\r\nclient<llm> HyperbolicDeepseekReasoner {\r\n  provider openai-generic\r\n  retry_policy Exponential\r\n  options {\r\n    model deepseek-ai/DeepSeek-R1\r\n    api_key env.HYPERBOLIC_DEEPSEEK_API_KEY\r\n    base_url \"https://api.hyperbolic.xyz/v1/\"\r\n    default_role \"user\"\r\n    temperature 1\r\n\r\n  }\r\n}\r\n\r\nclient<llm> HyperbolicDeepseekV3 {\r\n  provider openai-generic\r\n  retry_policy Exponential\r\n  options {\r\n    model deepseek-ai/DeepSeek-V3\r\n    api_key env.HYPERBOLIC_DEEPSEEK_API_KEY\r\n    base_url \"https://api.hyperbolic.xyz/v1/\"\r\n    default_role \"user\"\r\n    temperature 1\r\n  }\r\n}\r\n\r\n\r\nclient<llm> DeepseekReasoner {\r\n  provider openai-generic\r\n  retry_policy Exponential\r\n  options {\r\n    model deepseek-reasoner\r\n    api_key env.DEEPSEEK_API_KEY\r\n    base_url \"https://api.deepseek.com\"\r\n    temperature 1\r\n\r\n  }\r\n}\r\n\r\n\r\nclient<llm> AnthropicSonnet35 {\r\n  provider anthropic\r\n  retry_policy Exponential\r\n  options {\r\n    model \"claude-3-5-sonnet-latest\"\r\n    api_key env.ANTHROPIC_API_KEY\r\n    temperature 1\r\n  }\r\n\r\n}\r\n\r\nclient<llm> AnthropicSonnet37 {\r\n  provider anthropic\r\n  retry_policy Exponential\r\n  options {\r\n    model \"claude-3-7-sonnet-latest\"\r\n    api_key env.ANTHROPIC_API_KEY\r\n    temperature 1\r\n  }\r\n\r\n}\r\n\r\nclient<llm> AnthropicOpus {\r\n  provider anthropic\r\n  retry_policy Exponential\r\n  options {\r\n    model \"claude-3-opus-latest\"\r\n    api_key env.ANTHROPIC_API_KEY\r\n    temperature 1\r\n  }\r\n}\r\n\r\nclient<llm> AnthropicHaiku {\r\n  provider anthropic\r\n  retry_policy Exponential\r\n  options {\r\n    model \"claude-3-5-haiku-latest\"\r\n    api_key env.ANTHROPIC_API_KEY\r\n    temperature 1\r\n  }\r\n}\r\n\r\nclient<llm> Gemini15Flash {\r\n  provider google-ai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"gemini-1.5-flash\"\r\n    api_key env.GOOGLE_API_KEY\r\n  }\r\n}\r\n\r\n\r\nclient<llm> Gemini15Pro {\r\n  provider google-ai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"gemini-1.5-pro\"\r\n    api_key env.GOOGLE_API_KEY\r\n  }\r\n}\r\n\r\n\r\nclient<llm> Gemini20FlashExp {\r\n  provider google-ai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"gemini-2.0-flash-exp\"\r\n    api_key env.GOOGLE_API_KEY\r\n  }\r\n}\r\n\r\n\r\nclient<llm> Gemini20FlashThinkingExp {\r\n  provider google-ai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"gemini-2.0-flash-thinking-exp-01-21\"\r\n    api_key env.GOOGLE_API_KEY\r\n  }\r\n\r\n}\r\n\r\nclient<llm> Gemini20Pro {\r\n  provider google-ai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"gemini-2.0-pro-exp-02-05\"\r\n    api_key env.GOOGLE_API_KEY\r\n  }\r\n\r\n}\r\n\r\n\r\n// https://docs.boundaryml.com/docs/snippets/clients/retry\r\nretry_policy Constant {\r\n  max_retries 3\r\n  // Strategy is optional\r\n  strategy {\r\n    type constant_delay\r\n    delay_ms 200\r\n  }\r\n}\r\n\r\nretry_policy Exponential {\r\n  max_retries 5\r\n  // Strategy is optional\r\n  strategy {\r\n    type exponential_backoff\r\n    delay_ms 300\r\n    mutliplier 1.5\r\n    max_delay_ms 10000\r\n  }\r\n}",
    "../c:\\Users\\danielp\\llm_to_midi\\baml_src\\generators.baml": "// This helps use auto generate libraries you can use in the language of\r\n// your choice. You can have multiple generators if you use multiple languages.\r\n// Just ensure that the output_dir is different for each generator.\r\ngenerator target {\r\n    // Valid values: \"python/pydantic\", \"typescript\", \"ruby/sorbet\", \"rest/openapi\"\r\n    output_type \"python/pydantic\"\r\n\r\n    // Where the generated code will be saved (relative to baml_src/)\r\n    output_dir \"../\"\r\n\r\n    // The version of the BAML package you have installed (e.g. same version as your baml-py or @boundaryml/baml).\r\n    // The BAML VSCode extension version should also match this version.\r\n    version \"0.77.0\"\r\n\r\n    // Valid values: \"sync\", \"async\"\r\n    // This controls what `b.FunctionName()` will be (sync or async).\r\n    default_client_mode sync\r\n}\r\n",
    "../c:\\Users\\danielp\\llm_to_midi\\baml_src\\midi.baml": "/////////////////////////////\r\n// Existing classes\r\n/////////////////////////////\r\n\r\n// Holds program numbers (0-127) for different voices\r\nclass Instrumentation {\r\n  bass int @description(\"Program number for bass voice\")\r\n  tenor int @description(\"Program number for tenor voice\")\r\n  alto int @description(\"Program number for alto voice\")\r\n  soprano int @description(\"Program number for soprano voice\")\r\n}\r\n\r\nclass SongMetadata {\r\n  title string @description(\"Creative title for the piece\")\r\n  tempo int @description(\"Recommended tempo in BPM\")\r\n  key_signature string @description(\"Key of the piece (e.g., 'C Major')\")\r\n  time_signature string @description(\"Time signature (e.g., '4/4')\")\r\n  instruments Instrumentation\r\n}\r\n\r\n/////////////////////////////\r\n// NEW: Flexible modular design\r\n/////////////////////////////\r\n\r\nclass SectionPlan {\r\n  label string @description(\"Label for this section, e.g., 'Intro', 'Verse', 'Chorus', Solo/Instrumental Break, Exposition, A, B, C, etc.\")\r\n  description string? @description(\"Textual description for the section's role in the piece. Convey the style techniques, rhythms, harmonies and/or feelings the section is meant to evoke.\")\r\n  number_of_phrases int @description(\"How many phrases are planned in this section.\")\r\n  measures_per_phrase int @description(\"Number of measures each phrase in this section should have\")\r\n  harmonic_direction string @description(\"A textual description of the harmonic structure of the section. This should include the key, the chords, and ideas about how the various parts should interact with each other.\")\r\n  rhythmic_direction string @description(\"A textual description of the rhythmic structure of the section. This should include the feel of the rhythm, the feel of the bass, the feel of the melody, the feel of the harmony, etc.\")\r\n  melodic_direction string @description(\"A textual description of the melodic structure of the section. This should include the feel of the melody, the feel of the bass, the feel of the harmony, etc.\")\r\n}\r\n\r\nclass CompositionPlan {\r\n  plan_title string @description(\"A short descriptive title for the composition plan.\")\r\n  style string? @description(\"Optional style or genre for the piece, e.g. 'classical waltz', 'jazz ballad', etc.\")\r\n  sections SectionPlan[] @description(\"A list of sections planned for the piece.\")\r\n}\r\n\r\nclass CompositionPlanWithMetadata {\r\n  plan CompositionPlan @description(\"The composition plan with sections and structure\")\r\n  metadata SongMetadata @description(\"The song metadata including title, tempo, key signature, time signature and instruments\")\r\n}\r\n\r\nclass NoteDuration {\r\n  note string? @description(\"For melodic parts (bass, tenor, alto, soprano, piano), the note name like 'C4', 'A#5', 'Bb3', etc. For percussion, the MIDI note number as a string, e.g., '35' for bass drum. Null indicates a rest.\")\r\n  duration string @description(\"Duration in beats, expressed as a fraction like '1/2', '1/3', '2', etc.\")\r\n}\r\n\r\nclass Beat {\r\n  harmony_description string @description(\"Harmony for this beat.\")\r\n  beat_counter string @description(\"Count of the current beat being written, starting at one  E.g., Beat 1 of 4\")\r\n  bass NoteDuration[] @description(\"Notes starting at this beat for bass. Leave empty [] when no new note starts.\")\r\n  tenor NoteDuration[] @description(\"Notes starting at this beat for tenor. Leave empty [] when no new note starts.\")\r\n  alto NoteDuration[] @description(\"Notes starting at this beat for alto. Leave empty [] when no new note starts.\")\r\n  soprano NoteDuration[] @description(\"Notes starting at this beat for soprano. Leave empty [] when no new note starts.\")\r\n  piano NoteDuration[] @description(\"Notes starting at this beat for piano. Leave empty [] when no new note starts.\")\r\n  percussion NoteDuration[]? @description(\"Optional percussion notes starting at this beat\")\r\n}\r\n\r\nclass Measure {\r\n  measure_counter string @description(\"Count of the current measure in this phrase, starting at one. E.g., Measure 1 of 8\")\r\n  harmony_plan_for_this_measure string @description(\"Describe how the harmony should develop over the beats of this measure.\")\r\n  beats Beat[] @description(\"List of beats in this measure. The number of beats should match the time signature.\")\r\n}\r\n\r\nclass Phrase {\r\n  phrase_counter string @description(\"Count of the current phrase in this section, starting at one. E.g., Phrase 1 of 2\")\r\n  phrase_label string @description(\"A musical phrase is a group of notes that create a musical idea. Phrases are similar to sentences in that they have a beginning and end, and they convey a specific meaning. In common practice (but not always), phrases are often four bars or measures long culminating in a more or less definite cadence.\")\r\n  phrase_description string @description(\"A textual description of the content of the phrase. The kind of chords, the shape of the melody, the intensity, the rhythms, etc.\")\r\n  lyrics string? @description(\"Optional lyrics for the phrase. If provided, the lyrics should be in the same language as the theme.\")\r\n  measures Measure[] @description(\"List of measures in this phrase. Must have exactly measures_per_phrase measures.\")\r\n}\r\n\r\nclass Section {\r\n  section_label string @description(\"Label for this section, e.g., 'Intro', 'Verse', 'Chorus', Solo/Instrumental Break, Exposition, A, B, C, etc.\")\r\n  section_description string @description(\"Textual description for the section's role in the piece. Convey the style techniques, rhythms, harmonies and/or feelings the section is meant to evoke.\")\r\n  harmonic_direction string @description(\"A textual description of the harmonic structure of the section. This should include the key, the chords, and ideas about how the various parts should interact with each other.\")\r\n  rhythmic_direction string @description(\"A textual description of the rhythmic structure of the section. This should include the feel of the rhythm, the feel of the bass, the feel of the melody, the feel of the harmony, etc.\")\r\n  melodic_direction string @description(\"A textual description of the melodic structure of the section. This should include the feel of the melody, the feel of the bass, the feel of the harmony, etc.\")\r\n  phrases Phrase[] @description(\"A list of phrases planned for this section.\")\r\n}\r\n\r\nclass ModularPiece {\r\n  metadata SongMetadata\r\n  sections Section[]\r\n}\r\n\r\n/////////////////////////////\r\n// Functions\r\n/////////////////////////////\r\n\r\nfunction GenerateCompositionPlan(theme: string) -> CompositionPlanWithMetadata {\r\n  client \"Gemini20Pro\"\r\n  prompt #\"\r\nYou are an expert music composer and theorist. The user wants to plan the structure of a piece\r\nBEFORE generating any actual note-level content.\r\n\r\n\r\nThey have asked for the following theme or instructions:\r\n\r\n\"{{ theme }}\"\r\n\r\nReturn a JSON object that follows the schema (CompositionPlanWithMetadata) exactly:\r\n{{ ctx.output_format }}\r\n\r\n\r\n\"#\r\n}\r\n\r\n// New function: GenerateOneSection\r\nfunction GenerateOneSection(\r\n  previousSections: Section[],\r\n  nextSectionPlan: SectionPlan,\r\n  overallPlan: CompositionPlanWithMetadata,\r\n  theme: string,\r\n  total_duration_per_phrase: float,\r\n  beats_per_measure: float\r\n) -> Section {\r\n  client \"Gemini20Pro\"\r\n  prompt #\"\r\nYou are an expert music composer well-versed in music theory. The user has already decided on the piece structure via the following plan:\r\n\r\n{{ overallPlan }}\r\n\r\nThe user also has requested the following theme:\r\n\\\"{{ theme }}\\\"\r\n\r\nSo far, we have completed the following sections:\r\n\r\n{{ previousSections }}\r\n\r\nNow, generate the **next section** according to the plan:\r\n\r\n{{ nextSectionPlan }}\r\n\r\nIMPORTANT REQUIREMENTS:\r\n\r\n- Do NOT include any comments in the JSON (no /* ... */).\r\n- Only generate this single next section (i.e. do not generate the entire piece or any other sections).\r\n- The new section must contain `phrases` with actual note-level detail in each part (bass, tenor, alto, soprano, piano, and optional percussion).\r\n- For the percussion field in each phrase:\r\n  - If you want percussion, include it as a non-empty list of NoteDuration objects\r\n  - If you don't want percussion, OMIT the field entirely (do not set it to null or empty list)\r\n- Each phrase must have exactly {{ nextSectionPlan.measures_per_phrase }} measures.\r\n- Each measure must contain notes for each voice (bass, tenor, alto, soprano, piano, and optionally percussion) summing to {{ beats_per_measure }} beats.\r\n- Total duration per voice in the phrase must be {{ total_duration_per_phrase }} beats.\r\n- Use fractional durations as strings (e.g., '1/2' for half a beat, '1/3' for a third of a beat) instead of decimal approximations. Do not use smaller than 1/16 notes.\r\n\r\n**When generating measures:**\r\n- Keep each measure self-contained; notes should not span across measures.\r\n- Durations must be strings representing fractions (e.g., '1/2', '1/3', '1'). Do not use smaller than 1/16 notes.\r\n- Ensure the total duration of each measure matches {{ beats_per_measure }} exactly.\r\n- For each measure, generate {{ beats_per_measure }} beats.\r\n- For each beat, specify the notes that start precisely at that beat for each voice.\r\n- Notes can have durations that extend beyond the beat or into subsequent measures, but they must not extend beyond the end of the phrase.\r\n- Leave empty [] when no new note starts.\r\n\r\nVoices:\r\n- bass\r\n- tenor\r\n- alto\r\n- soprano\r\n- piano (instrument #0)\r\n- percussion (channel 10) - optional, only include if it fits the genre and style\r\n\r\nInstruments:\r\n- Choose appropriate MIDI instruments for bass, tenor, alto, and soprano voices (from overallPlan.metadata.instruments).\r\n- Piano voice is always instrument 0 (Acoustic Grand Piano)\r\n- Percussion track uses General MIDI drum map note numbers on channel 10\r\n\r\nComposition Guidelines:\r\n- Use varied rhythms for each part\r\n- Keep each part coherent, with independent but harmonically compatible lines\r\n- Use good voice leading between parts, avoid parallel fifths and octaves\r\n- Write interesting motifs and follow rules of Western tonality and music theory\r\n- Ensure variety between phrases\r\n- Parts may rest at times to give other parts a chance to shine and the listeners ears a break\r\n- Use piano and/or percussion track to provide rhythmic foundation if appropriate for genre\r\n\r\nTechnical Requirements:\r\n- Each phrase must have a total duration of exactly {{ total_duration_per_phrase }} beats for each voice.\r\n- Ensure that the sum of the durations in each voice's note list (bass, tenor, alto, soprano, piano, and percussion if present) equals exactly {{ total_duration_per_phrase }}.\r\n- For example, if total_duration_per_phrase is 16.0, then each voice should have notes whose durations sum to 16.0 beats.\r\n- For melodic parts (bass, tenor, alto, soprano, piano), use note names in the format \"NoteOctave\", where Note is A, B, C, D, E, F, G, optionally followed by # for sharp or b for flat, and Octave is an integer from 0 to 9. For example, \"C4\" for middle C, \"A3\", \"G#5\", \"Bb2\", etc.\r\n- For percussion, use MIDI note numbers as strings, e.g., \"35\" for bass drum, \"38\" for snare, \"42\" for closed hi-hat, etc.\r\n- Use null to indicate a rest.\r\n- Duration is in beats (1/4 = quarter note, 1/8 = eighth note, 1/16 = sixteenth note. Don't go smaller.)\r\n- End long phrases with interesting cadences or long notes\r\n- Ensure variety of rhythms and counterpoint among voices, limit unison rhythms\r\n- Use piano to keep beat and add interest (e.g. arpeggiated chords)\r\n- Use percussion to enhance rhythm and groove, but only if it fits the genre\r\n- omit percussion for delicate pieces where it wouldn't fit (e.g. nocturne)\r\n- The metadata (title, tempo, key/time signatures) should be derived from the plan\r\n- Don't complain about the number of notes, just do your best.\r\n\r\nTitle, tempo, key, etc. are found in overallPlan or you can infer them from prior sections.\r\nBut do not repeat them here; just create the next section and its phrases.\r\n\r\n- THIS IS THE MOST IMPORTANT INSTRUCTION. ENSURE VARIETY OF RHYTHMS AND COUNTERPOINT AMONG VOICES, LIMIT UNISON RHYTHMS.\r\n\r\n- Return a JSON object matching the 'Section' schema exactly:\r\n{{ ctx.output_format }}\r\n\r\nDo not return any text other than the JSON object.\r\n\r\nMake sure to contrast busy sections or phrases with quieter ones.\r\n\r\nPlease make sure that you craft beautiful melodies that are memorable in and of themselves. There should be a clear melody and theme the listener remembers from each section. Don't meander.\r\n\r\nDon't forget:\r\n- Each phrase in this section must have exactly {{ nextSectionPlan.measures_per_phrase }} measures.\r\n- Each measure in this section must contain notes for each voice (bass, tenor, alto, soprano, piano, and optionally percussion) summing to {{ beats_per_measure }} beats.\r\n- Total duration per voice in the phrase in this section must be {{ total_duration_per_phrase }} beats.\r\n- Ensure the total duration of each measure in this section matches {{ beats_per_measure }} exactly.\r\n\"#\r\n}\r\n",
}

def get_baml_files():
    return file_map