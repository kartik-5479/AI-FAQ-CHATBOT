#!/usr/bin/env python3
"""
JARVIS - Startup Bootstrap Script
Handles installation and startup of the chatbot
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("\n")
    print("="*50)
    print("  JARVIS - AI FAQ Chatbot")
    print("  Just A Rather Very Intelligent System")
    print("="*50)
    print()

def check_python():
    """Check Python version"""
    print("[1/5] Checking Python version...")
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Error: Python 3.8+ required!")
        sys.exit(1)
    print()

def install_dependencies():
    """Install required packages"""
    print("[2/5] Installing dependencies...")
    
    packages = [
        'Flask==2.3.3',
        'Flask-CORS==4.0.0',
        'nltk==3.8.1',
        'scikit-learn==1.3.0',
        'numpy==1.24.3',
        'reportlab==4.0.4'
    ]
    
    try:
        for package in packages:
            print(f"  Installing {package}...", end='', flush=True)
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-q', package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(" ✓")
        
        print("✓ Dependencies installed successfully")
        print()
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error installing dependencies: {e}")
        sys.exit(1)

def download_nltk_data():
    """Download NLTK data"""
    print("[3/5] Downloading NLP data...")
    
    nltk_data = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
    
    try:
        import nltk
        for data in nltk_data:
            print(f"  Downloading {data}...", end='', flush=True)
            nltk.download(data, quiet=True, raise_errors=True)
            print(" ✓")
        
        print("✓ NLP data downloaded successfully")
        print()
    except Exception as e:
        print(f"\n✗ Error downloading NLP data: {e}")
        sys.exit(1)

def init_database():
    """Initialize database"""
    print("[4/5] Initializing database...")
    
    try:
        import database
        database.init_database()
        database.insert_sample_faqs()
        print("✓ Database initialized with sample FAQs")
        print()
    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        sys.exit(1)

def start_server():
    """Start Flask server"""
    print("[5/5] Starting JARVIS...")
    print()
    print("="*50)
    print("✓ JARVIS is ready!")
    print()
    print("Open your browser to: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*50)
    print()
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nShutting down JARVIS...")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main execution"""
    print_header()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        check_python()
        install_dependencies()
        download_nltk_data()
        init_database()
        start_server()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
