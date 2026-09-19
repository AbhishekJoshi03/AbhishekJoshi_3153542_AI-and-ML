import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";

const TOOL_LABELS = {
  search_travel_knowledge_base: "📚 Knowledge Base",
  get_current_weather: "🌤 Weather MCP",
  convert_indian_rupees_to_sgd: "💱 Currency MCP",
};

function ChatBubble({ turn }) {
  const isUser = turn.sender === "user";

  return (
    <div className={`message-row ${isUser ? "from-user" : "from-assistant"}`}>
      <div className="message-avatar">{isUser ? "🧑" : "🦩"}</div>

      <div className="message-body">
        <div className="message-sender">{isUser ? "You" : "Singapore Travel Agent"}</div>

        <div className="message-bubble">
          <Markdown remarkPlugins={[remarkGfm, remarkBreaks]}>
            {turn.text}
          </Markdown>
        </div>

        {!isUser && turn.toolsInvoked?.length > 0 && (
          <div className="tool-chip-row">
            {turn.toolsInvoked.map((toolName) => (
              <span className="tool-chip" key={toolName}>
                {TOOL_LABELS[toolName] || toolName}
              </span>
            ))}
          </div>
        )}

        {!isUser && turn.citations?.length > 0 && (
          <div className="citation-panel">
            <div className="citation-title">Sources</div>

            {[...new Map(turn.citations.map(item => [item.title, item])).values()].map((citation) => (
              <a
                key={citation.title}
                href={citation.url}
                target="_blank"
                rel="noreferrer"
                className="citation-link"
              >
                📄 {citation.title}
              </a>
            ))}
          </div>
        )}

        {!isUser && turn.usedLiveData && (
          <div className="live-data-note">
            ⚡ Current information retrieved live via MCP
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatBubble;
