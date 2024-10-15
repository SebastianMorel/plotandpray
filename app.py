import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import openai
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

openai.api_key = os.getenv("OPENAI_API_KEY")

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/example')
def example():
    return render_template('example.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file, on_bad_lines='skip')
        else:
            df = pd.read_excel(file, on_bad_lines='skip')
        
        charts = analyze_and_generate_charts(df)
        
        return render_template('result.html', charts=charts)
    else:
        return jsonify({'error': 'File type not allowed'}), 400

def analyze_and_generate_charts(df):
    columns = df.columns.tolist()
    sample_data = df.head(25).to_dict(orient='records')
    
    prompt = f"""
    Given the following dataset information:
    
    Column names: {columns}
    Sample data: {sample_data}
    
    Please analyze this data and suggest 3 appropriate chart types. For each chart, provide:
    1. A brief explanation of why this chart is suitable.
    2. An appropriate title for the chart based on the data.
    3. Python code using matplotlib to create the chart.

    Respond in the following format:
    Title: [Your chart title here]
    Explanation: [Your explanation here]
    Code:
    ```python
    [Your Python code here]
    ```"""
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )

    charts = []
    chart_blocks = response.choices[0].message['content'].split('Title:')[1:]
    for block in chart_blocks:
        title = block.split('Explanation:')[0].strip()
        explanation = block.split('Explanation:')[1].split('Code:')[0].strip()
        chart_code = block.split('```python')[1].split('```')[0].strip()
        
        plt.figure(figsize=(10, 6))
        exec(chart_code)
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        chart = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        charts.append({
            'title': title,
            'explanation': explanation,
            'image': chart
        })
    
    return charts

if __name__ == '__main__':
    app.run()