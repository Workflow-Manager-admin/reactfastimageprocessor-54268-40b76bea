import React, { useRef } from 'react';

// PUBLIC_INTERFACE
function ImageUpload({ onImageSelected }) {
  const fileInput = useRef();

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onImageSelected(e.target.files[0]);
    }
  };

  // Drag events for minimal drag-and-drop support
  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onImageSelected(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => e.preventDefault();

  return (
    <div
      className="image-upload-drop"
      onClick={() => fileInput.current.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      tabIndex={0}
    >
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        ref={fileInput}
        style={{ display: 'none' }}
        onChange={handleChange}
        data-testid="file-input"
      />
      <div className="image-upload-instructions">
        <span role="img" aria-label="upload" style={{ fontSize: 32 }}>📤</span>
        <div>Click or Drag & Drop Image Here</div>
        <div style={{ fontSize: 13, color: '#999', marginTop: 4 }}>
          Supported: JPEG, PNG, WEBP
        </div>
      </div>
    </div>
  );
}

export default ImageUpload;
