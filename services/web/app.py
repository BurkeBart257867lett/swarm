# services/web/app.py
# REDACTED Swarm — Hardened Web Terminal with Dual-Mode Runtime Bridge
# Security-first design: auth, validation, timeout, audit, DHT integration

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
import subprocess
import os
import threading
import sys
import shlex
import logging
import time
import re
import hashlib
import hmac
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
import requests  # for TypeScript runtime bridge

app = Flask(__name__, template_folder='templates')

# ────────────────────────────────────────────────
# 🔐 Security Configuration (loaded from env)
# ────────────────────────────────────────────────

API_KEY = os.getenv('WEB_TERMINAL_API_KEY')  # Required for auth
CORS_ORIGINS = os.getenv('WEB_CORS_ORIGINS', 'http://localhost:3000').split(',')
RUNTIME_API_URL = os.getenv('RUNTIME_API_URL', 'http://localhost:4001')  # TS runtime bridge
MAX_COMMAND_LENGTH = 4096
COMMAND_TIMEOUT_SECONDS = int(os.getenv('WEB_COMMAND_TIMEOUT', '300'))  # 5 min default
RATE_LIMIT_REQUESTS = int(os.getenv('WEB_RATE_LIMIT', '10'))  # per minute per session
RATE_LIMIT_WINDOW = 60  # seconds

# ────────────────────────────────────────────────
# 📝 Audit Logging Setup
# ────────────────────────────────────────────────

LOG_DIR = Path(__file__).parent.parent / 'data' / 'audit'
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG = LOG_DIR / 'web_terminal.log'

def audit_log(event_type: str, session_id: str, command: str, status: str, details: dict = None):
    """Append structured audit entry to log file"""
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': event_type,
        'session': session_id,
        'command': command[:200],  # truncate for safety
        'status': status,
        'details': details or {}
    }
    with open(AUDIT_LOG, 'a', encoding='utf-8') as f:
        f.write(f"{entry}\n")
    logger.info(f"[AUDIT] {entry}")

# ────────────────────────────────────────────────
# ⚡ Rate Limiting (simple token bucket per session)
# ────────────────────────────────────────────────

rate_limits = defaultdict(lambda: deque(maxlen=RATE_LIMIT_REQUESTS))

def check_rate_limit(session_id: str) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    # Remove expired timestamps
    while rate_limits[session_id] and rate_limits[session_id][0] < window_start:
        rate_limits[session_id].popleft()
    if len(rate_limits[session_id]) >= RATE_LIMIT_REQUESTS:
        return False
    rate_limits[session_id].append(now)
    return True

# ────────────────────────────────────────────────
# 🔗 TypeScript Runtime Bridge Client
# ────────────────────────────────────────────────

