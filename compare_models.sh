#!/bin/bash
# Compare Models - A simple script to demonstrate the multiple model generation feature

echo "LLM to MIDI - Model Comparison Script"
echo "========================================="
echo
echo "This script will generate music using all available models with the same theme."
echo "The models will run concurrently to save time."
echo

python main.py --models "OpenAIGPT45,OpenAIo1,OpenAIo1Mini,OpenAIo3Mini,OpenAIGPT4o,OpenAIGPT4oMini,HyperbolicDeepseekReasoner,HyperbolicDeepseekV3,AnthropicSonnet35,AnthropicSonnet37,AnthropicOpus,AnthropicHaiku,Gemini15Flash,Gemini15Pro,Gemini20FlashExp,Gemini20FlashThinkingExp,Gemini20Pro" --theme "A single phrase test theme." --concurrent

echo
echo "All models have completed. Check the outputs folder for the generated MIDI files."
echo "Each filename includes the model name that was used for generation."
echo 