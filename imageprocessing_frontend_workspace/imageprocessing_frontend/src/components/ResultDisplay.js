import React from 'react';

// PUBLIC_INTERFACE
function ResultDisplay({ resultUrl, onDownload }) {
  if (!resultUrl) return null;
  return (
    <div className="image-preview">
      <div className="preview-label">Processed Result</div>
      <img src={resultUrl} alt="Processed" style={{ boxShadow: "0 0 8px #ff5062" }} />
      <button className="btn btn-large" style={{ marginTop: 10, background: "#ff5062" }} onClick={onDownload}>
        Download
      </button>
    </div>
  );
}
export default ResultDisplay;
