//// filepath: /home/kalki/imported/career/Competitions/2025/AAAI Hackathon/frontend/src/components/SpawnCards/SpawnCards.jsx
import React, { useEffect, useState } from 'react';
import Draggable from 'react-draggable';
import './SpawnCards.css';
import { v4 as uuidv4 } from 'uuid';
import HeadingFormatter from '../CardFormatters/HeadingFormatter';
import { motion, AnimatePresence } from 'framer-motion';
import BodyFormatter from '../CardFormatters/BodyFormatter';

// These minimal sizes are used for collision detection.
const CARD_MIN_WIDTH = 350;
const CARD_MIN_HEIGHT = 40;

const SpawnCard = ({ card, updateCardPosition, content, cardType, index }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);

  useEffect(() => {
    console.log("content: ", content);
  }, [])

  return (
    <Draggable
      bounds="parent"
      position={{ x: card.x, y: card.y }}
      onStop={(e, data) => updateCardPosition(card.id, data.x, data.y)}
    >
      <motion.div
        className="spawn-card"
        initial={{ opacity: 0, filter: 'blur(10px)' }}
        animate={{ opacity: 1, filter: 'blur(0px)' }}
        exit={{ opacity: 0, filter: 'blur(10px)' }}
        transition={{ duration: 0.5, delay: index * 0.2 }}
      >
        <HeadingFormatter content={content} cardType={cardType} isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />
        {!isCollapsed && (
          <BodyFormatter content={content} cardType={cardType} />
        )}
      </motion.div>
    </Draggable>
  );
};

// Utility function to check if `rect` overlaps any rect in `rects`
const overlaps = (rect, rects) => {
  return rects.some(r => (
    rect.x + rect.width >= r.x &&
    rect.x <= r.x + r.width &&
    rect.y + rect.height >= r.y &&
    rect.y <= r.y + r.height
  ));
};

// Utility: tries up to 100 times to generate a non-overlapping random position using minimal dimensions.
const generateRandomPosition = (minWidth, minHeight, reservedRects, existingRects) => {
  for (let i = 0; i < 100; i++) {
    const x = Math.random() * (window.innerWidth - minWidth);
    const y = Math.random() * (window.innerHeight - minHeight);
    const newRect = { x, y, width: minWidth, height: minHeight };
    if (!overlaps(newRect, reservedRects) && !overlaps(newRect, existingRects)) {
      return newRect;
    }
  }
  return null;
};

const SpawnCards = ({ existingElems, cardContents, cardType }) => {
  const [spawnedCards, setSpawnedCards] = useState([]);

  const spawnCard = (cardContent) => {
    // Reserved areas from the passed refs (if any)
    let extraReserved = [];
    if (existingElems && Array.isArray(existingElems)) {
      existingElems.forEach(refElem => {
        if (refElem && refElem.current) {
          const rect = refElem.current.getBoundingClientRect();
          extraReserved.push({
            x: rect.left,
            y: rect.top,
            width: rect.width,
            height: rect.height,
          });
        }
      });
    }

    const reservedRects = [...extraReserved];

    // Existing cards' positions using minimal dimensions for collision testing.
    const existingRects = spawnedCards.map(card => ({
      x: card.x,
      y: card.y,
      width: CARD_MIN_WIDTH,
      height: CARD_MIN_HEIGHT,
    }));

    const pos = generateRandomPosition(CARD_MIN_WIDTH, CARD_MIN_HEIGHT, reservedRects, existingRects);
    if (pos) {
      const newCard = { id: uuidv4(), ...pos, content: cardContent };
      setSpawnedCards(prev => [...prev, newCard]);
    } else {
      // console.log("No space available to spawn a new card.");
    }
  };

  // useEffect(() => {
  //   console.log("")
  // }, [currentActiveId])

  useEffect(() => {
    console.log("cardContents: ", cardContents);
    setSpawnedCards([]);
    if (cardContents && cardContents.length > 0) {
      cardContents.forEach(card => {
        spawnCard(card);
      });
    }
  }, [cardContents])

  useEffect(() => {
    // console.log("spawnedCards:", spawnedCards)
  }, [spawnedCards])

  const updateCardPosition = (id, x, y) => {
    setSpawnedCards(prev =>
      prev.map(card => (card.id === id ? { ...card, x, y } : card))
    );
  };

  return (
    <div className="spawn-cards-container">
      <AnimatePresence>
        {spawnedCards.map((card, index) => (
          <SpawnCard
            key={card.id}
            card={card}
            updateCardPosition={updateCardPosition}
            content={card.content}
            cardType={cardType}
            index={index}
          />
        ))}
      </AnimatePresence>
      {/* {spawnedCards.map((card, index) => (
        <SpawnCard key={card.id} card={card} updateCardPosition={updateCardPosition} content={card.content} cardType={cardType} index={index} />
      ))} */}
    </div>
  );
};

export default SpawnCards;