#!/usr/bin/env python3
"""
Simple test Flask app to verify basic functionality
"""

from flask import Flask

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "message": "Test app working"}

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return {"message": "Test app is running"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
