// REST API Client Module
const API = {
  async fetchImages() {
    const res = await fetch('/api/images');
    if (!res.ok) throw new Error('Failed to fetch sample images');
    return res.json();
  },

  async startRun(imageFilename) {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_filename: imageFilename })
    });
    if (!res.ok) throw new Error('Failed to start run');
    return res.json();
  },

  async submitApproval(runId, approved, operatorNotes = '') {
    const res = await fetch(`/api/approve/${runId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved, operator_notes: operatorNotes })
    });
    if (!res.ok) throw new Error('Failed to submit approval');
    return res.json();
  },

  async getLogs(runId) {
    const res = await fetch(`/api/logs/${runId}`);
    if (!res.ok) throw new Error('Failed to fetch logs');
    return res.json();
  }
};
