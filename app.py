"""
=================================================
BharatAI Streamlit Dashboard (Sprint 3 OS)
=================================================
"""

import io
import os
import json
import time
import logging
import threading
import uuid
import urllib.parse
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver

import streamlit as st
import streamlit.components.v1 as components

from config.settings import APP_NAME, VERSION, LOG_FILE, LOG_LEVEL, ROOT_DIR
from models.manager import manager
from core.registry import registry
from services.telegram import send_telegram_message
from services.dispatch_service import execute_dispatch_workflow
from services.request_timing import (
    RequestTimingFilter,
    create_request_context,
    log_timing,
)

# -------------------------------------------------------
# LOGGING SETUP
# -------------------------------------------------------
logger = logging.getLogger("bharatai")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
if not logger.handlers:
    try:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[request_id=%(request_id)s stage=%(stage)s elapsed_ms=%(elapsed_ms)s cumulative_ms=%(cumulative_ms)s] "
            "%(message)s"
        ))
        fh.addFilter(RequestTimingFilter())
        logger.addHandler(fh)
    except Exception as e:
        print(f"Failed to set up file handler in app.py: {e}")

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[request_id=%(request_id)s stage=%(stage)s elapsed_ms=%(elapsed_ms)s cumulative_ms=%(cumulative_ms)s] "
        "%(message)s"
    ))
    sh.addFilter(RequestTimingFilter())
    logger.addHandler(sh)

