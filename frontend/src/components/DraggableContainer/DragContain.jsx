import React, { useState } from 'react';
import Draggable from 'react-draggable';
import DragPop from './DraggablePopup/DragPop';
import "./DragContain.css";

const DraggableContainer = ({ Visible, Content }) => {
  const [popupOpen, setPopupOpen] = useState(false);

  const handleTogglePopup = () => {
    setPopupOpen((open) => !open);
  };

  return (
    <>
      <Draggable>
        <div onClick={handleTogglePopup}>
          {Visible}
        </div>
      </Draggable>
      {popupOpen && (
        <DragPop Content={Content} setPopupOpen={setPopupOpen} />  
      )}
    </>
  );
};

export default DraggableContainer;