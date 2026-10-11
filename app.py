import os
import asyncio
from flask import Flask, render_template_string, request, send_file
import edge_tts

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8">
    <title>Burmese AI Voice App</title>
    <style>
        body { font-family: sans-serif; margin: 50px; background: #f4f4f9; color: #333; }
        h1 { color: #2c3e50; }
        textarea { width: 100%; height: 150px; padding: 10px; font-size: 16px; border-radius: 5px; border: 1px solid #ccc; }
        select, button { padding: 10px 20px; font-size: 16px; margin-top: 10px; cursor: pointer; border-radius: 5px; border: 1px solid #ccc; }
        button { background: #3498db; color: white; border: none; }
        button:hover { background: #2980b9; }
        .container { max-width: 600px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h1>မြန်မာ AI အသံထွက်စနစ်</h1>
        <form method="POST">
            <textarea name="text" placeholder="မြန်မာစာသားကို ဤနေရာတွင် ရိုက်ထည့်ပါ...">{{ text }}</textarea><br>
            <label><b>အသံရွေးချယ်ရန်:</b></label><br>
            <select name="voice">
                <option value="my-MM-NilarNeural" {% if voice == 'my-MM-NilarNeural' %}selected{% endif %}>Nilar (အမျိုးသမီး အသံ)</option>
                <option value="my-MM-ThihaNeural" {% if voice == 'my-MM-ThihaNeural' %}selected{% endif %}>Thiha (အမျိုးသား အသံ)</option>
            </select><br><br>
            <button type="submit">အသံဖိုင်ထုတ်ရန်</button>
        </form>
        {% if audio_file %}
            <h3 style="margin-top: 20px;">ရလဒ် အသံဖိုင်:</h3>
            <audio controls style="width: 100%;">
                <source src="/play/{{ audio_file }}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio><br><br>
            <a href="/download/{{ audio_file }}" download><button style="background: #27ae60; width: 100%;">အသံဖိုင် ဒေါင်းလုဒ်ဆွဲရန်</button></a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    audio_file = None
    text = ""
    voice = "my-MM-NilarNeural"
    if request.method == 'POST':
        text = request.form.get('text')
        voice = request.form.get('voice')
        if text:
            audio_filename = "output.mp3"
            base_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(base_dir, audio_filename)
            async def generate():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
            asyncio.run(generate())
            audio_file = audio_filename
    return render_template_string(HTML_TEMPLATE, audio_file=audio_file, text=text, voice=voice)

@app.route('/play/<filename>')
def play(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_file(os.path.join(base_dir, filename), mimetype='audio/mp3')

@app.route('/download/<filename>')
def download(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_file(os.path.join(base_dir, filename), as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)