# -------------------------------------------------------
# BACKGROUND API SERVER ON PORT 8502
# -------------------------------------------------------
class APIRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # FAST_MODEL = DEFAULT_MODEL  # Use default model for fast responsester
        pass

    def _begin_request_timing(self, method: str) -> tuple[str, float]:
        request_context = create_request_context(uuid.uuid4().hex)
        log_timing(
            logger,
            "http_request_received",
            request_context.start_perf,
            message=f"method={method} path={self.path}",
        )
        return request_context.request_id, request_context.start_perf

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        request_id, request_start_perf = self._begin_request_timing("GET")
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # 1. Serve Static Files
        if path in ('/', '/index.html'):
            self._send_file(os.path.join(ROOT_DIR, "index.html"), "text/html")
        elif path == '/style.css':
            self._send_file(os.path.join(ROOT_DIR, "style.css"), "text/css")
        elif path == '/script.js':
            self._send_file(os.path.join(ROOT_DIR, "script.js"), "application/javascript")
            
        # 2. Serve API Endpoints
        elif path == '/api/health':
            try:
                # 1. API Server check (this endpoint is reachable)
                api_healthy = True
                
                # 2. WorkflowEngine check
                try:
                    from core.workflow_engine import workflow_engine
                    workflow_engine_healthy = getattr(workflow_engine, "_initialized", False)
                except Exception:
                    workflow_engine_healthy = False
                
                # 3. AgentRegistry check
                try:
                    from core.registry import registry
                    agent_registry_healthy = getattr(registry, "_initialized", False)
                    registered_agents_count = len(registry.list_agents())
                except Exception:
                    agent_registry_healthy = False
                    registered_agents_count = 0
                
                # 4. ModelManager check
                try:
                    from models.manager import manager
                    model_manager_healthy = getattr(manager, "_initialized", False)
                except Exception:
                    model_manager_healthy = False
                
                # 5. Ollama provider connectivity check (lightweight)
                ollama_healthy = False
                ollama_reachable = False
                ollama_models = []
                try:
                    from models.manager import manager, OllamaProvider
                    ollama_prov = manager.providers.get("ollama")
                    if isinstance(ollama_prov, OllamaProvider):
                        import ollama
                        # Check connectivity with a quick 2.0s timeout
                        temp_client = ollama.Client(host=ollama_prov.host, timeout=2.0)
                        res = temp_client.list()
                        ollama_models = [m.model for m in res.models]
                        ollama_reachable = True
                        ollama_healthy = True
                except Exception as e:
                    logger.warning(f"Ollama health check failed in /api/health: {e}")
                
                # 6. Gemini client configuration check (without text generation)
                gemini_healthy = False
                gemini_configured = False
                try:
                    from models.manager import manager, GeminiProvider
                    gemini_prov = manager.providers.get("gemini")
                    if isinstance(gemini_prov, GeminiProvider):
                        gemini_configured = bool(gemini_prov.client)
                        if gemini_configured:
                            from google import genai
                            # Sanity check without generation (list models with 2.0s timeout)
                            temp_gemini_client = genai.Client(api_key=gemini_prov.api_key, http_options={"timeout": 2.0})
                            temp_gemini_client.models.list()
                            gemini_healthy = True
                except Exception as e:
                    logger.warning(f"Gemini health check failed in /api/health: {e}")
                
                # Overall readiness: basic systems initialization plus at least one available provider
                ready = bool(
                    api_healthy
                    and workflow_engine_healthy
                    and agent_registry_healthy
                    and model_manager_healthy
                    and (ollama_healthy or gemini_healthy)
                )
                
                self._send_json({
                    "success": True,
                    "ready": ready,
                    "components": {
                        "api": {
                            "healthy": api_healthy
                        },
                        "workflow_engine": {
                            "healthy": workflow_engine_healthy
                        },
                        "agent_registry": {
                            "healthy": agent_registry_healthy,
                            "registered_agents": registered_agents_count
                        },
                        "ollama": {
                            "healthy": ollama_healthy,
                            "reachable": ollama_reachable,
                            "available_models": ollama_models
                        },
                        "gemini": {
                            "healthy": gemini_healthy,
                            "configured": gemini_configured
                        }
                    }
                })
            except Exception as e:
                self._send_json({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "stage": "health_check"
                }, status=500)



        elif path == '/api/agents':
            try:
                agents_list = []
                for name in registry.list_agents():
                    agent = registry.get_agent(name)
                    agents_list.append({
                        "name": name,
                        "active": agent.is_active,
                        "role": agent.role
                    })
                self._send_json({"agents": agents_list})
            except Exception as e:
                self._send_json({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "stage": "list_agents"
                }, status=500)
        elif path == '/api/logs':
            try:
                log_data = ""
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        log_data = "".join(lines[-100:])
                self._send_json({"logs": log_data})
            except Exception as e:
                self._send_json({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "stage": "get_logs"
                }, status=500)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        request_id, request_start_perf = self._begin_request_timing("POST")
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            data = json.loads(post_data) if post_data else {}
        except Exception:
            data = {}

        if path == '/api/agents/toggle':
            agent_name = data.get("agent")
            active = data.get("active")
            if not agent_name:
                validation_start = time.perf_counter()
                log_timing(
                    logger,
                    "request_validation",
                    validation_start,
                    message="agent_toggle missing agent",
                )
                self._send_json({
                    "success": False,
                    "error": "Missing 'agent' parameter",
                    "traceback": "",
                    "stage": "toggle_agent"
                }, status=400)
                return
            
            try:
                validation_start = time.perf_counter()
                log_timing(
                    logger,
                    "request_validation",
                    validation_start,
                    message=f"agent_toggle agent={agent_name} active={active}",
                )
                if active:
                    registry.activate_agent(agent_name)
                else:
                    registry.deactivate_agent(agent_name)
                self._send_json({"status": "success"})
            except Exception as e:
                self._send_json({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "stage": "toggle_agent"
                }, status=500)

        elif path == '/api/dispatch':
            goal = data.get("goal")
            logger.info(f"[LOG] Request received: POST /api/dispatch. Goal: '{goal}'")
            validation_start = time.perf_counter()
            log_timing(
                logger,
                "request_validation",
                validation_start,
                message="goal_present" if goal is not None else "goal_missing",
            )
            if goal is None:
                logger.warning("[LOG] Request missing 'goal' parameter. Returning 400.")
                self._send_json({
                    "success": False,
                    "error": "Missing 'goal' parameter",
                    "traceback": "",
                    "stage": "workflow_dispatch"
                }, status=400)
                return
            
            # Set up Server-Sent Events (SSE) streaming headers
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            def send_event(event_type, payload_data):
                try:
                    serialization_start = time.perf_counter()
                    event_msg = {
                        "event": event_type,
                        "data": payload_data,
                        "timestamp": time.time()
                    }
                    chunk = f"data: {json.dumps(event_msg)}\n\n".encode('utf-8')
                    log_timing(
                        logger,
                        "sse_serialization",
                        serialization_start,
                        message=f"event={event_type}",
                    )
                    self.wfile.write(chunk)
                    self.wfile.flush()
                    log_timing(
                        logger,
                        "http_response_sent",
                        serialization_start,
                        message=f"event={event_type}",
                    )
                except Exception as e:
                    logger.error(f"Error sending SSE chunk: {e}")

            try:
                send_event("stage_started", {"stage": "classification", "message": "Connecting..."})
                
                # Define progress callback to stream stages
                def on_progress(event_type, payload):
                    if event_type in ("stage_started", "classification_complete", "research_complete", "formatting_complete", "final_answer", "end"):
                        send_event(event_type, payload)
                
                # Execute workflow
                print("HTTP")
                import sys; sys.stdout.buffer.write(b"\xe2\x86\x93\n"); sys.stdout.flush()
                logger.info("[LOG] Starting workflow execution...")
                dispatch_execution = execute_dispatch_workflow(goal, on_progress=on_progress)
                logger.info("[LOG] Workflow execution completed.")
                
                # Emit final_answer event
                send_event("final_answer", {
                    "result": dispatch_execution.formatted_output
                })
                
                # Emit end event
                send_event("end", {
                    "message": "Workflow dispatch completed."
                })
                
                # Send completion event with final result
                send_event("formatting_complete", {
                    "result": dispatch_execution.formatted_output,
                    "elapsed": dispatch_execution.elapsed
                })
                logger.info(f"[LOG] Response returned. Total execution time: {dispatch_execution.elapsed:.2f}s")
                
                # Send Telegram Notification
                try:
                    telegram_msg = f"📢 *BharatAI Mission Completed!*\n\n*Goal:* {goal}\n\n*Executive Summary:*\n{dispatch_execution.formatted_output}"
                    send_telegram_message(telegram_msg)
                except Exception as te:
                    logger.warning(f"Telegram notification failed: {te}")
                self.close_connection = True
            except Exception as e:
                logger.error(f"[LOG] Error during workflow dispatch endpoint: {e}\n{traceback.format_exc()}")
                send_event("error", {
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "stage": "workflow_dispatch"
                })
                logger.info("[LOG] Error response returned.")
                self.close_connection = True
        elif path == '/api/dispatch-json':
            goal = data.get("goal")
            logger.info(f"[LOG] Request received: POST /api/dispatch-json. Goal: '{goal}'")
            if goal is None:
                self._send_json({"success": False, "error": "Missing 'goal'"}, status=400)
                return

            # Ensure dispatch_execution is defined and handle workflow execution safely
            dispatch_execution = None
            try:
                # Execute the workflow (single point of failure)
                dispatch_execution = execute_dispatch_workflow(goal)
                # Validate the result; must not be None
                if dispatch_execution is None:
                    raise ValueError("execute_dispatch_workflow returned None")

                # Build success response preserving original fields
                self._send_json({
                    "success": True,
                    "goal": goal,
                    "result": getattr(dispatch_execution, "formatted_output", None),
                    "elapsed": getattr(dispatch_execution, "elapsed", None)
                })
            except Exception as e:
                # Log full traceback for debugging
                logger.exception("Workflow dispatch failed")
                self._send_json({
                    "success": False,
                    "error": str(e),
                    "stage": "workflow_dispatch",
                    "traceback": traceback.format_exc()
                }, status=500)
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, data, status=200):
        serialization_start = time.perf_counter()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        payload = json.dumps(data).encode('utf-8')
        log_timing(
            logger,
            "json_serialization",
            serialization_start,
            message=f"status={status}",
            bytes=len(payload),
        )
        self.wfile.write(payload)
        self.wfile.flush()
        log_timing(
            logger,
            "http_response_sent",
            serialization_start,
            message=f"status={status}",
        )

    def _send_file(self, file_path, content_type):
        try:
            serialization_start = time.perf_counter()
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            payload = content.encode('utf-8')
            log_timing(
                logger,
                "json_serialization",
                serialization_start,
                message=f"static_file={os.path.basename(file_path)}",
                bytes=len(payload),
            )
            self.wfile.write(payload)
            self.wfile.flush()
            log_timing(
                logger,
                "http_response_sent",
                serialization_start,
                message=f"static_file={os.path.basename(file_path)}",
            )
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error serving file: {e}".encode('utf-8'))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

def start_api_server():
    server_address = ('', 8502)
    logger.info("Starting background API server on port 8502...")
    try:
        httpd = ThreadedHTTPServer(server_address, APIRequestHandler)
        logger.info("API server bound and serving on port 8502.")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"API server failed to start: {e}")

# Start the server thread exactly once using Streamlit session tracking in a background daemon thread
if "api_server_thread_started" not in st.session_state:
    import threading
    t = threading.Thread(target=start_api_server, daemon=True)
    t.start()
    st.session_state["api_server_thread_started"] = True

# -------------------------------------------------------
# STREAMLIT UI INJECTION
# -------------------------------------------------------
st.set_page_config(
    page_title=f"{APP_NAME} Headquarters Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Render the modular dashboard
from ui.dashboard import render_dashboard
render_dashboard()
