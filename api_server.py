#!/usr/bin/env python3
"""
Flask API Server for OnlyFans Detector
Deploy this to make your detector accessible via HTTP for n8n integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
from onlyfans_detector_hybrid_final import detect_onlyfans_in_bio_link

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for n8n integration

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "OnlyFans Detector API",
        "version": "1.0.0"
    })

@app.route('/detect', methods=['POST'])
def detect_onlyfans():
    """Main detection endpoint"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'bio_link' not in data:
            return jsonify({
                "error": "Missing bio_link parameter",
                "usage": "Send POST with JSON: {\"bio_link\": \"https://link.me/username\"}"
            }), 400
        
        bio_link = data['bio_link']
        # Normalize if a dict was sent (n8n sometimes sends objects)
        if isinstance(bio_link, dict):
            for key in ['external_url', 'url', 'link', 'profile_url', 'bio_link']:
                if key in bio_link and isinstance(bio_link[key], str) and bio_link[key].strip():
                    bio_link = bio_link[key]
                    break
        
        logger.info(f"Processing bio link: {bio_link}")
        
        # Run detection (async function)
        result = asyncio.run(detect_onlyfans_in_bio_link(bio_link))
        
        # Add request info to result
        result['request'] = {
            'bio_link': bio_link
        }
        
        logger.info(f"Detection result: {result['has_onlyfans']} for {bio_link}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return jsonify({
            "error": "Detection failed",
            "message": str(e),
            "bio_link": data.get('bio_link') if 'data' in locals() else None
        }), 500

@app.route('/detect', methods=['GET'])
def detect_get():
    """GET endpoint for simple testing"""
    bio_link = request.args.get('bio_link')
    
    if not bio_link:
        return jsonify({
            "error": "Missing bio_link parameter",
            "usage": "GET /detect?bio_link=https://link.me/username"
        }), 400
    
    try:
        logger.info(f"Processing bio link (GET): {bio_link}")
        
        # Run detection
        result = asyncio.run(detect_onlyfans_in_bio_link(bio_link))
        
        # Add request info
        result['request'] = {
            'bio_link': bio_link,
            'method': 'GET'
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Detection error (GET): {str(e)}")
        return jsonify({
            "error": "Detection failed",
            "message": str(e),
            "bio_link": bio_link
        }), 500

@app.route('/batch', methods=['POST'])
def batch_detect():
    """Batch detection endpoint for multiple bio links"""
    try:
        data = request.get_json()
        
        # Handle both formats: {"bio_links": [...]} and raw array [...]
        if isinstance(data, list):
            # Raw array format: ["url1", "url2"]
            bio_links = data
            logger.info(f"Received raw array format with {len(bio_links)} URLs")
        elif isinstance(data, dict) and 'bio_links' in data:
            # Object format: {"bio_links": ["url1", "url2"]}
            bio_links = data['bio_links']
            logger.info(f"Received object format with {len(bio_links)} URLs")
        else:
            logger.error(f"Invalid data format received: {type(data)}")
            return jsonify({
                "error": "Invalid format. Send either {\"bio_links\": [\"url1\", \"url2\"]} or [\"url1\", \"url2\"]",
                "usage": "Send POST with JSON: {\"bio_links\": [\"url1\", \"url2\"]} or [\"url1\", \"url2\"]"
            }), 400
        
        if not isinstance(bio_links, list):
            return jsonify({
                "error": "bio_links must be an array"
            }), 400
        
        if len(bio_links) > 100:  # Reasonable upper limit
            return jsonify({
                "error": f"Maximum 100 bio links per batch. Received {len(bio_links)} URLs.",
                "received_count": len(bio_links),
                "max_allowed": 100
            }), 400
        
        # Normalize any dict entries to URLs
        normalized_links = []
        for item in bio_links:
            if isinstance(item, dict):
                extracted = None
                for key in ['external_url', 'url', 'link', 'profile_url', 'bio_link']:
                    if key in item and isinstance(item[key], str) and item[key].strip():
                        extracted = item[key]
                        break
                normalized_links.append(extracted if extracted else item)
            else:
                normalized_links.append(item)

        bio_links = normalized_links

        logger.info(f"Processing batch of {len(bio_links)} bio links")
        
        # Process each bio link with timeout protection
        results = []
        for i, bio_link in enumerate(bio_links):
            try:
                logger.info(f"Processing URL {i+1}/{len(bio_links)}: {bio_link}")
                # Add timeout to prevent hanging
                result = asyncio.run(detect_onlyfans_in_bio_link(bio_link))
                result['request'] = {'bio_link': bio_link}
                results.append(result)
            except asyncio.TimeoutError:
                logger.error(f"Timeout processing {bio_link}")
                results.append({
                    "error": f"Timeout processing {bio_link}",
                    "bio_link": bio_link,
                    "has_onlyfans": False,
                    "onlyfans_urls": [],
                    "detection_method": None,
                    "errors": ["Timeout after 30 seconds"],
                    "debug_info": []
                })
            except Exception as e:
                logger.error(f"Failed to process {bio_link}: {str(e)}")
                results.append({
                    "error": f"Failed to process {bio_link}: {str(e)}",
                    "bio_link": bio_link,
                    "has_onlyfans": False,
                    "onlyfans_urls": [],
                    "detection_method": None,
                    "errors": [str(e)],
                    "debug_info": []
                })
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Batch detection error: {str(e)}")
        return jsonify({
            "error": "Batch detection failed",
            "message": str(e)
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with available endpoints info"""
    return jsonify({
        "service": "OnlyFans Detector API",
        "version": "1.0.0",
        "available_endpoints": [
            "GET /health",
            "GET /detect?bio_link=URL",
            "POST /detect",
            "POST /batch"
        ],
        "usage": {
            "single_detection": "POST /detect with {\"bio_link\": \"https://link.me/username\"}",
            "batch_detection": "POST /batch with {\"bio_links\": [\"url1\", \"url2\"]}",
            "health_check": "GET /health"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
