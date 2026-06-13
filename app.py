"""
Jarvis - AI-Powered FAQ Chatbot
Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os
from io import BytesIO, StringIO
import csv

# Import custom services
from database import init_database, insert_sample_faqs, get_connection
from services.nlp_service import nlp_service
from services.similarity_service import similarity_service

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize database
def init_app():
    """Initialize application"""
    if not os.path.exists('database.db'):
        init_database()
        insert_sample_faqs()
        similarity_service.refresh_training()
        print("Database initialized with sample FAQs")

# ==================== CHAT ROUTES ====================

@app.route('/', methods=['GET'])
def index():
    """Render main chat page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process user question and return answer
    Returns JSON with answer, confidence, and metadata
    """
    try:
        data = request.get_json()
        user_question = data.get('message', '').strip()
        
        if not user_question:
            return jsonify({'error': 'Empty question'}), 400
        
        # Detect intent
        intent = nlp_service.detect_intent(user_question)
        
        # Handle special intents
        special_responses = {
            'greeting': "Hello! I'm Jarvis, your intelligent FAQ assistant. How can I help you today?",
            'goodbye': "Thank you for using Jarvis! Have a great day!",
            'thanks': "You're welcome! I'm always here to help. Is there anything else?",
            'help': "I'm here to assist you! You can ask me questions about admissions, fees, courses, placements, hostel, library, exams, and much more."
        }
        
        if intent in special_responses:
            bot_answer = special_responses[intent]
            confidence = 100.0
            faq_id = None
        else:
            # Find similar FAQs using TF-IDF and cosine similarity
            similar_faqs = similarity_service.find_similar_faq(user_question, threshold=0.25, top_k=1)
            
            if similar_faqs:
                top_match = similar_faqs[0]
                bot_answer = top_match['answer']
                confidence = top_match['confidence']
                faq_id = top_match['faq_id']
            else:
                # Fallback response
                bot_answer = "I couldn't find an exact answer to your question. Please try rephrasing it or check our FAQ database. Would you like me to show you some related topics?"
                confidence = 0.0
                faq_id = None
        
        # Add typing delay simulation
        response_data = {
            'success': True,
            'answer': bot_answer,
            'confidence': round(confidence, 2),
            'intent': intent,
            'faq_id': faq_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to chat history
        save_chat_history(user_question, bot_answer, confidence, intent, faq_id)
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/similar-faqs', methods=['POST'])
def get_similar_faqs():
    """Get similar FAQs for fallback"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        similar_faqs = similarity_service.find_similar_faq(question, threshold=0.2, top_k=3)
        
        return jsonify({
            'success': True,
            'faqs': similar_faqs
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ==================== HISTORY ROUTES ====================

@app.route('/history', methods=['GET'])
def history():
    """Render history page"""
    return render_template('history.html')

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get chat history"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = (page - 1) * limit
        
        # Get total count
        cursor.execute('SELECT COUNT(*) as count FROM chat_history')
        total = cursor.fetchone()['count']
        
        # Get history records
        cursor.execute('''
            SELECT id, user_question, bot_answer, confidence, intent, timestamp 
            FROM chat_history 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        history_records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'history': history_records,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/history/<int:history_id>', methods=['GET'])
def get_history_item(history_id):
    """Get specific history item"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM chat_history WHERE id = ?
        ''', (history_id,))
        
        record = dict(cursor.fetchone())
        conn.close()
        
        return jsonify({'success': True, 'record': record})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/history', methods=['DELETE'])
def delete_history():
    """Delete all history"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM chat_history')
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'History cleared'})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/history/<int:history_id>', methods=['DELETE'])
def delete_history_item(history_id):
    """Delete specific history item"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM chat_history WHERE id = ?', (history_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'History item deleted'})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ==================== FAVORITES ROUTES ====================

@app.route('/favorites', methods=['GET'])
def favorites():
    """Render favorites page"""
    return render_template('favorites.html')

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """Get favorites"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_question, bot_answer, date_saved 
            FROM favorites 
            ORDER BY date_saved DESC
        ''')
        
        favorites_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'success': True, 'favorites': favorites_list})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """Add to favorites"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        user_question = data.get('user_question')
        bot_answer = data.get('bot_answer')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO favorites (chat_id, user_question, bot_answer) 
            VALUES (?, ?, ?)
        ''', (chat_id, user_question, bot_answer))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Added to favorites'})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
def remove_favorite(favorite_id):
    """Remove from favorites"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM favorites WHERE id = ?', (favorite_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Removed from favorites'})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ==================== STATISTICS ROUTES ====================

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Render dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get chat statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total questions
        cursor.execute('SELECT COUNT(*) as count FROM chat_history')
        total_questions = cursor.fetchone()['count']
        
        # Total FAQs
        cursor.execute('SELECT COUNT(*) as count FROM faqs')
        total_faqs = cursor.fetchone()['count']
        
        # Average confidence
        cursor.execute('SELECT AVG(confidence) as avg_conf FROM chat_history WHERE confidence > 0')
        avg_confidence = cursor.fetchone()['avg_conf'] or 0
        
        # Most asked category
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM chat_history c 
            JOIN faqs f ON c.faq_id = f.id 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        
        category_result = cursor.fetchone()
        most_asked_category = category_result['category'] if category_result else 'N/A'
        
        # Categories breakdown
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM chat_history c 
            JOIN faqs f ON c.faq_id = f.id 
            GROUP BY category 
            ORDER BY count DESC
        ''')
        
        categories_breakdown = [dict(row) for row in cursor.fetchall()]
        
        # Intent distribution
        cursor.execute('''
            SELECT intent, COUNT(*) as count 
            FROM chat_history 
            GROUP BY intent 
            ORDER BY count DESC
        ''')
        
        intent_distribution = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_questions': total_questions,
                'total_faqs': total_faqs,
                'avg_confidence': round(avg_confidence, 2),
                'most_asked_category': most_asked_category,
                'categories_breakdown': categories_breakdown,
                'intent_distribution': intent_distribution
            }
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ==================== FAQ ROUTES ====================

