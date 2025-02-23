import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { FaWrench } from 'react-icons/fa';
import "./ToolParser.css";

const ToolParser = ({ response,
  setCardContents,
  isSpawned,
  setIsSpawned,
  setCardType,
  id,
  currentActiveId }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const [spawned, setSpawned] = useState(false);
  // Define the marker regex to extract the JSON between markers.
  const markerRegex = /<#\s*Tool Response\s*#>([\s\S]*?)<#\s*Tool Response\s*#>/;
  const match = response.match(markerRegex);
  let content = response;

  if (match && match[1]) {
    content = match[1].trim();
  }

  // Attempt to parse the extracted string as JSON.
  let parsedData;
  if (content) {
    try {
      parsedData = JSON.parse(content);
      // console.log("Parsed tool response JSON:", parsedData);
    } catch (error) {
      // console.error("Failed to parse tool response JSON:", error);
    }
  }

  // Always call useState at the top level.
  const toggleCollapse = () => {
    setIsCollapsed(prev => !prev);
  };

  useEffect(() => {
    if (spawned) {
      setSpawned(false);
    }
  }, [currentActiveId])

  useEffect(() => {
    if (id === currentActiveId) {
      if (!spawned) {
        if (parsedData?.result) {
          if (parsedData?.result.status === "success") {
            if (Array.isArray(parsedData?.result.results)) {
              setCardContents(parsedData?.result.results);
            } else if (typeof parsedData?.result.results === 'object') {
              setCardContents([parsedData?.result.results]);
            }
            setSpawned(true);
          }
          if (parsedData?.details) {
            setCardType(parsedData?.details?.name);
          }
        }
        else {
          setCardContents([]);
        }
      }
    }
  }, [currentActiveId, response]);

  // If the JSON contains a details property, render the tool section.
  if (parsedData?.details) {
    const { name, description } = parsedData?.details;
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
};

export default ToolParser;