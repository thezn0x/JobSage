from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import toml
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Paths
BASE_DIR = Path(__file__).parent.parent  # Parent directory (skillscout/)
CONFIG_PATH = 'config/config.toml'
LOGS_DIR = 'src/utils/logs.log'

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)


def log_event(message, level='INFO'):
    """Log events to file"""
    timestamp = datetime.now().isoformat()
    log_file = LOGS_DIR / 'control_panel.log'
    
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        if not CONFIG_PATH.exists():
            return jsonify({
                'success': False,
                'error': 'Config file not found'
            }), 404
        
        with open(CONFIG_PATH, 'r') as f:
            config_content = f.read()
        
        log_event('Configuration loaded')
        return jsonify({
            'success': True,
            'config': config_content
        })
    
    except Exception as e:
        log_event(f'Error loading config: {str(e)}', 'ERROR')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config', methods=['POST'])
def save_config():
    """Save configuration"""
    try:
        data = request.json
        config_content = data.get('config')
        
        if not config_content:
            return jsonify({
                'success': False,
                'error': 'No config provided'
            }), 400
        
        # Validate TOML syntax
        try:
            toml.loads(config_content)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid TOML syntax: {str(e)}'
            }), 400
        
        # Save config
        with open(CONFIG_PATH, 'w') as f:
            f.write(config_content)
        
        log_event('Configuration saved')
        return jsonify({'success': True})
    
    except Exception as e:
        log_event(f'Error saving config: {str(e)}', 'ERROR')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/extract/<source>', methods=['POST'])
def run_extractor(source):
    """Run extractor for specific source"""
    try:
        log_event(f'Starting {source} extractor')
        
        # Build command
        if source == 'all':
            cmd = ['python', '-m', 'src.extractors']
        elif source == 'rozee':
            cmd = ['python', '-m', 'src.extractors.rozee']
        elif source == 'careerjet':
            cmd = ['python', '-m', 'src.extractors.careerjet']
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown source: {source}'
            }), 400
        
        # Run extractor
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Try to parse job count from output
            count = result.stdout.count('job') if 'job' in result.stdout else 0
            
            log_event(f'{source} extractor completed: {count} jobs')
            return jsonify({
                'success': True,
                'count': count,
                'output': result.stdout
            })
        else:
            log_event(f'{source} extractor failed: {result.stderr}', 'ERROR')
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    
    except subprocess.TimeoutExpired:
        log_event(f'{source} extractor timed out', 'ERROR')
        return jsonify({
            'success': False,
            'error': 'Extractor timed out (> 5 minutes)'
        }), 500
    
    except Exception as e:
        log_event(f'Extractor error: {str(e)}', 'ERROR')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/transform/<source>', methods=['POST'])
def run_transformer(source):
    """Run transformer for specific source"""
    try:
        log_event(f'Starting {source} transformer')
        
        # Build command
        if source == 'all':
            cmd = ['python', '-m', 'src.transformers']
        elif source == 'rozee':
            cmd = ['python', '-m', 'src.transformers.rozee_cleaner']
        elif source == 'careerjet':
            cmd = ['python', '-m', 'src.transformers.careerjet_cleaner']
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown source: {source}'
            }), 400
        
        # Run transformer
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            count = result.stdout.count('cleaned') if 'cleaned' in result.stdout else 0
            
            log_event(f'{source} transformer completed: {count} jobs')
            return jsonify({
                'success': True,
                'count': count,
                'output': result.stdout
            })
        else:
            log_event(f'{source} transformer failed: {result.stderr}', 'ERROR')
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    
    except Exception as e:
        log_event(f'Transformer error: {str(e)}', 'ERROR')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/load/<source>', methods=['POST'])
def run_loader(source):
    """Run loader for specific source"""
    try:
        log_event(f'Starting {source} loader')
        
        # Build command
        if source == 'all':
            cmd = ['python', '-m', 'src.loaders.main_loader']
        elif source in ['rozee', 'careerjet']:
            cmd = ['python', '-m', 'src.loaders.main_loader', '--source', source]
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown source: {source}'
            }), 400
        
        # Run loader
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            count = result.stdout.count('loaded') if 'loaded' in result.stdout else 0
            
            log_event(f'{source} loader completed: {count} jobs')
            return jsonify({
                'success': True,
                'count': count,
                'output': result.stdout
            })
        else:
            log_event(f'{source} loader failed: {result.stderr}', 'ERROR')
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    
    except Exception as e:
        log_event(f'Loader error: {str(e)}', 'ERROR')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/etl/full', methods=['POST'])
def run_full_etl():
    """Run complete ETL pipeline"""
    try:
        log_event('Starting full ETL pipeline')
        
        # Run the complete ETL script
        cmd = ['python', 'run_etl.py']
        
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=900  # 15 minute timeout
        )
        
        if result.returncode == 0:
            # Parse output for job count
            lines = result.stdout.split('\n')
            total_jobs = 0
            for line in lines:
                if 'jobs' in line.lower():
                    try:
                        total_jobs = int(''.join(filter(str.isdigit, line)))
                    except Exception:
                        pass
            
            log_event(f'Full ETL completed: {total_jobs} jobs processed')
            return jsonify({
                'success': True,
                'total_jobs': total_jobs,
                'output': result.stdout
            })
        else:
            log_event(f'Full ETL failed: {result.stderr}', 'ERROR')
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    
    except subprocess.TimeoutExpired:
        log_event('Full ETL timed out', 'ERROR')
        return jsonify({
            'success': False,
            'error': 'ETL pipeline timed out (> 15 minutes)'
        }), 500
    
    except Exception as e:
        log_event(f'ETL error: {str(e)}', 'ERROR')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/db/test', methods=['POST'])
def test_database():
    """Test database connection"""
    try:
        data = request.json
        conn_string = data.get('connection_string')
        
        if not conn_string:
            return jsonify({
                'success': False,
                'error': 'No connection string provided'
            }), 400
        
        # Try to connect (using psycopg2 or SQLAlchemy)
        import psycopg2
        
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        
        log_event('Database connection successful')
        return jsonify({'success': True})
    
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'psycopg2 not installed. Install with: pip install psycopg2-binary'
        }), 500
    
    except Exception as e:
        log_event(f'Database connection failed: {str(e)}', 'ERROR')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent logs"""
    try:
        log_file = LOGS_DIR / 'control_panel.log'
        
        if not log_file.exists():
            return jsonify({
                'success': True,
                'logs': []
            })
        
        with open(log_file, 'r') as f:
            logs = f.readlines()[-100:]  # Last 100 lines
        
        return jsonify({
            'success': True,
            'logs': [log.strip() for log in logs]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        # Check if extractors/transformers/loaders are running
        # This is a simple implementation
        status = {
            'running': False,
            'last_run': None,
            'next_scheduled': None
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/', methods=['GET'])
def index():
    """API info"""
    return jsonify({
        'service': 'SkillScout Control Panel API',
        'version': '1.0.0',
        'endpoints': [
            'GET  /api/config',
            'POST /api/config',
            'POST /api/extract/<source>',
            'POST /api/transform/<source>',
            'POST /api/load/<source>',
            'POST /api/etl/full',
            'POST /api/db/test',
            'GET  /api/logs',
            'GET  /api/status'
        ]
    })


if __name__ == '__main__':
    print("🚀 SkillScout Control Panel API")
    print("=" * 50)
    print("API running on: http://localhost:5000")
    print("Open Control Panel: skillscout-control-panel/index.html")
    print("=" * 50)
    
    log_event('Control Panel API started')
    app.run(host='0.0.0.0', port=5000, debug=True)