@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    """Get all FAQs"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        category = request.args.get('category')
        
        if category:
            cursor.execute('SELECT * FROM faqs WHERE category = ? ORDER BY id', (category,))
        else:
            cursor.execute('SELECT * FROM faqs ORDER BY category, id')
        
        faqs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'success': True, 'faqs': faqs})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get FAQ categories"""
    try:
        categories = similarity_service.get_all_categories()
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ==================== EXPORT ROUTES ====================

@app.route('/api/export/txt', methods=['GET'])
def export_txt():
    """Export history as TXT"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_question, bot_answer, confidence, timestamp 
            FROM chat_history 
            ORDER BY timestamp
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        # Create text content
        content = "JARVIS - Chat History Export\n"
        content += "=" * 80 + "\n"
        content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += "=" * 80 + "\n\n"
        
        for i, record in enumerate(records, 1):
            content += f"[{i}] {record['timestamp']}\n"
            content += f"User Question: {record['user_question']}\n"
            content += f"Jarvis Answer: {record['bot_answer']}\n"
            content += f"Confidence: {record['confidence']}%\n"
            content += "-" * 80 + "\n\n"
        
        # Return file
        output = StringIO()
        output.write(content)
        output.seek(0)
        
        return send_file(
            BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/plain',
            as_attachment=True,
            download_name=f"jarvis_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export history as CSV"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_question, bot_answer, confidence, intent, timestamp 
            FROM chat_history 
            ORDER BY timestamp
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Timestamp', 'User Question', 'Jarvis Answer', 'Confidence (%)', 'Intent'])
        
        # Write data
        for record in records:
            writer.writerow([
                record['timestamp'],
                record['user_question'],
                record['bot_answer'],
                record['confidence'],
                record['intent']
            ])
        
        output.seek(0)
        
        return send_file(
            BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"jarvis_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    """Export history as PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_question, bot_answer, confidence, timestamp 
            FROM chat_history 
            ORDER BY timestamp
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        # Create PDF
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4F46E5'),
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph('JARVIS - Chat History Export', title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Metadata
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=20
        )
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
        story.append(Paragraph(f"Total Conversations: {len(records)}", meta_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Content
        for i, record in enumerate(records, 1):
            q_style = ParagraphStyle(
                'Question',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#4F46E5'),
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )
            a_style = styles['Normal']
            
            story.append(Paragraph(f"[{i}] User Question:", q_style))
            story.append(Paragraph(record['user_question'], a_style))
            story.append(Spacer(1, 0.1*inch))
            
            story.append(Paragraph("Jarvis Answer:", q_style))
            story.append(Paragraph(record['bot_answer'], a_style))
            story.append(Spacer(1, 0.05*inch))
            
            conf_style = ParagraphStyle(
                'Confidence',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Confidence: {record['confidence']}% | Time: {record['timestamp']}", conf_style))
            story.append(Spacer(1, 0.15*inch))
        
        doc.build(story)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"jarvis_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ==================== HELPER FUNCTIONS ====================

def save_chat_history(question, answer, confidence, intent, faq_id=None):
    """Save chat to history"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_history (user_question, bot_answer, confidence, intent, faq_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', (question, answer, confidence, intent, faq_id))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving chat history: {e}")

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    init_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
