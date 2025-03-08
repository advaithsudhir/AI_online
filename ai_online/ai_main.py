import os
import requests
import json
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Mistral API details
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "YOUR API KEY") # Obtain your api key from mistral ai
API_URL = "https://api.mistral.ai/v1/chat/completions"

# File for chat history
CHAT_HISTORY_FILE = "chat_history.json"

# Function to load chat history from file
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        print(f"✅ Found chat history file: {CHAT_HISTORY_FILE}")
        try:
            with open(CHAT_HISTORY_FILE, "r") as file:
                content = file.read()
                print(f"✅ File content: {content}")
                if content.strip():  # Check if file is not empty
                    return json.loads(content)
                else:
                    print("❌ Chat history file is empty. Starting fresh.")
        except (json.JSONDecodeError, IOError) as e:
            print(f"❌ Error loading chat history file: {e}. Starting fresh.")
    else:
        print(f"❌ Chat history file not found: {CHAT_HISTORY_FILE}. Starting fresh.")
    return [{"role": "system", "content": "You are a helpful AI assistant."}]

# Function to save chat history to file
def save_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, "w") as file:
            json.dump(chat_history, file, indent=4)
        print(f"✅ Chat history saved to: {CHAT_HISTORY_FILE}")
    except IOError as e:
        print(f"❌ Error saving chat history to file: {e}")

# Load chat history at the start
chat_history = load_chat_history()

def chat_with_mistral(user_input):
    global chat_history

    # Add user message to chat history
    chat_history.append({"role": "user", "content": user_input})

    # Send request to Mistral AI
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
            json={"model": "mistral-tiny", "messages": chat_history},
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Error: Failed to connect to Mistral API. {e}")
        return "❌ Error: Failed to connect to Mistral API."

    # Extract response text
    try:
        ai_response = response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        ai_response = "❌ Error: Could not get a valid response from Mistral API."

    # Add AI response to history
    chat_history.append({"role": "assistant", "content": ai_response})

    # Limit chat history size
    MAX_HISTORY_LENGTH = 10
    if len(chat_history) > MAX_HISTORY_LENGTH:
        chat_history = chat_history[-MAX_HISTORY_LENGTH:]

    # Save updated chat history to file
    save_chat_history()

    return ai_response

# Example chat loop
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("AI: Goodbye!")
        break
    reply = chat_with_mistral(user_input)
    print(f"AI: {reply}")
