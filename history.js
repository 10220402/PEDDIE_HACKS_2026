// ==========================================
// HEALTHLENS - HISTORY
// ==========================================

const historyContainer =
    document.getElementById("historyContainer");


// ==========================================
// LOAD HISTORY
// ==========================================

async function loadHistory() {

    try {

        const response = await fetch("/history");


        if (!response.ok) {
            throw new Error("Could not load history");
        }


        const data = await response.json();


        if (!data.history || data.history.length === 0) {

            historyContainer.innerHTML = `
                <div class="empty-history">

                    📭

                    <h3>
                        No conversations yet
                    </h3>

                    <p>
                        Your HealthLens conversations
                        will appear here.
                    </p>

                </div>
            `;

            return;
        }


        historyContainer.innerHTML = "";


        data.history.forEach(item => {

            const historyItem =
                document.createElement("div");

            historyItem.className =
                "history-item";


            historyItem.innerHTML = `

                <div class="history-question">

                    <span>👤</span>

                    <div>

                        <strong>
                            You asked
                        </strong>

                        <p>
                            ${escapeHTML(item.message)}
                        </p>

                    </div>

                </div>


                <div class="history-answer">

                    <span>🤖</span>

                    <div>

                        <strong>
                            HealthLens
                        </strong>

                        <p>
                            ${formatAnswer(item.reply)}
                        </p>

                    </div>

                </div>

            `;


            historyContainer.appendChild(
                historyItem
            );

        });


    } catch (error) {

        console.error(
            "History error:",
            error
        );


        historyContainer.innerHTML = `

            <div class="history-error">

                ⚠️

                <h3>
                    History could not be loaded
                </h3>

                <p>
                    Make sure the HealthLens
                    backend is running.
                </p>

            </div>

        `;

    }

}


// ==========================================
// FORMAT ANSWER
// ==========================================

function formatAnswer(text) {

    if (!text) {
        return "";
    }


    let answer =
        escapeHTML(text);


    answer = answer.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );


    answer = answer.replace(
        /\n/g,
        "<br>"
    );


    return answer;

}


// ==========================================
// SECURITY
// ==========================================

function escapeHTML(text) {

    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


// ==========================================
// START
// ==========================================

loadHistory();