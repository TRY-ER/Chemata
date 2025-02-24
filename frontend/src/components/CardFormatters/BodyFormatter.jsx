import React, { useEffect } from "react";
import "./Formatter.css";
import ProtViewer from "../ProtViewer/ProtViewer";

const BodyFormatter = ({ content, cardType }) => {
    useEffect(() => {
        console.log("card type >>", cardType);
    }, [cardType])

    if (["SMILES Similarity Search", "Polymer Similarity Search", "Protein Similarity Search"].includes(cardType)) {
        console.log("this is gettting triggered")
        return (
            <div className="card-content">
                {content.image && <img src={`data:image/png;base64,${content.image}`} alt="Tool" />}
                {content.identifier && <p className="card-iden">{content.identifier}</p>}
                {content.score && <p>Score: {content.score.toFixed(3)}</p>}
            </div>
        );
    }
    if (["Molecule Explorer", "Polymer Explorer"].includes(cardType)) {
        return (
            <div className="card-content">
                {content.image && <img src={`data:image/png;base64,${content.image}`} alt="Tool" />}
                {content.info && Object.entries(content.info).map(([key, value]) => (
                    <p key={key}>
                        <span className="key-highlight">{key}</span>: <span className="value-gap">{value}</span>
                    </p>
                ))}
            </div>
        );
    }
    if (cardType === "Protein Explorer") {
        return (
            <div className="card-content">
                <ProtViewer activeMol={content.id} />
                {content.info && Object.entries(content.info).map(([key, value]) => (
                    <p key={key}>
                        <span className="key-highlight">{key}</span>: <span className="value-gap">{value}</span>
                    </p>
                ))}
            </div>
        );
    }
};

export default BodyFormatter;