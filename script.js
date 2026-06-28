// script.js - Premium AI Operating System UI Engine

const API_BASE = "http://localhost:8502/api";

// Specialist Roster Data
const AGENTS = {
  neo: {
    name: "NEO",
    role: "Professional CEO",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&h=120&q=80",
    status: "idle",
    activity: "Ready to coordinate operations",
    energy: 100,
    confidence: 98,
    memory: "64 MB",
    model: "gemini-2.5-flash",
    eta: "Instant",
    goal: "Supervise execution pipeline",
    active: true
  },
  atlas: {
    name: "ATLAS",
    role: "Lead Planner",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=120&h=120&q=80",
    status: "idle",
    activity: "Optimizing pipeline layouts",
    energy: 95,
    confidence: 94,
    memory: "128 MB",
    model: "llama3.1:8b",
    eta: "Ready",
    goal: "Decompose incoming goals",
    active: true
  },
  orion: {
    name: "ORION",
    role: "Research Scientist",
    avatar: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=120&h=120&q=80",
    status: "sleep",
    activity: "Indexing documentation sources",
    energy: 60,
    confidence: 96,
    memory: "256 MB",
    model: "mistral:7b",
    eta: "Offline",
    goal: "Information retrieval",
    active: true
  },
  apex: {
    name: "APEX",
    role: "Software Engineer",
    avatar: "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=120&h=120&q=80",
    status: "working",
    activity: "Writing microservices...",
    energy: 88,
    confidence: 92,
    memory: "512 MB",
    model: "qwen3:8b",
    eta: "2.4m remaining",
    goal: "Write clean code modules",
    active: true
  },
  lumina: {
    name: "LUMINA",
    role: "Communication Lead",
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=120&h=120&q=80",
    status: "idle",
    activity: "Monitoring output formats",
    energy: 90,
    confidence: 97,
    memory: "96 MB",
    model: "gemini-2.5-flash",
    eta: "Ready",
    goal: "Compile executive summary",
    active: true
  },
  judge: {
    name: "JUDGE",
    role: "Reviewer",
    avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=120&h=120&q=80",
    status: "idle",
    activity: "Standing by for reviews",
    energy: 99,
    confidence: 99,
    memory: "160 MB",
    model: "gemini-2.5-flash",
    eta: "Ready",
    goal: "Validate agent outputs",
    active: true
  },
  oracle: {
    name: "ORACLE",
    role: "QA Engineer",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=120&h=120&q=80",
    status: "sleep",
    activity: "Idle in sandbox room",
    energy: 40,
    confidence: 95,
    memory: "128 MB",
    model: "phi3:medium",
    eta: "Offline",
    goal: "Unit test validation",
    active: true
  },
  nova: {
    name: "NOVA",
    role: "DevOps Engineer",
    avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=120&h=120&q=80",
    status: "idle",
    activity: "Checking server container metrics",
    energy: 85,
    confidence: 91,
    memory: "192 MB",
    model: "phi3:medium",
    eta: "Ready",
    goal: "Deploy container services",
    active: true
  },
  cipher: {
    name: "CIPHER",
    role: "Security Architect",
    avatar: "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=120&h=120&q=80",
    status: "working",
    activity: "Scanning ports for vulnerabilities",
    energy: 92,
    confidence: 98,
    memory: "256 MB",
    model: "qwen3:8b",
    eta: "Continuous",
    goal: "Firewall rule auditing",
    active: true
  }
};

let devModeEnabled = false;
let logPollInterval = null;

// Initialize app elements
document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  
  // Render agents list
  renderAgentGrid();
  
  // Start simulation of metrics and statuses
  startSimulation();
  
  // Fetch real agent status from local server
  syncAgentStates();
  
  // Auto-resize chat input text-area
  const chatInput = document.getElementById("chat-input");
  chatInput.addEventListener("input", function() {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
  });
});

