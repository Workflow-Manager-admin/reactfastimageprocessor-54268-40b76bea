import React from 'react';

const SUPPORTED_FORMATS = ['jpeg', 'png', 'webp'];
const SUPPORTED_FILTERS = ['BLUR', 'CONTOUR', 'DETAIL', 'EDGE_ENHANCE', 'SHARPEN', 'SMOOTH'];

// PUBLIC_INTERFACE
function OptionsSidebar({ options, setOptions, onProcess, hasImage }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-content">
        <h3 className="sidebar-title" style={{ color: '#ff5062' }}>Processing Options</h3>
        <div className="option-group">
          <label>Resize (Width x Height)</label>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              type="number"
              min="1"
              placeholder="Width"
              value={options.width}
              onChange={e => setOptions(o => ({ ...o, width: e.target.value }))}
              className="opt-input"
            />
            <input
              type="number"
              min="1"
              placeholder="Height"
              value={options.height}
              onChange={e => setOptions(o => ({ ...o, height: e.target.value }))}
              className="opt-input"
            />
          </div>
        </div>
        <div className="option-group">
          <label>Format</label>
          <select
            value={options.format}
            onChange={e => setOptions(o => ({ ...o, format: e.target.value }))}
            className="opt-input"
          >
            <option value="">(keep original)</option>
            {SUPPORTED_FORMATS.map(f => (
              <option key={f} value={f}>{f.toUpperCase()}</option>
            ))}
          </select>
        </div>
        <div className="option-group">
          <label>Filter</label>
          <select
            value={options.filter}
            onChange={e => setOptions(o => ({ ...o, filter: e.target.value }))}
            className="opt-input"
          >
            <option value="">None</option>
            {SUPPORTED_FILTERS.map(f => (
              <option key={f} value={f}>{f}</option>
            ))}
          </select>
        </div>
        <button
          className="btn btn-large"
          disabled={!hasImage}
          onClick={onProcess}
          style={{ marginTop: 12, background: hasImage ? '#ff5062' : '#ccc', cursor: hasImage ? 'pointer' : 'not-allowed' }}
        >
          Process Image
        </button>
      </div>
    </aside>
  );
}

export default OptionsSidebar;
