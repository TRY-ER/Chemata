import React, { useState, useEffect, useRef } from 'react';
import { DraggableCore } from 'react-draggable';
import './App.css';

function App() {
  const [dots, setDots] = useState([]);
  const [query, setQuery] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    // Create a grid of dots
    const spacing = 50;
    const cols = Math.floor(window.innerWidth / spacing);
    const rows = Math.floor(window.innerHeight / spacing);
    const newDots = [];
    let id = 0;
    for (let i = 0; i <= rows; i++) {
      for (let j = 0; j <= cols; j++) {
        const x = j * spacing + spacing / 2;
        const y = i * spacing + spacing / 2;
        newDots.push({ id: id++, x, y, origX: x, origY: y });
      }
    }
    setDots(newDots);
  }, []);

  const handleMouseMove = (e) => {
    const threshold = 100;
    setDots((prevDots) =>
      prevDots.map((dot) => {
        const dx = dot.x - e.clientX;
        const dy = dot.y - e.clientY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < threshold) {
          const moveDistance = 5 * ((threshold - distance) / threshold);
          const angle = Math.atan2(dy, dx);
          return {
            ...dot,
            x: dot.x + Math.cos(angle) * moveDistance,
            y: dot.y + Math.sin(angle) * moveDistance,
          };
        } else {
          const revertSpeed = 0.1;
          return {
            ...dot,
            x: dot.x + (dot.origX - dot.x) * revertSpeed,
            y: dot.y + (dot.origY - dot.y) * revertSpeed,
          };
        }
      })
    );
  };

  const handleMouseLeave = () => {
    setDots((prevDots) =>
      prevDots.map((dot) => ({
        ...dot,
        x: dot.origX,
        y: dot.origY,
      }))
    );
  };

  const handleSend = () => {
    console.log('Query sent:', query);
    setQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleTextareaChange = (e) => {
    setQuery(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  return (
    <div
      className="App"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {dots.map((dot) => (
        <div
          key={dot.id}
          className="dot"
          style={{ left: dot.x, top: dot.y }}
        />
      ))}
      <div className="glass-input">
        <textarea
          ref={textareaRef}
          placeholder="Type something..."
          value={query}
          onChange={handleTextareaChange}
        />
        <button className="send-button" onClick={handleSend}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="white"
            width="20px"
            height="20px"
          >
            <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default App;