// Show dashboard
function showDashboard() {
  document.getElementById("landing-hero").classList.remove("active");
  document.getElementById("landing-hero").classList.add("hidden");
  document.getElementById("command-center").classList.remove("hidden");
  document.getElementById("command-center").classList.add("active");
  
  addFeedItem("System", "Ready", "Main Command Center initiated.");
}

// Show landing page
function showLanding() {
  document.getElementById("command-center").classList.remove("active");
  document.getElementById("command-center").classList.add("hidden");
  document.getElementById("landing-hero").classList.remove("hidden");
  document.getElementById("landing-hero").classList.add("active");
}

// Render roster cards
function renderAgentGrid() {
  const grid = document.getElementById("agent-grid");
  grid.innerHTML = "";
  
  Object.keys(AGENTS).forEach(key => {
    const agent = AGENTS[key];
    const card = document.createElement("div");
    card.id = `card-${key}`;
    card.className = `agent-card-premium state-${agent.status}`;
    
    card.innerHTML = `
      <div class="agent-header-row">
        <div class="agent-avatar-container">
          <img src="${agent.avatar}" class="agent-avatar-premium" alt="${agent.name}" />
          <div class="presence-dot"></div>
        </div>
        <div class="agent-title-col">
          <div class="agent-name-premium">${agent.name}</div>
          <div class="agent-role-premium">${agent.role}</div>
        </div>
        <div class="agent-toggle-switch">
          <label class="switch">
            <input type="checkbox" id="toggle-${key}" ${agent.active ? 'checked' : ''} onchange="toggleAgentSwitch('${key}')" />
            <span class="slider"></span>
          </label>
        </div>
      </div>
      
      <div class="agent-metrics-grid">
        <div class="agent-metric-item">
          <span class="metric-label-small">MEMORY</span>
          <span class="metric-val-small">${agent.memory}</span>
        </div>
        <div class="agent-metric-item">
          <span class="metric-label-small">MODEL</span>
          <span class="metric-val-small">${agent.model}</span>
        </div>
      </div>
      
      <div class="agent-progress-row">
        <div class="progress-label-bar">
          <span>Energy</span>
          <span id="energy-val-${key}">${agent.energy}%</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" id="energy-bar-${key}" style="width: ${agent.energy}%"></div>
        </div>
      </div>
      
      <div class="agent-progress-row">
        <div class="progress-label-bar">
          <span>Confidence</span>
          <span>${agent.confidence}%</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${agent.confidence}%; background-color: var(--secondary)"></div>
        </div>
      </div>
      
      <div class="agent-activity-box">
        <span class="activity-status-lbl">CURRENT ACTIVITY</span>
        <div class="activity-text" id="activity-text-${key}">${agent.activity}</div>
      </div>
    `;
    grid.appendChild(card);
  });
  
  updateActiveCount();
}

// Update count of active agents
function updateActiveCount() {
  const activeCount = Object.values(AGENTS).filter(a => a.active).length;
  document.getElementById("roster-active-count").textContent = `${activeCount} Active`;
  document.getElementById("hud-agents").textContent = `${activeCount} / 9`;
}

