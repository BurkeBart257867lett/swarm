from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import os
import threading
import sys
import shlex
import logging
from pathlib import Path

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load system prompt once
SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / 'terminal' / 'system.prompt.md'
SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding='utf-8') if SYSTEM_PROMPT_PATH.exists() else "Default REDACTED Swarm prompt."

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('output', {'data': '✅ Connected to REDACTED Swarm Web Terminal.'})

@socketio.on('command')
def handle_command(data):
    raw_cmd = data.get('cmd', '').strip()
    if not raw_cmd:
        return

    try:
        # Proper shell-like parsing
        args = shlex.split(raw_cmd)
    except ValueError as e:
        emit('output', {'data': f'❌ Parse error: {e}'})
        return

    # Build command safely
    script_path = Path(__file__).parent.parent / 'lib' / 'python' / 'run_with_ollama.py'
    full_cmd = [
        sys.executable,
        str(script_path),
        '--prompt', SYSTEM_PROMPT,   # always inject system prompt first
        *args
    ]

    def run_process():
        try:
            logger.info(f"Executing: {' '.join(full_cmd[:5])}...")  # truncated for log safety

            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=script_path.parent,   # run from lib/python/ dir
                bufsize=1,                # line buffered
                universal_newlines=True
            )

            # Stream stdout live
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    emit('output', {'data': line.strip()})

            process.stdout.close()
            stderr = process.stderr.read().strip()
            if stderr:
                emit('output', {'data': f'⚠️  {stderr}'})

            process.wait()
            if process.returncode != 0:
                emit('output', {'data': f'Process exited with code {process.returncode}'})

        except FileNotFoundError:
            emit('output', {'data': '❌ run_with_ollama.py not found. Check paths.'})
        except Exception as e:
            logger.error(f"Terminal error: {e}")
            emit('output', {'data': f'💥 Error: {str(e)}'})

    # Run in background
    threading.Thread(target=run_process, daemon=True).start()

if __name__ == '__main__':
    # Security: only debug in development
    is_dev = os.getenv('FLASK_ENV') == 'development'
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=is_dev,
        allow_unsafe_werkzeug=is_dev
    )
