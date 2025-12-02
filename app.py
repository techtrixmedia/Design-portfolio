#!/usr/bin/env python3
"""
Creative Design Studio - Backend Server
A simple Flask server for handling contact form submissions and serving the website.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json

app = Flask(__name__)
app.static_folder = '.'
app.static_url_path = ''
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = './uploads'

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Store contact messages (in production, use a database)
CONTACTS_FILE = 'contacts.json'

def load_contacts():
    """Load existing contacts from file."""
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_contacts(contacts):
    """Save contacts to file."""
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=2)

@app.route('/')
def index():
    """Serve the main page."""
    return app.send_static_file('index.html')

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    """Handle contact form submissions."""
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('name') or not data.get('email') or not data.get('message'):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Create contact record
        contact = {
            'id': len(load_contacts()) + 1,
            'name': data.get('name'),
            'email': data.get('email'),
            'message': data.get('message'),
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        # Save to file
        contacts = load_contacts()
        contacts.append(contact)
        save_contacts(contacts)
        
        # Log the submission
        print(f"[{datetime.now()}] New contact from {contact['name']} ({contact['email']})")
        
        return jsonify({'success': True, 'message': 'Contact saved successfully'}), 201
    
    except Exception as e:
        print(f"Error processing contact: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts (admin only in production)."""
    try:
        contacts = load_contacts()
        return jsonify({'success': True, 'data': contacts}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/read', methods=['PUT'])
def mark_contact_read(contact_id):
    """Mark a contact as read."""
    try:
        contacts = load_contacts()
        for contact in contacts:
            if contact['id'] == contact_id:
                contact['read'] = True
                save_contacts(contacts)
                return jsonify({'success': True, 'message': 'Contact marked as read'}), 200
        
        return jsonify({'success': False, 'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'Creative Design Studio API'}), 200

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images, etc.)."""
    try:
        return app.send_static_file(filename)
    except:
        return "File not found", 404

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Creative Design Studio - Backend Server")
    print("=" * 50)
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
