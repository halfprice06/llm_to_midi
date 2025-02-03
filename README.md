set up venv

install pip -r requirements.txt

set up api keys in .env

go to baml_src/clients.baml for list of wired up models

choose a model name and insert into the 'client' field for the two baml functions in midi.baml | GenerateCompositionPlan() and GenerateOneSection() 

run main.py and describe what kind of composition you want it to write. the model can control style, tempo, key, selected midi instrument for bass tenor soprano and alto channels, a piano track and percussion on channel 10

o1 and sonnet seem to work best. 

prompts need work, few shot examples maybe of what good chord structure looks like and how to write a solid melody. 

