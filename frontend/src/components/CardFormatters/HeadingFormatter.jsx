import React from "react"
import { useState } from "react";
import "./Formatter.css";


const HeadingFormatter = ({ content, cardType, isCollapsed, setIsCollapsed }) => {
  const toggleCollapse = () => setIsCollapsed(prev => !prev);
  return (
    <div className="card-header" onClick={toggleCollapse}>
          <span>{content.identifier}</span>
          <button className="collapse-button">
            {isCollapsed ? 'Expand' : 'Collapse'}
          </button>
        </div>
  );
}

export default HeadingFormatter;