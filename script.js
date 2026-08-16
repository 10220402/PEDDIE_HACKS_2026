// ==========================================
// HEALTHLENS - CHAT INTERFACE
// ==========================================

const input = document.getElementById("userMessage");
const messages = document.getElementById("chatMessages");

// ==========================================
// CONVERSATION HISTORY
// ==========================================

let conversationHistory = [];

// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage() {

    const userText = input.value.trim();

    if (userText === "") {
        return;
    }

    conversationHistory.push({
        role: "user",
        message: userText
    });

    messages.innerHTML += `
        <div class="user-message">
            ${escapeHTML(userText)}
        </div>
    `;

    input.value = "";

    const thinkingId = "thinking-" + Date.now();

    messages.innerHTML += `
        <div class="bot-message thinking" id="${thinkingId}">
            🤔 HealthLens is thinking...
        </div>
    `;

    scrollToBottom();

    try {

        const response = await fetch("/chat", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: userText,
                history: conversationHistory
            })
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        const thinkingMessage =
            document.getElementById(thinkingId);

        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        const reply =
            data.reply ||
            "Sorry, I couldn't generate a response.";

        conversationHistory.push({
            role: "assistant",
            message: reply
        });

        const formattedReply =
            formatAIResponse(reply);

        messages.innerHTML += `
            <div class="bot-message">
                ${formattedReply}
            </div>
        `;

        scrollToBottom();

    } catch (error) {

        console.error(
            "HealthLens connection error:",
            error
        );

        const thinkingMessage =
            document.getElementById(thinkingId);

        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        messages.innerHTML += `
            <div class="bot-message error-message">
                ⚠️ HealthLens couldn't connect right now.
                Please try again in a moment.
            </div>
        `;

        scrollToBottom();
    }
}

// ==========================================
// QUICK HEALTH TOPICS
// ==========================================

function askTopic(question) {

    input.value = question;

    sendMessage();
}

// ==========================================
// CLEAR CHAT
// ==========================================

function clearChat() {

    conversationHistory = [];

    messages.innerHTML = `
        <div class="bot-message">
            👋 Hello! I'm HealthLens.
            Ask me about a health topic.
        </div>

        <div class="health-topics">

            <h3>
                Explore Health Topics
            </h3>

            <div class="topic-categories">

                <button onclick="askTopic('What is asthma?')">
                    🫁 Respiratory Health
                </button>

                <button onclick="askTopic('What is anemia?')">
                    🩸 Blood & Nutrition
                </button>

                <button onclick="askTopic('What is diabetes?')">
                    🩺 Common Conditions
                </button>

                <button onclick="askTopic('What is dehydration?')">
                    💧 Everyday Health
                </button>

            </div>

        </div>
    `;

    scrollToBottom();
}

// ==========================================
// FORMAT AI RESPONSE
// ==========================================

function formatAIResponse(text) {

    text = text.trim();

    text = escapeHTML(text);

    text = text.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    text = text.replace(
        /^[ \t]*[-•]\s*(.*)$/gm,
        "<div class='answer-point'>• $1</div>"
    );

    text = text.replace(
        /^[ \t]*(\d+)\.\s+(.*)$/gm,
        "<div class='answer-point'>$1. $2</div>"
    );

    text = text.replace(
        /\n{2,}/g,
        "\n"
    );

    text = text.replace(
        /\n/g,
        "<br>"
    );

    return text;
}

// ==========================================
// SECURITY
// ==========================================

function escapeHTML(text) {

    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ==========================================
// AUTO SCROLL
// ==========================================

function scrollToBottom() {

    messages.scrollTop =
        messages.scrollHeight;
}

// ==========================================
// ENTER KEY SUPPORT
// ==========================================

input.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();
    }

});