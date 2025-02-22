import React, { useState, useEffect, useRef } from 'react';
import Draggable from 'react-draggable';
import './App.css';
import ReactDOM from 'react-dom';
import DraggableInfoButton from './components/DraggableContainer/DragContain';
import DragVisualizer from './components/DraggableContainer/DraggableVisualizer/DragViz';

function App() {
  const [dots, setDots] = useState([]);
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const textareaRef = useRef(null);
  const eventSourceRef = useRef(null);

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

  const handleSend = async () => {
    if (!query.trim()) return;

    // Save the query and create a new response entry
    const newResponseId = Date.now();
    setResponses(prev => [...prev, {
      id: newResponseId,
      query: query,
      response: '',
      complete: false
    }]);

    // Clear input
    setQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      setIsLoading(true);

      // Send query to backend with the ID
      const response = await fetch('http://localhost:8000/chat/init', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: newResponseId, query: query }), // Send ID with query
      });

      if (!response.ok) throw new Error('Network response was not ok');

      // Setup SSE connection
      eventSourceRef.current = new EventSource(`http://localhost:8000/chat/stream/${newResponseId}`);

      eventSourceRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setResponses(prev => prev.map(resp =>
          resp.id === newResponseId
            ? { ...resp, response: resp.response + data.chunk }
            : resp
        ));
      };

      eventSourceRef.current.onerror = () => {
        setResponses(prev => prev.map(resp =>
          resp.id === newResponseId
            ? { ...resp, complete: true }
            : resp
        ));
        eventSourceRef.current.close();
      };

    } catch (error) {
      console.error('Error:', error);
      setResponses(prev => prev.map(resp =>
        resp.id === newResponseId
          ? { ...resp, response: 'Error: Failed to get response', complete: true }
          : resp
      ));
    } finally {
      setIsLoading(false);
    }
  }; 

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

  // Cleanup SSE connection on component unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleTextareaChange = (e) => {
    setQuery(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  // const queryResponseSection = <>
  //     <div className = "singular-section">
  //       <div className = "query-section">
  //         <p>Some query</p>
  //       </div>
  //       <div className = "response-section">
  //         <p>Some response</p>
  //       </div>
  //     </div>
  //     </>

  const queryResponseSection = responses.map(({ id, query: userQuery, response }) => (
    <div key={id} className="singular-section">
      <div className="query-section">
        <p>{userQuery}</p>
      </div>
      <div className="response-section">
        <p>{response || 'Loading...'}</p>
      </div>
    </div>
  ));

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

      <div className="chat-actions">
        {responses.length > 0 ? queryResponseSection : (
          <p className="empty-message">No conversations yet...</p>
        )}
      </div>


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

      <DraggableInfoButton
        Visible={<DragVisualizer style={{ top: "25px", right: "25px" }} />}
        Content={<h1>Some Content</h1>}
      />
    </div>
  );
}

export default App;