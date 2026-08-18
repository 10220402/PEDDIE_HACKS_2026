from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from testing_database import (
    create_database,
    save_chat,
    get_chat_history
)
import os


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
# WEBSITE HOME
# ==========================================

@app.route("/")
def home():

    return send_from_directory(
        os.path.dirname(os.path.abspath(__file__)),
        "index.html"
    )


# ==========================================
# SERVE WEBSITE FILES
# ==========================================

@app.route("/<path:filename>")
def static_files(filename):

    return send_from_directory(
        os.path.dirname(os.path.abspath(__file__)),
        filename
    )


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
You are HealthLens, a health-information chatbot.

Your ONLY purpose is to answer health-related
questions.

==================================================
HEALTH-ONLY RULE
==================================================

You may answer questions about:

• Health
• Diseases
• Medical conditions
• Symptoms
• The human body
• Nutrition
• Sleep
• Exercise
• Hygiene
• Mental wellbeing
• First aid
• Prevention
• Medical tests
• Healthcare
• General medicine information
• Health-related lifestyle questions

If the question is genuinely health-related,
answer it.

If the question is NOT health-related,
DO NOT answer it.

Do NOT try to connect unrelated questions to
health.

For ANY unrelated question, reply ONLY:

**I'm HealthLens, a health-information chatbot. 🩺**

• I'm only available to answer health-related
  questions.
• Please ask me something about health!

Do not answer or discuss the unrelated question.

==================================================
FOLLOW-UP QUESTIONS
==================================================

Use the conversation history to understand
follow-up questions.

For example:

User: What is asthma?

HealthLens: [answer]

User: What are its symptoms?

Understand that "its" refers to asthma.

Do not ask the user to repeat information that
is already clear from the conversation.

==================================================
ANSWER STYLE
==================================================

For health-related questions:

• Use easy English.
• Keep answers short and useful.
• Preferably stay under 120 words.
• Do not write unnecessarily long paragraphs.
• Be clear, respectful, and calm.

==================================================
FORMATTING
==================================================

Use clean formatting.

Use bold headings when appropriate.

Example:

**What is Asthma?**

• Asthma is a common lung condition that can make
  breathing difficult.

**Common Symptoms**

• Coughing
• Wheezing
• Shortness of breath
• Chest tightness

**Important**

• This information is for educational purposes.

Formatting rules:

• Put each important point on a new line.
• Use the bullet character "•".
• Leave a blank line between sections.
• Keep the answer visually clean.

==================================================
HEALTH SAFETY
==================================================

• Provide educational information only.
• Do NOT diagnose the user.
• Do NOT say the user definitely has a disease.
• Do NOT replace a doctor or healthcare professional.
• Do NOT provide personalized medication doses.
• Do NOT tell users to start, stop, or change
  prescription medicine.
• If serious or emergency symptoms are described,
  recommend professional medical help.

==================================================
CONVERSATION HISTORY
==================================================

{conversation_context}

==================================================
CURRENT USER QUESTION
==================================================

{message}

==================================================
FINAL DECISION
==================================================

If the question is health-related:
Answer it.

If the question is NOT health-related:
Reply ONLY with:

**I'm HealthLens, a health-information chatbot. 🩺**

• I'm only available to answer health-related
  questions.
• Please ask me something about health!

Do not add anything else.
"""
        )


        # ==================================
        # GET AI RESPONSE
        # ==================================

        reply = response.text


        # ==================================
        # SAVE CHAT
        # ==================================

        save_chat(
            user_message=message,
            ai_response=reply
        )


        # ==================================
        # SEND RESPONSE
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
# HISTORY API
# ==========================================

@app.route("/history", methods=["GET"])
def history():

    try:

        history_data = get_chat_history()

        history_list = []

        for item in history_data:

            history_list.append({
                "id": item[0],

                # IMPORTANT:
                # history.js expects "message"
                "message": item[1],

                # IMPORTANT:
                # history.js expects "reply"
                "reply": item[2],

                "created_at": item[3]
            })

        return jsonify({
            "history": history_list
        })


    except Exception as e:

        print("HISTORY ERROR:", e)

        return jsonify({
            "history": [],
            "error": "History could not be loaded."
        }), 500


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )