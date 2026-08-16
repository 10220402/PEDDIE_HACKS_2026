from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
import os

# Database functions
from testing_database import (
    create_database,
    save_chat,
    get_chat_history
)


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in the .env file."
    )


# ==========================================
# CONNECT TO GEMINI
# ==========================================

client = genai.Client(api_key=api_key)


# ==========================================
# CREATE FLASK APP
# ==========================================

app = Flask(__name__)

CORS(app)


# ==========================================
# CREATE DATABASE
# ==========================================

create_database()


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return "HealthLens backend is working!"


# ==========================================
# CHAT
# ==========================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json() or {}

    message = data.get("message", "").strip()

    history = data.get("history", [])


    # ======================================
    # CHECK MESSAGE
    # ======================================

    if not message:

        return jsonify({
            "reply": "Please enter a health question."
        })


    # ======================================
    # BUILD CONVERSATION CONTEXT
    # ======================================

    conversation_context = ""

    for item in history:

        role = item.get("role", "")

        text = item.get("message", "")


        if role == "user":

            conversation_context += (
                f"User: {text}\n"
            )


        elif role == "assistant":

            conversation_context += (
                f"HealthLens: {text}\n"
            )


    # ======================================
    # ASK GEMINI
    # ======================================

    try:

        response = client.models.generate_content(

            model="gemini-3.5-flash",

            contents=f"""
You are HealthLens AI, a simple and friendly
health-information assistant.

Your goal is to explain health topics in EASY
ENGLISH so ordinary people can understand the
information quickly.

CONVERSATION RULE:
- Use the conversation history to understand
  words such as "it", "its", "they", "them",
  "this", and "that".
- If the user asks a follow-up question,
  understand what health topic they mean from
  the previous conversation.
- Do not ask the user to repeat information
  that is already clear from the conversation.

ANSWER STYLE:
- Keep every answer short and to the point.
- Preferably stay under 120 words.
- Do not write long paragraphs.
- Do not unnecessarily repeat the question.
- Give useful information directly.

FORMATTING:
- Use clear bold headings with Markdown.
- Example:
  **What is Asthma?**
  **Common Symptoms**
  **Important**
- Put every important point on a new line.
- Use "-" for bullet points.
- Put a blank line between sections.
- Keep the answer clean and easy to read.

HEALTH SAFETY:
- Provide educational information only.
- Do not diagnose the user.
- Do not say the user definitely has a disease.
- Do not replace a doctor or healthcare professional.
- Do not provide personalized medication doses.
- Do not tell users to start, stop, or change
  prescription medicine.
- If serious or emergency symptoms are described,
  recommend professional medical help.

LANGUAGE:
- Use simple everyday English.
- Be respectful and calm.
- Avoid unnecessary medical terminology.
- Explain difficult medical terms simply.

CONVERSATION HISTORY:
{conversation_context}

CURRENT USER QUESTION:
{message}
"""
        )


        # ==================================
        # GET AI RESPONSE
        # ==================================

        reply = response.text


        # ==================================
        # SAVE CHAT TO DATABASE
        # ==================================

        save_chat(
            user_message=message,
            ai_response=reply
        )


        # ==================================
        # SEND RESPONSE TO WEBSITE
        # ==================================

        return jsonify({
            "reply": reply
        })


    except Exception as e:

        print("GEMINI API ERROR:", e)

        return jsonify({
            "reply":
            "⚠️ HealthLens AI is temporarily unavailable. "
            "Please try again shortly."
        })


# ==========================================
# HISTORY
# ==========================================

@app.route("/history", methods=["GET"])
def history():

    try:

        rows = get_chat_history()

        history = []


        for row in rows:

            chat_id = row[0]

            user_message = row[1]

            ai_response = row[2]

            created_at = row[3]


            history.append({

                "id": chat_id,

                "message": user_message,

                "reply": ai_response,

                "created_at": created_at

            })


        return jsonify({

            "history": history

        })


    except Exception as e:

        print("HISTORY ERROR:", e)

        return jsonify({

            "history": [],

            "error":
                "Could not load conversation history."

        }), 500


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)