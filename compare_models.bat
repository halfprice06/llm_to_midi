@echo off
REM Compare Models - A simple script to demonstrate the multiple model generation feature

echo LLM to MIDI - Model Comparison Script
echo =========================================
echo.
echo This script will generate music using multiple models with the same theme.
echo.

python main.py --models "OpenAIGPT4oMini,AnthropicHaiku" --theme "Create a playful piano piece with a clear melodic theme and variations. Use a fast tempo and bright major key."

echo.
echo All models have completed. Check the outputs folder for the generated MIDI files.
echo Each filename includes the model name that was used for generation.
echo. 