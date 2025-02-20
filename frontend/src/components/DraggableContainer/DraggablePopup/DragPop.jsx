import React from "react";
import "./DragPop.css";

const DragPop = ({ Content, setPopupOpen }) => {
    return (
        <div className="popup" onClick={() => setPopupOpen(false)}>
            <div className="popup-content" onClick={(e) => e.stopPropagation()}>
                <div className="close-button" onClick={() => setPopupOpen(false)}>
                    ✖
                </div>
                {Content}
            </div>
        </div>
    )
}

export default DragPop;