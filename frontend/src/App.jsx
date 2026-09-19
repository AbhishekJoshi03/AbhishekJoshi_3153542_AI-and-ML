import { useState } from "react";
import ChatBubble from "./components/ChatBubble";
import "./App.css";

const API_BASE_URL = "http://localhost:8000";

const WELCOME_TURN = {
  sender: "assistant",
  text:
    "Hi, I'm Singapore Travel Agent! I can help with attractions, transport, food, itineraries, current weather and INR to SGD conversion for your Singapore trip.",
  toolsInvoked: [],
  citations: [],
  usedLiveData: false,
};

const SUGGESTED_PROMPTS = [
  "3-day itinerary for a first-time visitor",
  "What's the weather like this week?",
  "Convert ₹50,000 to SGD",
  "Best neighbourhoods for street food",
];

function extractReplyText(reply) {
  if (typeof reply === "string") {
    return reply;
  }

  if (Array.isArray(reply) && reply[0]?.text) {
    return reply[0].text;
  }

  return "Sorry, I couldn't parse that response.";
}

function App() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [conversation, setConversation] = useState([WELCOME_TURN]);
  const [draftMessage, setDraftMessage] = useState("");
  const [isWaitingForReply, setIsWaitingForReply] = useState(false);

  const submitMessage = async (messageOverride) => {
    const messageText = (messageOverride ?? draftMessage).trim();

    if (!messageText || isWaitingForReply) {
      return;
    }

    setConversation((previous) => [
      ...previous,
      { sender: "user", text: messageText },
    ]);

    setDraftMessage("");
    setIsWaitingForReply(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message: messageText,
        }),
      });

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();

      setConversation((previous) => [
        ...previous,
        {
          sender: "assistant",
          text: extractReplyText(data.reply),
          toolsInvoked: data.tools_invoked || [],
          citations: data.citations || [],
          usedLiveData: data.used_live_data || false,
        },
      ]);
    } catch (error) {
      console.error(error);

      setConversation((previous) => [
        ...previous,
        {
          sender: "assistant",
          text: "Sorry, I could not connect to the travel companion backend.",
          toolsInvoked: [],
          citations: [],
          usedLiveData: false,
        },
      ]);
    } finally {
      setIsWaitingForReply(false);
    }
  };

  const handleComposerKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitMessage();
    }
  };

  const startNewChat = () => {
    window.location.reload();
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-inner">
          <div className="app-brand">
            <div className="app-brand-mark">🦩</div>
            <div className="app-brand-text">
              <h1>Singapore Travel Agent</h1>
              <p>Your Singapore travel companion</p>
            </div>
          </div>

          <button className="new-chat-button" onClick={startNewChat}>
            New Chat
          </button>
        </div>
      </header>

      <main className="chat-shell">
        <div className="message-list">
          {conversation.map((turn, index) => (
            <ChatBubble key={index} turn={turn} />
          ))}

          {isWaitingForReply && (
            <div className="message-row from-assistant">
              <div className="message-avatar">🦩</div>
              <div className="message-body">
                <div className="message-sender">Singapore Travel Agent</div>
                <div className="message-bubble is-typing">
                  <span className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {conversation.length === 1 && (
          <div className="suggestion-row">
            {SUGGESTED_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                className="suggestion-chip"
                onClick={() => submitMessage(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        )}

        <div className="composer">
          <textarea
            value={draftMessage}
            onChange={(event) => setDraftMessage(event.target.value)}
            onKeyDown={handleComposerKeyDown}
            placeholder="Ask me anything about Singapore..."
            rows={2}
            disabled={isWaitingForReply}
          />

          <button
            onClick={() => submitMessage()}
            disabled={isWaitingForReply || !draftMessage.trim()}
          >
            Send
          </button>
        </div>

        <div className="composer-footnote">
          Knowledge Base • Live Weather via MCP • Live Currency via MCP
        </div>
      </main>
    </div>
  );
}

export default App;
