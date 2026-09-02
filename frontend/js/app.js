// Main UI Application Controller
document.addEventListener('DOMContentLoaded', () => {
  const imageSelect = document.getElementById('image-select');
  const thumbnailGallery = document.getElementById('thumbnail-gallery');
  const activeImage = document.getElementById('active-image');
  const imagePlaceholder = document.getElementById('image-placeholder');
  const runBtn = document.getElementById('run-btn');
  
  const runStatusBadge = document.getElementById('run-status-badge');
  const timeline = document.getElementById('timeline');
  
  const hitlBanner = document.getElementById('hitl-banner');
  const hitlProposedAction = document.getElementById('hitl-proposed-action');
  const hitlReasoning = document.getElementById('hitl-reasoning');
  const operatorNotesInput = document.getElementById('operator-notes');
  const approveBtn = document.getElementById('approve-btn');
  const rejectBtn = document.getElementById('reject-btn');

  const resultCard = document.getElementById('result-card');
  const finalStatusBadge = document.getElementById('final-status-badge');
  const resDefectType = document.getElementById('res-defect-type');
  const resSeverity = document.getElementById('res-severity');
  const resToolName = document.getElementById('res-tool-name');
  const resFinalAction = document.getElementById('res-final-action');
  const toolPayloadJson = document.getElementById('tool-payload-json');

  let currentRunId = null;
  let activeSocket = null;
  let sampleImagesList = [];

  // Initialize Sample Images Dropdown & Thumbnails
  async function init() {
    try {
      const data = await API.fetchImages();
      sampleImagesList = data.images || [];
      
      imageSelect.innerHTML = '<option value="" disabled selected>Select aerial sample photo...</option>';
      thumbnailGallery.innerHTML = '';

      sampleImagesList.forEach((img, idx) => {
        // Dropdown option
        const opt = document.createElement('option');
        opt.value = img.filename;
        opt.textContent = `${img.title}`;
        imageSelect.appendChild(opt);

        // Gallery thumbnail
        const thumb = document.createElement('img');
        thumb.src = img.url;
        thumb.alt = img.title;
        thumb.className = 'thumb-item';
        thumb.dataset.filename = img.filename;
        thumb.addEventListener('click', () => selectImage(img.filename));
        thumbnailGallery.appendChild(thumb);
      });

      // Auto-select first image
      if (sampleImagesList.length > 0) {
        selectImage(sampleImagesList[0].filename);
      }
    } catch (err) {
      console.error('Failed to load sample images:', err);
    }
  }

  function selectImage(filename) {
    imageSelect.value = filename;
    const selected = sampleImagesList.find(i => i.filename === filename);
    if (selected) {
      activeImage.src = selected.url;
      activeImage.classList.remove('hidden');
      imagePlaceholder.classList.add('hidden');
      runBtn.disabled = false;

      // Update thumbnail active states
      document.querySelectorAll('.thumb-item').forEach(t => {
        t.classList.toggle('active', t.dataset.filename === filename);
      });
    }
  }

  imageSelect.addEventListener('change', (e) => selectImage(e.target.value));

  // Run Workflow Handler
  runBtn.addEventListener('click', async () => {
    const selectedFilename = imageSelect.value;
    if (!selectedFilename) return;

    // Reset UI state
    runBtn.disabled = true;
    runStatusBadge.textContent = 'RUNNING';
    runStatusBadge.className = 'badge badge-active';
    timeline.innerHTML = '';
    hitlBanner.classList.add('hidden');
    resultCard.classList.add('hidden');

    try {
      const runData = await API.startRun(selectedFilename);
      currentRunId = runData.run_id;

      // Connect WebSocket
      if (activeSocket) activeSocket.close();
      activeSocket = new StreamSocket(currentRunId, handleStreamEvent);
      activeSocket.connect();

    } catch (err) {
      alert(`Error starting inspection: ${err.message}`);
      runBtn.disabled = false;
      runStatusBadge.textContent = 'ERROR';
      runStatusBadge.className = 'badge badge-idle';
    }
  });

  // Handle live WebSocket event stream
  function handleStreamEvent(event) {
    const { step, message, data } = event;

    // Add entry to timeline
    addTimelineItem(step, message, data);

    if (step === 'AWAITING_HUMAN_APPROVAL') {
      runStatusBadge.textContent = 'AWAITING APPROVAL';
      runStatusBadge.className = 'badge badge-warning';
      showHITLBanner(data);
    } 
    else if (step === 'HITL_RESPONSE') {
      hitlBanner.classList.add('hidden');
    }
    else if (step === 'WORKFLOW_COMPLETE') {
      runStatusBadge.textContent = 'COMPLETED';
      runStatusBadge.className = 'badge badge-success';
      runBtn.disabled = false;
      showFinalResult(data);
    }
    else if (step === 'ERROR') {
      runStatusBadge.textContent = 'FAILED';
      runStatusBadge.className = 'badge badge-idle';
      runBtn.disabled = false;
    }
  }

  function addTimelineItem(step, message, data) {
    const item = document.createElement('div');
    let category = 'perception';
    
    if (step.includes('RAG')) category = 'rag';
    else if (step.includes('PLAN')) category = 'planning';
    else if (step.includes('HITL')) category = 'hitl';
    else if (step.includes('EXECUTION') || step.includes('WORKFLOW')) category = 'execution';

    item.className = `timeline-item ${category}`;
    
    let extraHtml = '';
    if (step === 'RAG_COMPLETE' && data && data.snippet) {
      extraHtml = `<div class="snippet-box">${escapeHtml(data.snippet)}</div>`;
    }

    item.innerHTML = `
      <div class="timeline-content">
        <h4>${step.replace(/_/g, ' ')}</h4>
        <p>${escapeHtml(message)}</p>
        ${extraHtml}
      </div>
    `;

    timeline.appendChild(item);
    item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function showHITLBanner(pendingData) {
    hitlBanner.classList.remove('hidden');
    hitlProposedAction.textContent = `Proposed Action: ${pendingData.proposed_action}`;
    hitlReasoning.textContent = `Reason: ${pendingData.reasoning}`;
    operatorNotesInput.value = '';
    hitlBanner.scrollIntoView({ behavior: 'smooth' });
  }

  // Approval / Rejection Listeners
  approveBtn.addEventListener('click', async () => {
    if (!currentRunId) return;
    const notes = operatorNotesInput.value;
    try {
      await API.submitApproval(currentRunId, true, notes);
      hitlBanner.classList.add('hidden');
    } catch (err) {
      alert(`Approval error: ${err.message}`);
    }
  });

  rejectBtn.addEventListener('click', async () => {
    if (!currentRunId) return;
    const notes = operatorNotesInput.value;
    try {
      await API.submitApproval(currentRunId, false, notes);
      hitlBanner.classList.add('hidden');
    } catch (err) {
      alert(`Rejection error: ${err.message}`);
    }
  });

  function showFinalResult(summaryData) {
    resultCard.classList.remove('hidden');
    const vlm = summaryData.vlm_summary || {};
    const plan = summaryData.plan_summary || {};
    const tool = summaryData.tool_result || {};

    resDefectType.textContent = vlm.defect_type || '-';
    resSeverity.textContent = vlm.severity || '-';
    resToolName.textContent = plan.recommended_tool || '-';
    resFinalAction.textContent = summaryData.final_action || '-';

    toolPayloadJson.textContent = JSON.stringify(tool, null, 2);
    resultCard.scrollIntoView({ behavior: 'smooth' });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  init();
});
