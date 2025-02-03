###############################################################################
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml
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
    
    "../c:\\Users\\danielp\\llm_to_midi\\baml_src\\clients.baml": "// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview\r\n\r\nclient<llm> OpenAIo1 {\r\n  provider openai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"o1\"\r\n    reasoning_effort \"high\"\r\n    temperature 1\r\n    api_key env.OPENAI_API_KEY\r\n\r\n  }\r\n}\r\n\r\nclient<llm> OpenAIo1Mini {\r\n  provider openai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"o1-mini\"\r\n    temperature 1\r\n    api_key env.OPENAI_API_KEY\r\n\r\n  }\r\n\r\n}\r\n\r\nclient<llm> OpenAIo3Mini {\r\n  provider openai\r\n  retry_policy Exponential\r\n\r\n  options {\r\n    reasoning_effort \"high\"\r\n    model \"o3-mini\"\r\n    temperature 1\r\n    api_key env.OPENAI_API_KEY\r\n  }\r\n}\r\n\r\nclient<llm> OpenAIGPT4o {\r\n  provider openai\r\n  retry_policy Exponential\r\n\r\n  options {\r\n    temperature 1\r\n    model \"gpt-4o\"\r\n    api_key env.OPENAI_API_KEY\r\n\r\n  }\r\n}\r\n\r\n\r\nclient<llm> HyperbolicDeepseekReasoner {\r\n  provider openai-generic\r\n  retry_policy Exponential\r\n  options {\r\n    model deepseek-ai/DeepSeek-R1\r\n    api_key env.HYPERBOLIC_DEEPSEEK_API_KEY\r\n    base_url \"https://api.hyperbolic.xyz/v1/\"\r\n    default_role \"user\"\r\n    temperature 1\r\n\r\n  }\r\n}\r\n\r\nclient<llm> HyperbolicDeepseekV3 {\r\n  provider openai-generic\r\n  retry_policy Exponential\r\n  options {\r\n    model deepseek-ai/DeepSeek-V3\r\n    api_key env.HYPERBOLIC_DEEPSEEK_API_KEY\r\n    base_url \"https://api.hyperbolic.xyz/v1/\"\r\n    default_role \"user\"\r\n    temperature 1\r\n  }\r\n}\r\n\r\n\r\nclient<llm> DeepseekReasoner {\r\n  provider openai-generic\r\n  retry_policy Exponential\r\n  options {\r\n    model deepseek-reasoner\r\n    api_key env.DEEPSEEK_API_KEY\r\n    base_url \"https://api.deepseek.com\"\r\n    temperature 1\r\n\r\n  }\r\n}\r\n\r\n\r\nclient<llm> AnthropicSonnet {\r\n  provider anthropic\r\n  retry_policy Exponential\r\n  options {\r\n    model \"claude-3-5-sonnet-latest\"\r\n    api_key env.ANTHROPIC_API_KEY\r\n    temperature 1\r\n  }\r\n\r\n}\r\n\r\nclient<llm> AnthropicOpus {\r\n  provider anthropic\r\n  retry_policy Exponential\r\n  options {\r\n    model \"claude-3-opus-latest\"\r\n    api_key env.ANTHROPIC_API_KEY\r\n    temperature 1\r\n  }\r\n}\r\n\r\nclient<llm> AnthropicHaiku {\r\n  provider anthropic\r\n  retry_policy Exponential\r\n  options {\r\n    model \"claude-3-5-haiku-latest\"\r\n    api_key env.ANTHROPIC_API_KEY\r\n    temperature 1\r\n  }\r\n}\r\n\r\nclient<llm> Gemini15Flash {\r\n  provider google-ai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"gemini-1.5-flash\"\r\n    api_key env.GOOGLE_API_KEY\r\n  }\r\n}\r\n\r\n\r\nclient<llm> Gemini15Pro {\r\n  provider google-ai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"gemini-1.5-pro\"\r\n    api_key env.GOOGLE_API_KEY\r\n  }\r\n}\r\n\r\n\r\nclient<llm> Gemini20FlashExp {\r\n  provider google-ai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"gemini-2.0-flash-exp\"\r\n    api_key env.GOOGLE_API_KEY\r\n  }\r\n}\r\n\r\n\r\nclient<llm> Gemini20FlashThinkingExp {\r\n  provider google-ai\r\n  retry_policy Exponential\r\n  options {\r\n    model \"gemini-2.0-flash-thinking-exp-01-21\"\r\n    api_key env.GOOGLE_API_KEY\r\n  }\r\n\r\n}\r\n\r\n\r\n// https://docs.boundaryml.com/docs/snippets/clients/retry\r\nretry_policy Constant {\r\n  max_retries 3\r\n  // Strategy is optional\r\n  strategy {\r\n    type constant_delay\r\n    delay_ms 200\r\n  }\r\n}\r\n\r\nretry_policy Exponential {\r\n  max_retries 2\r\n  // Strategy is optional\r\n  strategy {\r\n    type exponential_backoff\r\n    delay_ms 300\r\n    mutliplier 1.5\r\n    max_delay_ms 10000\r\n  }\r\n}",
    "../c:\\Users\\danielp\\llm_to_midi\\baml_src\\generators.baml": "// This helps use auto generate libraries you can use in the language of\n// your choice. You can have multiple generators if you use multiple languages.\n// Just ensure that the output_dir is different for each generator.\ngenerator target {\n    // Valid values: \"python/pydantic\", \"typescript\", \"ruby/sorbet\", \"rest/openapi\"\n    output_type \"python/pydantic\"\n\n    // Where the generated code will be saved (relative to baml_src/)\n    output_dir \"../\"\n\n    // The version of the BAML package you have installed (e.g. same version as your baml-py or @boundaryml/baml).\n    // The BAML VSCode extension version should also match this version.\n    version \"0.74.0\"\n\n    // Valid values: \"sync\", \"async\"\n    // This controls what `b.FunctionName()` will be (sync or async).\n    default_client_mode sync\n}\n",
    "../c:\\Users\\danielp\\llm_to_midi\\baml_src\\midi.baml": "/////////////////////////////\r\n// Existing classes\r\n/////////////////////////////\r\n\r\n// Represents the duration and pitch of a musical note\r\nclass NoteDuration {\r\n  note int? @description(\"MIDI note number, null indicates a rest. For percussion (channel 10), this represents the drum/percussion instrument number.\")\r\n  duration float @description(\"Duration in beats\")\r\n}\r\n\r\n// Holds program numbers (0-127) for different voices\r\nclass Instrumentation {\r\n  bass int @description(\"Program number for bass voice\")\r\n  tenor int @description(\"Program number for tenor voice\")\r\n  alto int @description(\"Program number for alto voice\")\r\n  soprano int @description(\"Program number for soprano voice\")\r\n}\r\n\r\nclass SongMetadata {\r\n  title string @description(\"Creative title for the piece\")\r\n  tempo int @description(\"Recommended tempo in BPM\")\r\n  key_signature string @description(\"Key of the piece (e.g., 'C Major')\")\r\n  time_signature string @description(\"Time signature (e.g., '4/4')\")\r\n  instruments Instrumentation\r\n}\r\n\r\n/////////////////////////////\r\n// NEW: Flexible modular design\r\n/////////////////////////////\r\n\r\n\r\nclass SectionPlan {\r\n  label string @description(\"Label for this section, e.g., 'Intro', 'Verse', 'Chorus', Solo/Instrumental Break, Exposition, A, B, C, etc.\")\r\n  description string? @description(\"Textual description for the section's role in the piece. Convey the style techniques, rhythms, harmonies and/or feelings the section is meant to evoke.\")\r\n  number_of_phrases int @description(\"How many phrases are planned in this section.\")\r\n  harmonic_direction string @description(\"A textual description of the harmonic structure of the section. This should include the key, the chords, and ideas about how the various parts should interact with each other.\")\r\n  rhythmic_direction string @description(\"A textual description of the rhythmic structure of the section. This should include the feel of the rhythm, the feel of the bass, the feel of the melody, the feel of the harmony, etc.\")\r\n  melodic_direction string @description(\"A textual description of the melodic structure of the section. This should include the feel of the melody, the feel of the bass, the feel of the harmony, etc.\")\r\n}\r\n\r\nclass CompositionPlan {\r\n  plan_title string @description(\"A short descriptive title for the composition plan.\")\r\n  style string? @description(\"Optional style or genre for the piece, e.g. 'classical waltz', 'jazz ballad', etc.\")\r\n  sections SectionPlan[] @description(\"A list of sections planned for the piece.\")\r\n}\r\n\r\nclass CompositionPlanWithMetadata {\r\n  plan CompositionPlan @description(\"The composition plan with sections and structure\")\r\n  metadata SongMetadata @description(\"The song metadata including title, tempo, key signature, time signature and instruments\")\r\n}\r\n\r\nclass ModularPhrase {\r\n  phrase_label string @description(\"A musical phrase is a group of notes that create a musical idea. Phrases are similar to sentences in that they have a beginning and end, and they convey a specific meaning. In common practice (but not always), phrases are often four bars or measures long culminating in a more or less definite cadence.\")\r\n  phrase_description string @description(\"A textual description of the content of the phrase. The kind of chords, the shape of the melody, the intensity, the rhythms, etc.\")\r\n  lyrics string? @description(\"Optional lyrics for the phrase. If provided, the lyrics should be in the same language as the theme.\")\r\n  bass NoteDuration[] @description(\"Bass line - typically provides harmonic foundation with slower rhythmic movement, often using root notes and fifths\")\r\n  tenor NoteDuration[] @description(\"Tenor voice - provides inner harmony, can move in parallel or contrary motion with other voices, often harmonizes with alto\")\r\n  alto NoteDuration[] @description(\"Alto voice - middle voice that helps fill out harmonies, frequently moves in parallel thirds with soprano or tenor\")\r\n  soprano NoteDuration[] @description(\"Soprano/lead voice - carries the main melody, typically has the highest pitch and most prominent melodic movement\")\r\n  piano NoteDuration[] @description(\"Piano part - can provide harmonic support, melodic lines, or both through a combination of chords and melodic passages. Arpeggios work well here.\")\r\n  percussion NoteDuration[]? @description(\"Optional percussion track (channel 10) - uses General MIDI drum map note numbers for rhythmic accompaniment\")\r\n}\r\n\r\nclass ModularSection {\r\n  section_label string @description(\"Label for this section, e.g., 'Intro', 'Verse', 'Chorus', Solo/Instrumental Break, Exposition, A, B, C, etc.\")\r\n  section_description string @description(\"Textual description for the section's role in the piece. Convey the style techniques, rhythms, harmonies and/or feelings the section is meant to evoke.\")\r\n  harmonic_direction string @description(\"A textual description of the harmonic structure of the section. This should include the key, the chords, and ideas about how the various parts should interact with each other.\")\r\n  rhythmic_direction string @description(\"A textual description of the rhythmic structure of the section. This should include the feel of the rhythm, the feel of the bass, the feel of the melody, the feel of the harmony, etc.\")\r\n  melodic_direction string @description(\"A textual description of the melodic structure of the section. This should include the feel of the melody, the feel of the bass, the feel of the harmony, etc.\")\r\n  phrases ModularPhrase[] @description(\"A list of phrases planned for this section.\")\r\n}\r\n\r\nclass ModularPiece {\r\n  metadata SongMetadata\r\n  sections ModularSection[]\r\n}\r\n\r\n/////////////////////////////\r\n// Functions\r\n/////////////////////////////\r\n\r\nfunction GenerateCompositionPlan(theme: string) -> CompositionPlanWithMetadata {\r\n  client \"AnthropicSonnet\"\r\n  prompt #\"\r\nYou are an expert music composer and theorist. The user wants to plan the structure of a piece\r\nBEFORE generating any actual note-level content.\r\n\r\n\r\nThey have asked for the following theme or instructions:\r\n\r\n\"{{ theme }}\"\r\n\r\nReturn a JSON object that follows the schema (CompositionPlanWithMetadata) exactly:\r\n{{ ctx.output_format }}\r\n\r\n\r\n\"#\r\n}\r\n\r\n\r\n// New function: GenerateOneSection\r\nfunction GenerateOneSection(\r\n  previousSections: ModularSection[],\r\n  nextSectionPlan: SectionPlan,\r\n  overallPlan: CompositionPlanWithMetadata,\r\n  theme: string\r\n) -> ModularSection {\r\n  client \"AnthropicSonnet\"\r\n  prompt #\"\r\nYou are an expert music composer well-versed in music theory. The user has already decided on the piece structure via the following plan:\r\n\r\n{{ overallPlan }}\r\n\r\nThe user also has requested the following theme:\r\n\\\"{{ theme }}\\\"\r\n\r\nSo far, we have completed the following sections:\r\n\r\n{{ previousSections }}\r\n\r\nNow, generate the **next section** according to the plan:\r\n\r\n{{ nextSectionPlan }}\r\n\r\nIMPORTANT REQUIREMENTS:\r\n\r\n- Do NOT include any comments in the JSON (no /* ... */).\r\n- Only generate this single next section (i.e. do not generate the entire piece or any other sections).\r\n- The new section must contain `phrases` with actual note-level detail in each part (bass, tenor, alto, soprano, piano, and optional percussion).\r\n- For the percussion field in each phrase:\r\n  - If you want percussion, include it as a non-empty list of NoteDuration objects\r\n  - If you don't want percussion, OMIT the field entirely (do not set it to null or empty list)\r\n\r\nVoices:\r\n- bass\r\n- tenor\r\n- alto\r\n- soprano\r\n- piano (instrument #0)\r\n- percussion (channel 10) - optional, only include if it fits the genre and style\r\n\r\nInstruments:\r\n- Choose appropriate MIDI instruments for bass, tenor, alto, and soprano voices\r\n- Piano voice is always instrument 0 (Acoustic Grand Piano)\r\n- Percussion track uses General MIDI drum map note numbers on channel 10\r\n\r\nComposition Guidelines:\r\n- Use varied rhythms for each part\r\n- Keep each part coherent, with independent but harmonically compatible lines\r\n- Use good voice leading between parts, avoid parallel fifths and octaves\r\n- Write interesting motifs and follow rules of Western tonality and music theory\r\n- Ensure variety between phrases\r\n- Parts may rest at times to give other parts a chance to shine and the listeners ears a break\r\n- Use piano and/or percussion track to provide rhythmic foundation if appropriate for genre\r\n\r\nTechnical Requirements:\r\n- Make phrases extremely long and interesting\r\n- Use MIDI note numbers:\r\n  - For melodic parts (60 = middle C)\r\n  - For percussion (35 = bass drum, 38 = snare, 42 = closed hi-hat, etc.)\r\n  - null indicates a rest\r\n- Duration is in beats (1.0 = quarter note, 0.5 = eighth note, 0.25 = sixteenth note, 0.125 = thirty-second note, etc.)\r\n- End long phrases with interesting cadences or long notes\r\n- Ensure variety of rhythms and counterpoint among voices, limit unison rhythms\r\n- Use piano to keep beat and add interest (e.g. arpeggiated chords)\r\n- Use percussion to enhance rhythm and groove, but only if it fits the genre\r\n- Omit percussion for delicate pieces where it wouldn't fit (e.g. nocturne)\r\n- The metadata (title, tempo, key/time signatures) should be derived from the plan\r\n- Don't complain about the number of notes, just do your best.\r\n\r\nTitle, tempo, key, etc. are found in overallPlan or you can infer them from prior sections. \r\nBut do not repeat them here; just create the next section and its phrases.\r\n\r\n- THIS IS THE MOST IMPORTANT INSTRUCTION. ENSURE VARIETY OF RHYTHMS AND COUNTERPOINT AMONG VOICES, LIMIT UNISON RHYTHMS.\r\n\r\n- Return a JSON object matching the 'ModularSection' schema exactly:\r\n{{ ctx.output_format }}\r\n\r\nDo not return any text other than the JSON object.\r\n\r\nMake sure to contrast busy sections or phrases with quieter ones.\r\n\r\nPlease make sure that you craft beautiful melodies that are memorable in and of themselves. There should be a clear melody and theme the listener remembers from each section. Don't meander.\r\n\r\n\"#\r\n}\r\n\r\n",
}

def get_baml_files():
    return file_map