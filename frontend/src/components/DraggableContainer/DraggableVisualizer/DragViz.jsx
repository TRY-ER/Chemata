import React, { forwardRef } from "react";
import "./DragViz.css";

const DragVisualizer = forwardRef((props, ref) => {
  return (
    <div
      ref={ref}
      className="info-button"
      style={props.style}
    >
      ℹ
    </div>
  );
});

export default DragVisualizer;