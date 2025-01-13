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
ollama run mistral

# Wait for Ollama process to finish.
wait $pid