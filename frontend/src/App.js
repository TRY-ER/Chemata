import React, { useState, useEffect, useRef } from 'react';
import Draggable from 'react-draggable';
import './App.css';
import ReactDOM from 'react-dom';
import DraggableInfoButton from './components/DraggableContainer/DragContain';
import DragVisualizer from './components/DraggableContainer/DraggableVisualizer/DragViz';
import ChatParser from './components/Parsers/ChatParser';
import ToolParser from './components/Parsers/ToolParser/ToolParser';
import SpawnCards from './components/SpawnCards/SpawnCards';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [dots, setDots] = useState([]);
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [cardContents, setCardContents] = useState([]);
  const [cardType, setCardType] = useState('');
  const [isSpawned, setIsSpawned] = useState(false);
  const [chatState, setChatState] = useState('default');
  const [currentActiveId, setCurrentActiveId] = useState(null);
  const textareaRef = useRef(null);
  const eventSourceRef = useRef(null);
  const chatActionRef = useRef(null);

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
    setChatState('running');
    setCardContents([]);
    setIsSpawned(false);
    // Save the query and create a new response entry
    const newResponseId = uuidv4();
    console.log("New response ID: ", newResponseId);
    console.log("Type of New response ID: ", typeof newResponseId);
    setResponses(prev => [...prev, {
      id: newResponseId,
      query: query,
      response: '',
      complete: false
    }]);
    setCurrentActiveId(newResponseId);

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
        body: JSON.stringify({ id: newResponseId, query: query, config: {} }), // Send ID with query
      });

      if (!response.ok) throw new Error('Network response was not ok');

      // Setup SSE connection
      eventSourceRef.current = new EventSource(`http://localhost:8000/chat/stream/${newResponseId}`);

      eventSourceRef.current.onmessage = (event) => {
        if (event.data === "<|end|>") {
          setResponses(prev => prev.map(resp =>
            resp.id === newResponseId
              ? { ...resp, complete: true }
              : resp
          ));
          eventSourceRef.current && eventSourceRef.current.close();
          setChatState('default');
          return;
        }
        const data = JSON.parse(event.data);
        setResponses(prev => prev.map(resp =>
          resp.id === newResponseId
            ? { ...resp, response: resp.response + data }
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
        setChatState('default');
      };

    } catch (error) {
      console.error('Error:', error);
      setResponses(prev => prev.map(resp =>
        resp.id === newResponseId
          ? { ...resp, response: 'Error: Failed to get response', complete: true }
          : resp
      ));
      setChatState('default');
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

  useEffect(() => {
    console.log('chat state: ', chatState);
  }, [chatState]);

  const handleMouseLeave = () => {
    setDots((prevDots) =>
      prevDots.map((dot) => ({
        ...dot,
        x: dot.origX,
        y: dot.origY,
      }))
    );
  };

  useEffect(() => {
    console.log("Card Type: ", cardType);
  }, [cardType])

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

  const setActiveIdOnClick = (id) => {
    // console.log("id recieved >>", id);
    if (chatState === "running") return;
    setCurrentActiveId(id);
  }

  // useEffect(() => {
  //   console.log("current active id >>", currentActiveId);
  // }, [currentActiveId]);

  const queryResponseSection = responses.map(({ id, query: userQuery, response }) => (
    <div key={id} className={`singular-section
      ${id === currentActiveId ? 'active' : ''}
    `} onClick={() => {setActiveIdOnClick(id)}}>
      <div className="query-section">
        <p>{userQuery}</p>
      </div>
      <ToolParser response={response}
        setCardContents={setCardContents}
        isSpawned={isSpawned}
        setIsSpawned={setIsSpawned}
        setCardType={setCardType}
        id={id}
        currentActiveId={currentActiveId}
      />
      <div className={`response-section ${id === currentActiveId && chatState === "running" ? 'running' : ''}
      `}>
        {<ChatParser response={response} />}
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

      <div className="chat-actions"
        ref={chatActionRef}
      >
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
      <SpawnCards existingElems={[chatActionRef, textareaRef]} cardContents={cardContents} cardType={cardType}
      currentActiveId={currentActiveId} />
    </div>
  );
}

export default App;

// import React, { useState, useEffect, useRef } from 'react';
// import Draggable from 'react-draggable';
// import './App.css';
// import ReactDOM from 'react-dom';
// import DraggableInfoButton from './components/DraggableContainer/DragContain';
// import DragVisualizer from './components/DraggableContainer/DraggableVisualizer/DragViz';
// import ChatParser from './components/Parsers/ChatParser';
// import ToolParser from './components/Parsers/ToolParser/ToolParser';

// function App() {
//   const [dots, setDots] = useState([]);
//   const [query, setQuery] = useState('');
//   const [responses, setResponses] = useState([]);
//   const [spawnedCards, setSpawnedCards] = useState([]);
//   const [isLoading, setIsLoading] = useState(false);
//   const textareaRef = useRef(null);
//   const eventSourceRef = useRef(null);

//   // Used for non-overlap spawning
//   const CARD_WIDTH = 250;
//   const CARD_HEIGHT = 150;

//   // On mount, create a grid of dots (existing code)
//   useEffect(() => {
//     const spacing = 50;
//     const cols = Math.floor(window.innerWidth / spacing);
//     const rows = Math.floor(window.innerHeight / spacing);
//     let id = 0;
//     const newDots = [];
//     for (let i = 0; i <= rows; i++) {
//       for (let j = 0; j <= cols; j++) {
//         const x = j * spacing + spacing / 2;
//         const y = i * spacing + spacing / 2;
//         newDots.push({ id: id++, x, y, origX: x, origY: y });
//       }
//     }
//     setDots(newDots);
//   }, []);

//   const handleSend = async () => {
//     if (!query.trim()) return;
//     const newResponseId = Date.now();
//     setResponses(prev => [...prev, {
//       id: newResponseId,
//       query: query,
//       response: '',
//       complete: false
//     }]);
//     setQuery('');
//     if (textareaRef.current) {
//       textareaRef.current.style.height = 'auto';
//     }
//     try {
//       setIsLoading(true);
//       const response = await fetch('http://localhost:8000/chat/init', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ id: newResponseId, query: query, config: {} }),
//       });
//       if (!response.ok) throw new Error('Network response was not ok');
//       eventSourceRef.current = new EventSource(`http://localhost:8000/chat/stream/${newResponseId}`);
//       eventSourceRef.current.onmessage = (event) => {
//         if (event.data === "<|end|>") {
//           setResponses(prev => prev.map(resp =>
//             resp.id === newResponseId ? { ...resp, complete: true } : resp
//           ));
//           eventSourceRef.current && eventSourceRef.current.close();
//           return;
//         }
//         const data = JSON.parse(event.data);
//         setResponses(prev => prev.map(resp =>
//           resp.id === newResponseId
//             ? { ...resp, response: resp.response + data }
//             : resp
//         ));
//       };
//       eventSourceRef.current.onerror = () => {
//         setResponses(prev => prev.map(resp =>
//           resp.id === newResponseId ? { ...resp, complete: true } : resp
//         ));
//         eventSourceRef.current.close();
//       };
//     } catch (error) {
//       console.error('Error:', error);
//       setResponses(prev => prev.map(resp =>
//         resp.id === newResponseId
//           ? { ...resp, response: 'Error: Failed to get response', complete: true }
//           : resp
//       ));
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleMouseMove = (e) => {
//     const threshold = 100;
//     setDots(prevDots => prevDots.map(dot => {
//       const dx = dot.x - e.clientX;
//       const dy = dot.y - e.clientY;
//       const distance = Math.sqrt(dx * dx + dy * dy);
//       if (distance < threshold) {
//         const moveDistance = 5 * ((threshold - distance) / threshold);
//         const angle = Math.atan2(dy, dx);
//         return {
//           ...dot,
//           x: dot.x + Math.cos(angle) * moveDistance,
//           y: dot.y + Math.sin(angle) * moveDistance,
//         };
//       } else {
//         const revertSpeed = 0.1;
//         return {
//           ...dot,
//           x: dot.x + (dot.origX - dot.x) * revertSpeed,
//           y: dot.y + (dot.origY - dot.y) * revertSpeed,
//         };
//       }
//     }));
//   };

//   const handleMouseLeave = () => {
//     setDots(prevDots => prevDots.map(dot => ({
//       ...dot,
//       x: dot.origX,
//       y: dot.origY,
//     })));
//   };

//   useEffect(() => {
//     return () => {
//       if (eventSourceRef.current) {
//         eventSourceRef.current.close();
//       }
//     };
//   }, []);

//   const handleTextareaChange = (e) => {
//     setQuery(e.target.value);
//     if (textareaRef.current) {
//       textareaRef.current.style.height = 'auto';
//       textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
//     }
//   };

//   const queryResponseSection = responses.map(({ id, query: userQuery, response }) => (
//     <div key={id} className="singular-section">
//       <div className="query-section">
//         <p>{userQuery}</p>
//       </div>
//       <ToolParser response={response} />
//       <div className="response-section">
//         {<ChatParser response={response} /> || 'Loading...'}
//       </div>
//     </div>
//   ));

//   // ----- SPAWN CARDS LOGIC -----
//   // Utility: check if `rect` overlaps any rect in `rects`
//   const overlaps = (rect, rects) => {
//     return rects.some(r => {
//       return !(
//         rect.x + rect.width < r.x ||
//         rect.x > r.x + r.width ||
//         rect.y + rect.height < r.y ||
//         rect.y > r.y + r.height
//       );
//     });
//   };

//   // Utility: generate a non-overlapping random position
//   const generateRandomPosition = (cardWidth, cardHeight, reservedRects, existingRects) => {
//     for (let i = 0; i < 100; i++) {
//       const x = Math.random() * (window.innerWidth - cardWidth);
//       const y = Math.random() * (window.innerHeight - cardHeight);
//       const newRect = { x, y, width: cardWidth, height: cardHeight };
//       if (!overlaps(newRect, reservedRects) && !overlaps(newRect, existingRects)) {
//         return newRect;
//       }
//     }
//     return null;
//   };

//   // Function to spawn a new card
//   const spawnCard = () => {
//     // Define reserved areas for existing UI elements:
//     // Chat Actions area (approximation based on App.css)
//     const chatActionsRect = {
//       x: window.innerWidth * 0.5 - (window.innerWidth * 0.4) / 2,
//       y: window.innerHeight * 0.6, // since chat-actions is at bottom:40%
//       width: window.innerWidth * 0.4,
//       height: window.innerHeight * 0.45,
//     };
//     // Glass input area approximation:
//     const glassInputRect = {
//       x: window.innerWidth * 0.5 - (window.innerWidth * 0.2) / 2,
//       y: window.innerHeight * 0.65 - 20,
//       width: window.innerWidth * 0.2,
//       height: 100,
//     };
//     const reservedRects = [chatActionsRect, glassInputRect];

//     // Existing cards' positions
//     const existingRects = spawnedCards.map(card => ({
//       x: card.x,
//       y: card.y,
//       width: CARD_WIDTH,
//       height: CARD_HEIGHT,
//     }));

//     const pos = generateRandomPosition(CARD_WIDTH, CARD_HEIGHT, reservedRects, existingRects);
//     if (pos) {
//       const newCard = { id: Date.now(), ...pos };
//       setSpawnedCards(prev => [...prev, newCard]);
//     } else {
//       console.log("No space available to spawn a new card.");
//     }
//   };

//   const updateCardPosition = (id, x, y) => {
//     setSpawnedCards(prev =>
//       prev.map(card => (card.id === id ? { ...card, x, y } : card))
//     );
//   };

//   // ----- SPAWN CARD COMPONENT -----
//   const SpawnCard = ({ card, updateCardPosition }) => {
//     const [isCollapsed, setIsCollapsed] = useState(true);
//     const toggleCollapse = () => setIsCollapsed(prev => !prev);

//     return (
//       <Draggable
//         bounds="parent"
//         position={{ x: card.x, y: card.y }}
//         onStop={(e, data) => updateCardPosition(card.id, data.x, data.y)}
//       >
//         <div className="spawn-card">
//           <div className="card-header" onClick={toggleCollapse}>
//             <span>Spawn Card {card.id}</span>
//             <button className="collapse-button">
//               {isCollapsed ? 'Expand' : 'Collapse'}
//             </button>
//           </div>
//           {!isCollapsed && (
//             <div className="card-content">
//               <p>This is some collapsible content for card {card.id}.</p>
//             </div>
//           )}
//         </div>
//       </Draggable>
//     );
//   };

//   return (
//     <div
//       className="App"
//       onMouseMove={handleMouseMove}
//       onMouseLeave={handleMouseLeave}
//     >
//       {dots.map(dot => (
//         <div
//           key={dot.id}
//           className="dot"
//           style={{ left: dot.x, top: dot.y }}
//         />
//       ))}

//       <div className="chat-actions">
//         {responses.length > 0 ? queryResponseSection : (
//           <p className="empty-message">No conversations yet...</p>
//         )}
//       </div>

//       <div className="glass-input">
//         <textarea
//           ref={textareaRef}
//           placeholder="Type something..."
//           value={query}
//           onChange={handleTextareaChange}
//         />
//         <button className="send-button" onClick={handleSend}>
//           <svg
//             xmlns="http://www.w3.org/2000/svg"
//             viewBox="0 0 24 24"
//             fill="white"
//             width="20px"
//             height="20px"
//           >
//             <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
//           </svg>
//         </button>
//       </div>

//       <DraggableInfoButton
//         Visible={<DragVisualizer style={{ top: "25px", right: "25px" }} />}
//         Content={<h1>Some Content</h1>}
//       />

//       {/* Spawn Card Button */}
//       <button className="spawn-button" onClick={spawnCard}>
//         Spawn Card
//       </button>

//       {/* Render spawned cards */}
//       {spawnedCards.map(card => (
//         <SpawnCard key={card.id} card={card} updateCardPosition={updateCardPosition} />
//       ))}
//     </div>
//   );
// }

// export default App;