import React from 'react';
import ReactMarkdown from 'react-markdown';
import "./ChatParser.css";

const ChatParser = ({ response }) => {
  if (!response) return null;

  const startMarker = "<# Chat Response Start#>";
  const endMarker = "<# Chat Response End#>";

  let content = response;
  const startIndex = response.indexOf(startMarker);
  
  if (startIndex !== -1) {
    // When the start marker exists, chop it off.
    const offset = startIndex + startMarker.length;
    const endIndex = response.indexOf(endMarker, offset);
  
    if (endIndex === -1) {
      // End marker not yet received – display content from start marker to the current end (streaming state)
      content = response.substring(offset).trim();
    } else {
      // Both markers received – extract only content between them
      content = response.substring(offset, endIndex).trim();
    }
  }

  return (
    <div className="chat-parser-content">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};

export default ChatParser;