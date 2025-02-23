import React, { useEffect } from "react";

const BodyFormatter = ({ content, cardType }) => {
    useEffect(() => {
        console.log("card type >>", cardType);
    }, [cardType])

    if (cardType === "SMILES Similarity Search") {
        console.log("this is gettting triggered")
        return (
            <div className="card-content">
            {content.image && <img src={`data:image/png;base64,${content.image}`} alt="Tool" />}
            {content.identifier && <p className="card-iden">{content.identifier}</p>}
            {content.score && <p>Score: {content.score.toFixed(3)}</p>}
            </div>
        );
    }
};

export default BodyFormatter;