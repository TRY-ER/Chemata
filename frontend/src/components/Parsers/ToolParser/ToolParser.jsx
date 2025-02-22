import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { FaWrench } from 'react-icons/fa';
import "./ToolParser.css";

const ToolParser = ({ response }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);
  if (!response) return null;

  // Define the marker regex to extract the JSON between markers.
  const markerRegex = /<#\s*Tool Response\s*#>([\s\S]*?)<#\s*Tool Response\s*#>/;
  const match = response.match(markerRegex);
  let content = response;

  if (match && match[1]) {
    content = match[1].trim();
  }

  // Attempt to parse the extracted string as JSON.
  let parsedData;
  try {
    parsedData = JSON.parse(content);
  } catch (error) {
    console.error("Failed to parse tool response JSON:", error);
    return <div className="tool-parser-error">Invalid Tool Response Format</div>;
  }

  // Always call useState at the top level.
  const toggleCollapse = () => {
    setIsCollapsed(prev => !prev);
  };

  // If the JSON contains a details property, render the tool section.
  if (parsedData.details) {
    const { name, description } = parsedData.details;
    return (
      <div className="tool-section">
        <div className="tool-header" onClick={toggleCollapse}>
          <FaWrench className="tool-icon" />
          <span className="tool-name">{name || 'Tool'}</span>
          <button className="toggle-button">
            {isCollapsed ? "Read More" : "Collapse"}
          </button>
        </div>
        {!isCollapsed && (
          <div className="tool-description">
            <ReactMarkdown>{description || 'No description provided.'}</ReactMarkdown>
          </div>
        )}
      </div>
    );
  }

  // Fallback: Render the entire content as markdown if no details property is provided.
  return (
    <div className="tool-parser-content">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};

export default ToolParser;