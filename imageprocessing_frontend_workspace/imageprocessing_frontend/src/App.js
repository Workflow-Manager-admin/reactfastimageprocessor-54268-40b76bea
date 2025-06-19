import React, { useState } from 'react';
import './App.css';
import ImageUpload from './components/ImageUpload';
import OptionsSidebar from './components/OptionsSidebar';
import ImagePreview from './components/ImagePreview';
import ResultDisplay from './components/ResultDisplay';

// Core layout: navbar, sidebar, main preview/result.
// Manages all image state and API interaction.

function App() {
  // Uploaded image file and preview URL
  const [uploadedFile, setUploadedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  // Filename as returned by backend
  const [filename, setFilename] = useState(null);

  // Selected processing options
  const [options, setOptions] = useState({
    width: '',
    height: '',
    format: '',
    filter: ''
  });

  // Processed image URL (blob/object URL)
  const [resultUrl, setResultUrl] = useState(null);

  // Upload handler
  const handleImageUpload = (file) => {
    setUploadedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResultUrl(null);
    setFilename(null);
  };

  // Send file to backend for upload
  const handleUploadToBackend = async () => {
    if (!uploadedFile) return;
    const data = new FormData();
    data.append('file', uploadedFile);

    try {
      const resp = await fetch('http://localhost:3001/upload', {
        method: 'POST',
        body: data
      });
      const json = await resp.json();
      setFilename(json.filename);
      return json.filename;
    } catch {
      alert('Upload failed');
    }
  };

  // Processing request
  const handleProcess = async () => {
    // Ensure file is uploaded, get backend filename
    let backendFilename = filename;
    if (!backendFilename) {
      backendFilename = await handleUploadToBackend();
      if (!backendFilename) return;
    }
    // Build query params for options
    const params = [];
    if (options.width) params.push(`width=${options.width}`);
    if (options.height) params.push(`height=${options.height}`);
    if (options.format) params.push(`format=${options.format}`);
    if (options.filter) params.push(`filter=${options.filter}`);

    const url = `http://localhost:3001/process/${backendFilename}${
      params.length ? '?' + params.join('&') : ''
    }`;

    try {
      const resp = await fetch(url, { method: 'POST' });
      if (!resp.ok) throw new Error('Processing failed');
      const blob = await resp.blob();
      setResultUrl(URL.createObjectURL(blob));
    } catch {
      alert('Image processing failed');
    }
  };

  // Download result
  const handleDownload = () => {
    if (!resultUrl) return;
    const link = document.createElement('a');
    link.href = resultUrl;
    link.download = 'processed_image';
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="app">
      <nav className="navbar">
        <div className="container" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div className="logo"><span className="logo-symbol">*</span> AI Image Processor</div>
          <span style={{ color: "#ff5062", fontWeight: 500 }}>Dashboard</span>
        </div>
      </nav>
      <main className="main-panel">
        <OptionsSidebar
          options={options}
          setOptions={setOptions}
          onProcess={handleProcess}
          hasImage={!!uploadedFile}
        />
        <section className="dashboard-content">
          <ImageUpload onImageSelected={handleImageUpload} />
          <ImagePreview src={previewUrl} />
          <ResultDisplay resultUrl={resultUrl} onDownload={handleDownload} />
        </section>
      </main>
    </div>
  );
}

export default App;
