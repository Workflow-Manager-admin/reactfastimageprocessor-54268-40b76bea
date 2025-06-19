import React from 'react';

// PUBLIC_INTERFACE
function ImagePreview({ src }) {
  if (!src) return null;
  return (
    <div className="image-preview">
      <div className="preview-label">Image Preview</div>
      <img src={src} alt="Preview" />
    </div>
  );
}
export default ImagePreview;
