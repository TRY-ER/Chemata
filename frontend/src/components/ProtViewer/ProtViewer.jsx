import React, { useEffect, useRef } from "react";
import * as $3Dmol from "3dmol";

const ProtViewer = ({
    activeMol,
}) => {
    const viewerRef = useRef(null);

    useEffect(() => {
        if (viewerRef.current) {
            // Create the viewer
            if (activeMol.length > 3) {
                const viewer = $3Dmol.createViewer(viewerRef.current);
                // Download PDB and load the 3D model
                $3Dmol.download(`pdb:${activeMol}`, viewer, { multimodel: true, frames: true }, function () {
                    viewer.setStyle({}, { cartoon: { color: "spectrum" } });
                    viewer.render();
                });
            }
        }
    }, [activeMol]);

    return (
        <div>
            {/* The div where the 3Dmol.js viewer will be created */}
            <div
                id="viewer"
                ref={viewerRef}
                style={{ width: '350px', height: '400px', position: 'relative' }}
            ></div>
        </div>
    );
};



export default ProtViewer;