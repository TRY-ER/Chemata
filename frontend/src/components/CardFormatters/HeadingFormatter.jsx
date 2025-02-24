import React from "react"
import { useState } from "react";
import "./Formatter.css";


const HeadingFormatter = ({ content, cardType, isCollapsed, setIsCollapsed }) => {
  const toggleCollapse = () => setIsCollapsed(prev => !prev);
  return (
    <div className="card-header" onClick={toggleCollapse}>
      {content?.identifier && <span>{content.identifier}</span>}
      {content?.id && <span>{content?.id}</span>}
      <button className="collapse-button">
        {isCollapsed ? 'Expand' : 'Collapse'}
      </button>
    </div>
  );
}

export default HeadingFormatter;