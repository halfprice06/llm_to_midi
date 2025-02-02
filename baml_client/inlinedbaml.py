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
    "../c:\\Users\\danielp\\llm_to_midi\\baml_src\\midi.baml": "/////////////////////////////\n// Existing classes\n/////////////////////////////\n\n// Represents the duration and pitch of a musical note\nclass NoteDuration {\n  note int? @description(\"MIDI note number, null indicates a rest. For percussion (channel 10), this represents the drum/percussion instrument number.\")\n  duration float @description(\"Duration in beats\")\n}\n\n// Holds program numbers (0-127) for different voices\nclass Instrumentation {\n  bass int @description(\"Program number for bass voice\")\n  tenor int @description(\"Program number for tenor voice\")\n  alto int @description(\"Program number for alto voice\")\n  soprano int @description(\"Program number for soprano voice\")\n}\n\nclass SongMetadata {\n  title string @description(\"Creative title for the piece\")\n  tempo int @description(\"Recommended tempo in BPM\")\n  key_signature string @description(\"Key of the piece (e.g., 'C Major')\")\n  time_signature string @description(\"Time signature (e.g., '4/4')\")\n  instruments Instrumentation\n}\n\n/////////////////////////////\n// NEW: Flexible modular design\n/////////////////////////////\n\n\nclass SectionPlan {\n  label string @description(\"Label for this section, e.g., 'Intro', 'Verse', 'Chorus', Solo/Instrumental Break, Exposition, A, B, C, etc.\")\n  description string? @description(\"Textual description for the section's role in the piece.\")\n  number_of_phrases int @description(\"How many phrases are planned in this section.\")\n}\n\nclass CompositionPlan {\n  plan_title string @description(\"A short descriptive title for the composition plan.\")\n  style string? @description(\"Optional style or genre for the piece, e.g. 'classical waltz', 'jazz ballad', etc.\")\n  sections SectionPlan[] @description(\"A list of sections planned for the piece.\")\n}\n\nclass ModularPhrase {\n  phrase_label string\n  bass NoteDuration[]\n  tenor NoteDuration[]\n  alto NoteDuration[]\n  soprano NoteDuration[]\n  piano NoteDuration[]\n  percussion NoteDuration[]?\n}\n\nclass ModularSection {\n  section_label string\n  phrases ModularPhrase[]\n}\n\nclass ModularPiece {\n  metadata SongMetadata\n  sections ModularSection[]\n}\n\nfunction GenerateCompositionPlan(theme: string) -> CompositionPlan {\n  client \"OpenAIo1\"\n  prompt #\"\nYou are an expert music composer. The user wants to plan the structure of a piece\nBEFORE generating any actual note-level content.\n\nThey have asked for the following theme or instructions:\n{{ theme }}\n\nReturn a JSON object that follows the schema (CompositionPlan) exactly:\n{{ ctx.output_format }}\n\nGuidelines for plan:\n- Provide a plan title (plan_title).\n- Optionally specify a style or genre (style).\n- Provide a list of sections, each with a label, optional description, and how many phrases it should have.\n- The user wants to see the piece broken into any structure you see fit (intro, verse, chorus, coda, etc.).\n- Only describe the plan; do NOT generate note-level detail at this step.\n\"#\n}\n\nfunction GenerateModularSong(plan: CompositionPlan) -> ModularPiece {\n  client \"OpenAIo1\"\n  prompt #\"\nYou are an expert composer. A user has already decided on the piece structure (sections, phrases) via the following plan:\n{{ plan }}\n\nNow please fill in the actual note-level content for each section and each phrase.\n\nRequirements / guidelines:\n- Each section in 'plan.sections' must appear in the final output with a matching label.\n- For each planned phrase, generate enough note-level detail in the voices (bass, tenor, alto, soprano, piano, and optionally percussion).\n- The final output must match the 'ModularPiece' schema exactly:\n\n{{ ctx.output_format }}\n\nNotes:\n- Use valid MIDI note numbers (0..127), or null for rests.\n- For percussion (channel 10), use the typical GM drum note numbers (35, 36, 38, 42, etc.) if applicable.\n- The 'metadata' can be guessed or derived from the plan. Provide a creative title, a tempo, a key signature, time signature, etc.\n- The user wants a cohesive piece but with the plan's structure.\n\"#\n}\n\ntest GenerateCompositionPlan {\n  functions [GenerateCompositionPlan]\n  args {\n    theme #\"\n      Write Twinkle Twinkle Little Star in C\n    \"#\n  }\n}\n\ntest GenerateModularSong {\n  functions [GenerateModularSong]\n  args {\n    plan {\n      plan_title \"Twinkle Twinkle Little Star - Traditional Arrangement\"\n      style \"Children's Folk Song\"\n      sections [\n        {\n          label \"A Section\"\n          description \"First melodic statement ('Twinkle twinkle little star, how I wonder what you are')\"\n          number_of_phrases 2\n        }\n        {\n          label \"B Section\" \n          description \"Middle contrasting section ('Up above the world so high, like a diamond in the sky')\"\n          number_of_phrases 2\n        }\n        {\n          label \"A' Section\"\n          description \"Return to main melody ('Twinkle twinkle little star, how I wonder what you are')\"\n          number_of_phrases 2\n        }\n      ]\n    }\n  }\n}\n",
}

def get_baml_files():
    return file_map