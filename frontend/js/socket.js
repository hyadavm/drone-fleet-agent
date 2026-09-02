// WebSocket Client Manager
class StreamSocket {
  constructor(runId, onMessageCallback) {
    this.runId = runId;
    this.onMessage = onMessageCallback;
    this.ws = null;
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${this.runId}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log(`[WS] Connected to stream for run ${this.runId}`);
    };

    this.ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (this.onMessage) this.onMessage(payload);
      } catch (err) {
        console.error('[WS] Error parsing message:', err);
      }
    };

    this.ws.onerror = (err) => {
      console.error('[WS] Error:', err);
    };

    this.ws.onclose = () => {
      console.log(`[WS] Disconnected from run ${this.runId}`);
    };
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  close() {
    if (this.ws) this.ws.close();
  }
}
