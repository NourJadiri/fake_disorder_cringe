#!/bin/bash

# Start Ollama in the background.

/bin/ollama serve &
# Record Process ID.
pid=$!
# Pause for Ollama to start.
sleep 5

echo "🔴 Retrieve llama model..."
ollama pull llama3.2
echo "🟢 Done!"

ollama create genderizer -f ./genderizer-modelfile
echo "🟢 Created genderizer model!"

ollama create sentimentizer -f ./sentimentizer-modelfile
echo "🟢 Created sentimentizer model!"

# Wait for Ollama process to finish.
wait $pid