class RuntimeBridge:
    """HTTP client for communicating with TypeScript runtime DHT APIs"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def query_dht_peers(self, role: str, limit: int = 10) -> dict:
        """Query DHT for peers with given role"""
        try:
            resp = self.session.get(
                f"{self.base_url}/api/dht/peers",
                params={'role': role, 'limit': limit},
                timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"Runtime bridge DHT query failed: {e}")
            return {'error': str(e), 'peers': []}
    
    def announce_capability(self, peer_id: str, roles: list, capabilities: list, character_hash: str = None) -> dict:
        """Announce web session as observer capability in DHT"""
        try:
            resp = self.session.post(
                f"{self.base_url}/api/dht/announce",
                json={
                    'peerId': peer_id,
                    'roles': roles,
                    'capabilities': capabilities,
                    'characterHash': character_hash,
                    'source': 'web_terminal'
                },
                timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"Runtime bridge capability announce failed: {e}")
            return {'error': str(e)}
    
    def execute_command(self, args: list, runtime_config: dict = None) -> dict:
        """Forward command to TypeScript runtime for execution"""
        try:
            resp = self.session.post(
                f"{self.base_url}/api/agent/execute",
                json={'args': args, 'config': runtime_config or {}},
                timeout=COMMAND_TIMEOUT_SECONDS
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"Runtime bridge command execution failed: {e}")
            return {'error': str(e), 'output': []}

# Initialize bridge
runtime_bridge = RuntimeBridge(RUNTIME_API_URL)

# ────────────────────────────────────────────────
# Flask + SocketIO Setup
# ────────────────────────────────────────────────

socketio = SocketIO(app, cors_allowed_origins=CORS_ORIGINS, async_mode='threading')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / 'web_app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────
# System Prompt + Path Resolution
# ────────────────────────────────────────────────

SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / 'terminal' / 'system.prompt.md'
SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding='utf-8') if SYSTEM_PROMPT_PATH.exists() else "Default REDACTED Swarm prompt."

PYTHON_SCRIPT_PATH = Path(__file__).parent.parent / 'lib' / 'python' / 'run_with_ollama.py'
ALLOWED_AGENTS_DIR = Path(__file__).parent.parent / 'agents'
ALLOWED_MODELS = {'qwen2.5', 'llama3', 'mistral', 'gemma'}  # extend as needed

# ────────────────────────────────────────────────
# 🔐 Authentication Helpers
# ────────────────────────────────────────────────

def generate_session_id() -> str:
    """Generate cryptographically random session identifier"""
    return hashlib.sha256(os.urandom(32) + str(time.time()).encode()).hexdigest()[:16]

def verify_signature(payload: str, signature: str, peer_public_key: str = None) -> bool:
    """Verify Ed25519 signature over command payload (future: integrate with libp2p peer IDs)"""
    # Placeholder: in production, use nacl.signing.VerifyKey(peer_public_key).verify()
    # For now, fallback to API key auth
    return API_KEY and hmac.compare_digest(signature, hmac.new(API_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest())

# ────────────────────────────────────────────────
# 🛡️ Command Validation
# ────────────────────────────────────────────────

def validate_command_args(args: list) -> tuple[bool, str]:
    """Validate parsed command arguments against security policy"""
    
    # Check for path traversal attempts
    for arg in args:
        if '..' in arg or arg.startswith('/'):
            return False, "Path traversal detected in arguments"
    
    # Validate --agent path
    try:
        agent_idx = args.index('--agent')
        if agent_idx + 1 < len(args):
            agent_path = Path(args[agent_idx + 1]).resolve()
            if not str(agent_path).startswith(str(ALLOWED_AGENTS_DIR.resolve())):
                return False, f"Agent path must reside within {ALLOWED_AGENTS_DIR}"
    except ValueError:
        pass  # --agent not specified, may be optional
    
    # Validate --model
    try:
        model_idx = args.index('--model')
        if model_idx + 1 < len(args):
            model = args[model_idx + 1]
            if model not in ALLOWED_MODELS:
                return False, f"Model '{model}' not allowed. Choose from: {ALLOWED_MODELS}"
    except ValueError:
        pass
    
    # Validate --runtime mode
    try:
        runtime_idx = args.index('--runtime')
        if runtime_idx + 1 < len(args):
            runtime = args[runtime_idx + 1]
            if runtime not in ('python', 'typescript'):
                return False, "Runtime must be 'python' or 'typescript'"
    except ValueError:
        pass  # default to python
    
    return True, ""

# ────────────────────────────────────────────────
# Flask Routes
# ────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'web-terminal', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/dht/peers', methods=['GET'])
def api_query_peers():
    """HTTP endpoint for DHT peer queries (alternative to WebSocket)"""
    role = request.args.get('role', 'agent')
    limit = min(int(request.args.get('limit', '10')), 50)  # cap at 50
    result = runtime_bridge.query_dht_peers(role, limit)
    return jsonify(result)

# ────────────────────────────────────────────────
# 🔌 SocketIO Event Handlers
# ────────────────────────────────────────────────

@socketio.on('connect')
def handle_connect():
    session_id = generate_session_id()
    request.session_id = session_id  # attach to request context
    
    # 🔐 Auth check
    token = request.args.get('token')
    signature = request.args.get('sig')
    
    if API_KEY:
        if token and hmac.compare_digest(token, API_KEY):
            pass  # API key auth passed
        elif signature and verify_signature(session_id, signature):
            pass  # signature auth passed
        else:
            audit_log('connect_failed', session_id, '', 'unauthorized', {'reason': 'invalid_credentials'})
            emit('auth_error', {'data': 'Authentication required'})
            disconnect()
            return
    
    audit_log('connect', session_id, '', 'success')
    emit('output', {'data': '✅ Connected to REDACTED Swarm Web Terminal.'})
    emit('session_id', {'id': session_id})  # send session ID for client tracking

@socketio.on('disconnect')
def handle_disconnect():
    session_id = getattr(request, 'session_id', 'unknown')
    audit_log('disconnect', session_id, '', 'success')

@socketio.on('command')
def handle_command(data):
    session_id = getattr(request, 'session_id', 'unknown')
    raw_cmd = data.get('cmd', '').strip()
    
    if not raw_cmd:
        emit('output', {'data': '❌ Empty command'})
        return
    
    # 🔐 Rate limit check
    if not check_rate_limit(session_id):
        audit_log('rate_limited', session_id, raw_cmd, 'blocked')
        emit('output', {'data': '⚠️  Rate limit exceeded. Please wait.'})
        return
    
    # 🔐 Command length guard
    if len(raw_cmd) > MAX_COMMAND_LENGTH:
        audit_log('command_too_long', session_id, raw_cmd[:100], 'blocked')
        emit('output', {'data': f'❌ Command exceeds max length ({MAX_COMMAND_LENGTH})'})
        return
    
    try:
        args = shlex.split(raw_cmd)
    except ValueError as e:
        audit_log('parse_error', session_id, raw_cmd, 'error', {'error': str(e)})
        emit('output', {'data': f'❌ Parse error: {e}'})
        return
    
    # 🛡️ Validate arguments
    valid, error_msg = validate_command_args(args)
    if not valid:
        audit_log('validation_failed', session_id, raw_cmd, 'blocked', {'reason': error_msg})
        emit('output', {'data': f'❌ Validation error: {error_msg}'})
        return
    
    # 🔄 Determine runtime mode
    runtime_mode = 'python'
    try:
        runtime_idx = args.index('--runtime')
        if runtime_idx + 1 < len(args):
            runtime_mode = args[runtime_idx + 1]
            # Remove runtime args so they don't reach underlying script
            args.pop(runtime_idx + 1)
            args.pop(runtime_idx)
    except ValueError:
        pass  # default to python
    
    audit_log('command_received', session_id, raw_cmd, 'accepted', {'runtime': runtime_mode})
    
    if runtime_mode == 'typescript':
        # 🌐 Route to TypeScript runtime via bridge
        run_typescript_command(session_id, args, data)
    else:
        # 🐍 Execute via Python runtime (existing path)
        run_python_command(session_id, args)

def run_python_command(session_id: str, args: list):
    """Execute command via Python runtime (run_with_ollama.py)"""
    
    full_cmd = [
        sys.executable,
        str(PYTHON_SCRIPT_PATH),
        '--prompt', SYSTEM_PROMPT,
        *args
    ]
    
    def run_process():
        start_time = time.time()
        try:
            logger.info(f"[Python] Executing: {' '.join(full_cmd[:6])}...")
            
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=PYTHON_SCRIPT_PATH.parent,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream stdout live
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    emit('output', {'data': line.strip()})
            
            process.stdout.close()
            stderr = process.stderr.read().strip()
            
            # ⏱️ Timeout check
            elapsed = time.time() - start_time
            if elapsed > COMMAND_TIMEOUT_SECONDS:
                process.kill()
                emit('output', {'data': f'⚠️  Process terminated: exceeded {COMMAND_TIMEOUT_SECONDS}s timeout'})
                audit_log('command_timeout', session_id, '', 'timeout', {'elapsed': elapsed})
                return
            
            process.wait(timeout=max(1, COMMAND_TIMEOUT_SECONDS - elapsed))
            
            if stderr:
                emit('output', {'data': f'⚠️  {stderr}'})
            if process.returncode != 0:
                emit('output', {'data': f'Process exited with code {process.returncode}'})
                audit_log('command_failed', session_id, '', 'error', {'returncode': process.returncode})
            else:
                audit_log('command_completed', session_id, '', 'success', {'duration': time.time() - start_time})
                
        except FileNotFoundError:
            emit('output', {'data': '❌ run_with_ollama.py not found. Check paths.'})
            audit_log('file_not_found', session_id, '', 'error')
        except subprocess.TimeoutExpired:
            process.kill()
            emit('output', {'data': f'⚠️  Process terminated: exceeded {COMMAND_TIMEOUT_SECONDS}s timeout'})
            audit_log('command_timeout', session_id, '', 'timeout')
        except Exception as e:
            logger.error(f"[Python] Terminal error: {e}")
            emit('output', {'data': f'💥 Error: {str(e)}'})
            audit_log('command_exception', session_id, '', 'error', {'exception': str(e)})
    
    threading.Thread(target=run_process, daemon=True).start()

def run_typescript_command(session_id: str, args: list, original_data: dict):
    """Route command to TypeScript runtime via HTTP bridge"""
    
    def execute_via_bridge():
        try:
            emit('output', {'data': f'🔗 Routing to TypeScript runtime: {" ".join(args)}'})
            
            # Extract optional runtime config from original data
            runtime_config = original_data.get('config', {})
            
            # Execute via bridge
            result = runtime_bridge.execute_command(args, runtime_config)
            
            if 'error' in result:
                emit('output', {'data': f'❌ Runtime bridge error: {result["error"]}'})
                audit_log('bridge_error', session_id, '', 'error', {'bridge_error': result['error']})
                return
            
            # Stream output if available
            output_lines = result.get('output', [])
            for line in output_lines:
                emit('output', {'data': line})
            
            audit_log('bridge_command_completed', session_id, '', 'success', {'lines': len(output_lines)})
            emit('output', {'data': '✅ TypeScript runtime execution complete.'})
            
        except Exception as e:
            logger.error(f"[Bridge] Execution error: {e}")
            emit('output', {'data': f'💥 Bridge error: {str(e)}'})
            audit_log('bridge_exception', session_id, '', 'error', {'exception': str(e)})
    
    threading.Thread(target=execute_via_bridge, daemon=True).start()

# ────────────────────────────────────────────────
# 🌱 DHT-Specific SocketIO Events
# ────────────────────────────────────────────────

@socketio.on('dht:query_peers')
def handle_dht_query(data):
    session_id = getattr(request, 'session_id', 'unknown')
    role = data.get('role', 'agent')
    limit = min(int(data.get('limit', '10')), 50)
    
    audit_log('dht_query', session_id, f'role:{role}', 'accepted')
    
    result = runtime_bridge.query_dht_peers(role, limit)
    emit('dht:peers_found', result)

@socketio.on('dht:announce_observer')
def handle_observer_announce(data):
    session_id = getattr(request, 'session_id', 'unknown')
    
    # Generate web-session peer ID (deterministic from session + timestamp)
    peer_id = f"web-{session_id}-{int(time.time())}"
    roles = data.get('roles', ['web_observer'])
    capabilities = data.get('capabilities', ['ui', 'monitoring'])
    character_hash = data.get('characterHash')
    
    result = runtime_bridge.announce_capability(peer_id, roles, capabilities, character_hash)
    
    if 'error' in result:
        emit('dht:announce_error', {'error': result['error']})
        audit_log('dht_announce_failed', session_id, '', 'error', {'bridge_error': result['error']})
    else:
        emit('dht:announced', {'peerId': peer_id, 'roles': roles})
        audit_log('dht_announce_success', session_id, '', 'success', {'peer_id': peer_id})

# ────────────────────────────────────────────────
# 🚀 Application Entry Point
# ────────────────────────────────────────────────

if __name__ == '__main__':
    is_dev = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting REDACTED Swarm Web Terminal (runtime bridge: {RUNTIME_API_URL})")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('WEB_PORT', '5000')),
        debug=is_dev,
        allow_unsafe_werkzeug=is_dev
    )