// Toggle agent switch in UI
function toggleAgentSwitch(key) {
  const toggle = document.getElementById(`toggle-${key}`);
  const isActive = toggle.checked;
  AGENTS[key].active = isActive;
  
  if (!isActive) {
    updateAgentStatus(key, "offline", "Deactivated by system administrator");
  } else {
    updateAgentStatus(key, "idle", "Activated and standing by");
  }
  
  updateActiveCount();
  
  // Call backend toggle endpoint
  fetch(`${API_BASE}/agents/toggle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ agent: key, active: isActive })
  })
  .then(res => res.json())
  .catch(err => console.error("Error toggling agent state in backend:", err));
}

// Update agent status & class
function updateAgentStatus(key, status, activity = null) {
  const agent = AGENTS[key];
  if (!agent) return;
  
  agent.status = status;
  if (activity) agent.activity = activity;
  
  const card = document.getElementById(`card-${key}`);
  if (card) {
    card.className = `agent-card-premium state-${status}`;
    const actText = document.getElementById(`activity-text-${key}`);
    if (actText && activity) actText.textContent = activity;
  }
}

// Sync states with real backend registry
function syncAgentStates() {
  fetch(`${API_BASE}/agents`)
    .then(res => res.json())
    .then(data => {
      // Data format: { "agents": [ { "name": "neo", "active": true, "role": "..." } ] }
      if (data && data.agents) {
        data.agents.forEach(backendAgent => {
          const key = backendAgent.name.toLowerCase();
          if (AGENTS[key]) {
            AGENTS[key].active = backendAgent.active;
            const toggle = document.getElementById(`toggle-${key}`);
            if (toggle) toggle.checked = backendAgent.active;
            
            if (!backendAgent.active) {
              updateAgentStatus(key, "offline", "Deactivated in system panel");
            } else if (AGENTS[key].status === "offline") {
              updateAgentStatus(key, "idle", "Activated and standing by");
            }
          }
        });
        updateActiveCount();
      }
    })
    .catch(err => console.error("Failed to query agents list from backend server:", err));
}

// Toggle Developer Mode display
function toggleDeveloperMode() {
  devModeEnabled = !devModeEnabled;
  const btn = document.getElementById("dev-mode-btn");
  const area = document.getElementById("developer-log-area");
  
  if (devModeEnabled) {
    btn.classList.add("active");
    area.classList.remove("hidden");
    startPollingLogs();
  } else {
    btn.classList.remove("active");
    area.classList.add("hidden");
    stopPollingLogs();
  }
}

// Clear local developer logs view
function clearDevLogs() {
  document.getElementById("dev-log-content").textContent = "";
}

// Start polling backend logs
function startPollingLogs() {
  if (logPollInterval) clearInterval(logPollInterval);
  pollLogs();
  logPollInterval = setInterval(pollLogs, 1500);
}

// Stop polling backend logs
function stopPollingLogs() {
  if (logPollInterval) {
    clearInterval(logPollInterval);
    logPollInterval = null;
  }
}

// Poll logs
function pollLogs() {
  fetch(`${API_BASE}/logs`)
    .then(res => res.json())
    .then(data => {
      if (data && data.logs) {
        const logContent = document.getElementById("dev-log-content");
        logContent.textContent = data.logs;
        logContent.scrollTop = logContent.scrollHeight;
      }
    })
    .catch(err => console.error("Failed to poll execution logs:", err));
}

// Simulate system metrics fluctuations
function startSimulation() {
  // Fluctuate CPU
  setInterval(() => {
    const cpu = Math.floor(15 + Math.random() * 25);
    document.getElementById("hud-cpu").textContent = `${cpu} %`;
  }, 3000);
  
  // Fluctuate RAM
  setInterval(() => {
    const ram = (5.8 + Math.random() * 0.9).toFixed(1);
    document.getElementById("hud-ram").textContent = `${ram} GB`;
  }, 4000);
  
  // Fluctuate Latency
  setInterval(() => {
    const lat = (1.5 + Math.random() * 2.5).toFixed(2);
    document.getElementById("hud-latency").textContent = `${lat} s`;
  }, 5000);

  // Slow random status fluctuations for simulated agents (like oracle, nova, cipher) to make them feel alive
  setInterval(() => {
    const simulated = ["oracle", "nova", "cipher", "orion"];
    const randomKey = simulated[Math.floor(Math.random() * simulated.length)];
    const agent = AGENTS[randomKey];
    
    if (agent && agent.active) {
      const statuses = ["idle", "working", "sleep"];
      const newStatus = statuses[Math.floor(Math.random() * statuses.length)];
      
      let activity = "";
      if (newStatus === "working") {
        activity = randomKey === "cipher" ? "Refactoring firewall settings..." : "Analyzing database partitions...";
      } else if (newStatus === "sleep") {
        activity = "Power conserving / resting";
      } else {
        activity = "Standing by for requests";
      }
      
      // Randomly deplete/charge energy
      const energyDelta = newStatus === "sleep" ? 10 : -5;
      agent.energy = Math.max(20, Math.min(100, agent.energy + energyDelta));
      const energyBar = document.getElementById(`energy-bar-${randomKey}`);
      const energyVal = document.getElementById(`energy-val-${randomKey}`);
      if (energyBar) energyBar.style.width = `${agent.energy}%`;
      if (energyVal) energyVal.textContent = `${agent.energy}%`;
      
      updateAgentStatus(randomKey, newStatus, activity);
      
      // Randomly log in Operations Feed
      if (Math.random() > 0.5) {
        addFeedItem(agent.name, newStatus, activity);
      }
    }
  }, 12000);
}

// Add operations feed entry
function addFeedItem(agentName, status, message) {
  const list = document.getElementById("activity-feed-list");
  const item = document.createElement("div");
  item.className = "feed-item";
  
  const time = new Date().toTimeString().split(' ')[0];
  const badgeClass = `badge-${agentName.toLowerCase()}`;
  
  item.innerHTML = `
    <span class="feed-time">${time}</span>
    <span class="feed-agent-badge ${badgeClass}">${agentName.toUpperCase()}</span>
    <span class="feed-message">${message}</span>
  `;
  
  list.appendChild(item);
  list.scrollTop = list.scrollHeight;
  
  // Cap list size
  while (list.children.length > 25) {
    list.removeChild(list.firstChild);
  }
}

// Highlight step in pipeline visualization
function highlightPipelineNode(nodeId) {
  const nodes = document.querySelectorAll(".pipeline-flow .node");
  nodes.forEach(n => n.classList.remove("active"));
  
  const target = document.getElementById(nodeId);
  if (target) target.classList.add("active");
}

// Reset pipeline visualization
function resetPipeline() {
  const nodes = document.querySelectorAll(".pipeline-flow .node");
  nodes.forEach(n => n.classList.remove("active"));
  document.getElementById("node-user").classList.add("active");
}

// Copy Code Block Utility
function copyToClipboard(button, text) {
  navigator.clipboard.writeText(text).then(() => {
    button.textContent = "Copied!";
    setTimeout(() => {
      button.textContent = "Copy";
    }, 2000);
  });
}

// Append Chat Message
function appendChatMessage(sender, content, isHtml = false) {
  const chatMessages = document.getElementById("chat-messages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `chat-message ${sender}`;
  
  const avatar = sender === "user" ? "👤" : "⚡";
  
  messageDiv.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content">${isHtml ? content : formatMarkdown(content)}</div>
  `;
  
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Simple Markdown formatting parser (supporting code blocks, headers, strong)
function formatMarkdown(text) {
  if (!text) return "";
  
  // Format code blocks
  let formatted = text.replace(/```([\s\S]*?)```/g, (match, code) => {
    // Escape HTML
    const escapedCode = code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return `<pre><button class="copy-code-btn" onclick="copyToClipboard(this, \`${escapedCode.trim().replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">Copy</button><code>${escapedCode.trim()}</code></pre>`;
  });
  
  // Format headers
  formatted = formatted.replace(/^### (.*$)/gim, '<h5>$1</h5>');
  formatted = formatted.replace(/^## (.*$)/gim, '<h4>$1</h4>');
  formatted = formatted.replace(/^# (.*$)/gim, '<h3>$1</h3>');
  
  // Format bold text
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Format lists
  formatted = formatted.replace(/^\s*\-\s*(.*$)/gim, '<li>$1</li>');
  
  // Convert newlines to breaks
  formatted = formatted.replaceAll("\n", "<br/>");
  
  return formatted;
}

// Dispatch User Goal to backend API
function dispatchGoal() {
  const input = document.getElementById("chat-input");
  const goalText = input.value.trim();
  if (!goalText) return;
  
  // Clear input field
  input.value = "";
  input.style.height = "auto";
  
  // Append user message to chat
  appendChatMessage("user", goalText);
  
  // Start pipeline animation
  highlightPipelineNode("node-neo");
  updateAgentStatus("neo", "working", "Decomposing task and orchestrating resources");
  addFeedItem("NEO", "working", `Initiating mission: "${goalText.substring(0, 40)}..."`);
  
  // Disable send button
  const sendBtn = document.getElementById("btn-send-task");
  sendBtn.disabled = true;
  
  // Show typing loader
  const chatMessages = document.getElementById("chat-messages");
  const loaderDiv = document.createElement("div");
  loaderDiv.id = "chat-typing-loader";
  loaderDiv.className = "chat-message assistant";
  loaderDiv.innerHTML = `
    <div class="message-avatar">⚡</div>
    <div class="message-content">
      <div class="animated-sub">Connecting...</div>
    </div>
  `;
  chatMessages.appendChild(loaderDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Track executing agents sequentially in UI for visual feedback
  const pipelineSteps = [
    { node: "node-atlas", agent: "atlas", status: "planning", activity: "Formulating workflow blueprint..." },
    { node: "node-orion", agent: "orion", status: "working", activity: "Searching local repositories and reference documentation..." },
    { node: "node-apex", agent: "apex", status: "working", activity: "Generating program logic..." },
    { node: "node-judge", agent: "judge", status: "working", activity: "Running code validation audits..." },
    { node: "node-lumina", agent: "lumina", status: "working", activity: "Structuring executive summaries..." }
  ];

  // Set to Thinking... after Connecting...
  setTimeout(() => {
    const subText = loaderDiv.querySelector(".animated-sub");
    if (subText && subText.textContent === "Connecting...") {
      subText.textContent = "Thinking...";
    }
  }, 1000);

  let stepIdx = 0;
  const pipelineInterval = setInterval(() => {
    if (stepIdx < pipelineSteps.length) {
      const step = pipelineSteps[stepIdx];
      highlightPipelineNode(step.node);
      updateAgentStatus(step.agent, step.status, step.activity);
      addFeedItem(AGENTS[step.agent].name, step.status, step.activity);
      
      // Update loader status text dynamically
      const subText = loaderDiv.querySelector(".animated-sub");
      if (subText) {
        if (step.agent === "atlas") {
          subText.textContent = "Planning...";
        } else if (step.agent === "orion" || step.agent === "apex" || step.agent === "judge") {
          subText.textContent = "Executing...";
        } else if (step.agent === "lumina") {
          subText.textContent = "Formatting...";
        }
      }
      
      stepIdx++;
    } else {
      clearInterval(pipelineInterval);
    }
  }, 3500);

  // Define streaming progress handler
  function handleProgressEvent(eventObj) {
    const { event, data } = eventObj;
    const subText = loaderDiv.querySelector(".animated-sub");
    
    if (event === "stage_started") {
      if (data.stage === "classification") {
        if (subText) subText.textContent = "Connecting...";
      } else if (data.stage === "formatting") {
        if (subText) subText.textContent = "Formatting...";
        highlightPipelineNode("node-lumina");
        updateAgentStatus("lumina", "working", "Structuring executive summary...");
        addFeedItem("LUMINA", "working", "Structuring executive summary...");
      }
    }
    else if (event === "classification_complete") {
      if (subText) subText.textContent = "Thinking...";
      updateAgentStatus("neo", "working", "Decomposing task and orchestrating resources");
      addFeedItem("NEO", "working", `Initiating mission, classified category: ${data.category}`);
    }
    else if (event === "planning_complete") {
      if (subText) subText.textContent = "Planning...";
      highlightPipelineNode("node-atlas");
      updateAgentStatus("atlas", "planning", "Formulating workflow blueprint...");
      addFeedItem("ATLAS", "planning", "Formulating workflow blueprint...");
    }
    else if (event === "research_complete") {
      if (subText) subText.textContent = "Executing...";
      highlightPipelineNode("node-orion");
      updateAgentStatus("orion", "working", "Searching local repositories and reference documentation...");
      addFeedItem("ORION", "working", "Searching local repositories and reference documentation...");
    }
    else if (event === "formatting_complete") {
      clearInterval(pipelineInterval);
      if (subText) subText.textContent = "Completed";
      
      // Remove loader after a brief delay
      setTimeout(() => {
        const loader = document.getElementById("chat-typing-loader");
        if (loader) loader.remove();
      }, 500);
      
      // Finalize pipeline nodes
      highlightPipelineNode("node-response");
      addFeedItem("System", "success", `Mission completed successfully in ${data.elapsed.toFixed(2)}s.`);
      
      // Reset agent status
      Object.keys(AGENTS).forEach(key => {
        if (AGENTS[key].active && AGENTS[key].status !== "offline") {
          updateAgentStatus(key, "idle", "Standing by for requests");
        }
      });
      
      // Append answer to chat
      appendChatMessage("assistant", data.result || "Mission accomplished, but no summary was generated.");
      
      // Reset pipeline visualizer after 5s
      setTimeout(resetPipeline, 5000);
      
      // Re-enable send button
      sendBtn.disabled = false;
    }
    else if (event === "error") {
      clearInterval(pipelineInterval);
      const loader = document.getElementById("chat-typing-loader");
      if (loader) loader.remove();
      
      highlightPipelineNode("node-response");
      addFeedItem("System", "danger", `Mission failed: ${data.error}`);
      
      Object.keys(AGENTS).forEach(key => {
        if (AGENTS[key].active && AGENTS[key].status !== "offline") {
          updateAgentStatus(key, "idle", "Standing by for requests");
        }
      });
      
      appendChatMessage("assistant", `❌ **Mission Failed**\n\nOrchestration failed during workflow dispatch.\n\nError details:\n\`\`\`\n${data.error}\n\`\`\``);
      sendBtn.disabled = false;
      setTimeout(resetPipeline, 5000);
    }
  }

  // Send request to API
  fetch(`${API_BASE}/dispatch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal: goalText })
  })
  .then(res => {
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    
    function processEvents(text) {
      buffer += text;
      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // Keep partial line
      
      for (const line of lines) {
        if (line.trim().startsWith("data: ")) {
          try {
            const rawJson = line.substring(6).trim();
            const eventObj = JSON.parse(rawJson);
            handleProgressEvent(eventObj);
          } catch (e) {
            console.error("Failed to parse event JSON:", e, line);
          }
        }
      }
    }
    
    function read() {
      return reader.read().then(({ done, value }) => {
        if (done) {
          if (buffer) {
            processEvents("");
          }
          return;
        }
        const text = decoder.decode(value, { stream: true });
        processEvents(text);
        return read();
      });
    }
    
    return read();
  })
  .catch(err => {
    clearInterval(pipelineInterval);
    console.error("Error dispatching goal:", err);
    
    const loader = document.getElementById("chat-typing-loader");
    if (loader) loader.remove();
    
    highlightPipelineNode("node-response");
    addFeedItem("System", "danger", `Mission failed: ${err.message}`);
    
    Object.keys(AGENTS).forEach(key => {
      if (AGENTS[key].active && AGENTS[key].status !== "offline") {
        updateAgentStatus(key, "idle", "Standing by for requests");
      }
    });
    
    appendChatMessage("assistant", `❌ **Mission Failed**\n\nOrchestration failed during workflow dispatch.\n\nError details:\n\`\`\`\n${err.message}\n\`\`\``);
    sendBtn.disabled = false;
    setTimeout(resetPipeline, 5000);
  });
}
