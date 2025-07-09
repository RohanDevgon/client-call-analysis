import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import requests

import sys
import io

# Force stdout to use UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ASSEMBLYAI_API_KEY = os.environ.get("ASSEMBLYAI_API_KEY")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")


app = Flask(__name__)


# Configure MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:ROMEO2003@localhost/client_sentiment_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
db = SQLAlchemy(app)






# Define AudioFile model
class AudioFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    transcript = db.Column(db.Text)
    
    # Basic analysis fields
    sentiment = db.Column(db.String(50))
    emotions = db.Column(db.String(100))
    summary = db.Column(db.Text)
    
    # Enhanced analysis fields
    customer_name = db.Column(db.String(100))  # Added missing field
    call_reason = db.Column(db.String(200))
    main_issue = db.Column(db.String(200))
    solution = db.Column(db.String(200))
    compensation = db.Column(db.String(200))
    urgency = db.Column(db.String(50))        # Added missing field
    sentiment_journey = db.Column(db.String(200))
    satisfaction = db.Column(db.String(50))
    agent_effectiveness = db.Column(db.String(100))
    detailed_summary = db.Column(db.Text)

    

from flask import send_from_directory


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        audio = request.files.get('audio')
        if audio:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)
            audio.save(filepath)




            # Save metadata to DB
            new_audio = AudioFile(filename=audio.filename)
            db.session.add(new_audio)
            db.session.commit()




            # Immediately transcribe after upload
            return redirect(url_for('transcribe_audio', audio_id=new_audio.id))
    return render_template('index.html')









def upload_to_assemblyai(filepath):
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    with open(filepath, 'rb') as f:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=f)
    if response.status_code == 200:
        return response.json()['upload_url']
    else:
        raise Exception(f"Upload failed: {response.text}")



def transcribe_diarized(upload_url):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json_data = {
        "audio_url": upload_url,
        "speaker_labels": True
    }
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    response = requests.post(endpoint, json=json_data, headers=headers)
    transcript_id = response.json()['id']

    # Poll until it's complete
    while True:
        polling = requests.get(f"{endpoint}/{transcript_id}", headers=headers).json()
        if polling['status'] == 'completed':
            return polling['utterances']  # speaker-separated list
        elif polling['status'] == 'error':
            raise Exception(f"Transcription failed: {polling['error']}")
        import time
        time.sleep(5)


def format_utterances(utterances):
    speaker_map = {}
    speaker_counter = 1
    formatted = []

    for u in utterances:
        spk = u['speaker']
        if spk not in speaker_map:
            label = "Agent" if speaker_counter == 1 else "Customer"
            speaker_map[spk] = label
            speaker_counter += 1

        speaker_name = speaker_map[spk]
        sentence = u['text'].strip()
        formatted.append(f"{speaker_name}: {sentence}")

    return "\n\n".join(formatted)  



def get_detailed_analysis(transcript):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""You are a customer service call analyst. Given a call transcript, extract the following fields. 
    Return each line **exactly in this format**. 
    If a field is missing or not applicable, write "N/A".

1. CALL OVERVIEW:
- Customer: <name or N/A>
- Reason: <brief reason or N/A>
- Urgency: <urgency or N/A>

2. KEY DETAILS:
- Main Issue: <main issue or N/A>
- Solution: <solution provided or N/A>
- Compensation: <compensation or N/A>

3. SENTIMENT ANALYSIS:
- Final Sentiment: <Positive/Negative/Neutral>
- Journey: <emotional flow or N/A>

4. SATISFACTION:
- Satisfaction: <High/Medium/Low or N/A>

5. AGENT PERFORMANCE:
- Effectiveness: <High/Medium/Low or N/A>

6. BRIEF SUMMARY:
- Summary: <3-4 sentence summary>

Return each finding on a new line exactly as formatted above. Only include sections where information is available.

Transcript:
{transcript[:4000]}"""

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a customer service analyst that extracts specific information in exact formats."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("DEEPSEEK RAW RESPONSE:\n", response.json()) 
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"DeepSeek API Error: {response.text}")
    


def parse_analysis_result(result):
    """Parse DeepSeek response into a dictionary"""
    parsed = {}
    for line in result.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            parsed[key] = value.strip()
    return parsed

@app.route('/transcribe/<int:audio_id>')
def transcribe_audio(audio_id):
    audio = AudioFile.query.get_or_404(audio_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)

    try:
        # Transcribe audio
        upload_url = upload_to_assemblyai(filepath)
        utterances = transcribe_diarized(upload_url)
        transcript_text = format_utterances(utterances)
        audio.transcript = transcript_text

        # Get detailed analysis
        detailed_result = get_detailed_analysis(transcript_text)
        
        if detailed_result:
            print("DETAILED RESULT:\n", detailed_result)  # A
            lines = [line.strip() for line in detailed_result.split('\n') if line.strip()]
            print("PARSED LINES:\n", lines)
            # Parse all fields from the detailed analysis
            for line in lines:
                lower_line = line.lower()

                if "- customer:" in lower_line:
                    audio.customer_name = line.split(":", 1)[1].strip()
                elif "- reason:" in lower_line:
                    audio.call_reason = line.split(":", 1)[1].strip()
                elif "- urgency:" in lower_line:
                    audio.urgency = line.split(":", 1)[1].strip()
                elif "- main issue:" in lower_line:
                    audio.main_issue = line.split(":", 1)[1].strip()
                elif "- solution:" in lower_line:
                    audio.solution = line.split(":", 1)[1].strip()
                elif "- compensation:" in lower_line:
                    audio.compensation = line.split(":", 1)[1].strip()
                elif "- final sentiment:" in lower_line:
                    audio.sentiment = line.split(":", 1)[1].strip()
                elif "- journey:" in lower_line:
                    audio.sentiment_journey = line.split(":", 1)[1].strip()
                elif "- satisfaction:" in lower_line:
                    audio.satisfaction = line.split(":", 1)[1].strip()
                elif "- effectiveness:" in lower_line:
                    audio.agent_effectiveness = line.split(":", 1)[1].strip()
                elif "- summary:" in lower_line:
                    summary = line.split(":", 1)[1].strip()
                    audio.summary = summary
                    audio.detailed_summary = summary
                elif "- emotions:" in lower_line:
                    audio.emotions = line.split(":", 1)[1].strip()
                else:
                    print(f"⚠️ Unrecognized line: {line}")


        db.session.commit()

    except Exception as e:
        return f"Error during processing: {e}"

    return redirect(url_for('view_audio', audio_id=audio.id))



@app.route('/audio/<int:audio_id>')
def view_audio(audio_id):
    audio = AudioFile.query.get_or_404(audio_id)
    return render_template('view_audio.html', audio=audio)




from flask import send_from_directory




@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)












if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)