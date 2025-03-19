from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import os
import json
import time

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Required for session management

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        betting_code = request.form.get('betting_code')
        
        if betting_code:
            # Store the code in session for reference
            session['bet9ja_code'] = betting_code
            
            # Run first script to process the Bet9ja code
            try:
                subprocess.run(['python', 'paste.py', betting_code], check=True)
                return redirect(url_for('processing'))
            except subprocess.CalledProcessError as e:
                return render_template('index.html', error=f"Error running first script: {str(e)}")
        else:
            return render_template('index.html', error="Please enter a betting code")
    
    return render_template('index.html')

@app.route('/processing')
def processing():
    bet9ja_code = session.get('bet9ja_code', '')
    
    # Check if real.json exists
    if not os.path.exists('real.json'):
        return render_template('index.html', 
                              error="Error: real.json file not found. First script failed.")
    
    return render_template('processing.html', bet9ja_code=bet9ja_code)

@app.route('/process_sporty')
def process_sporty():
    # Run the wrapper script for sport.py
    try:
        subprocess.run(['python', 'sport_wrapper.py'], check=True)
        
        # Try to find the SportyBet code
        sporty_code = extract_sporty_code()
        
        if sporty_code:
            return redirect(url_for('result', code=sporty_code))
        else:
            return render_template('index.html', 
                                  error="Could not find SportyBet booking code in the output")
    except subprocess.CalledProcessError as e:
        return render_template('index.html', 
                              error=f"Error running sport script: {str(e)}")

def extract_sporty_code():
    """Extract the SportyBet booking code"""
    # First try the dedicated file
    if os.path.exists('sporty_code.txt'):
        with open('sporty_code.txt', 'r') as f:
            code = f.read().strip()
            if code:
                return code
    
    # Try the log file
    if os.path.exists('sport_output.log'):
        with open('sport_output.log', 'r') as f:
            content = f.read()
            import re
            matches = re.search(r'BOOKING CODE:\s*([A-Z0-9]+)', content)
            if matches:
                return matches.group(1)
    
    # Check if the code is in real.json
    try:
        with open('real.json', 'r') as f:
            data = json.load(f)
            if 'sporty_code' in data:
                return data['sporty_code']
    except:
        pass
    
    return None

@app.route('/result')
def result():
    sporty_code = request.args.get('code', '')
    bet9ja_code = session.get('bet9ja_code', '')
    
    return render_template('result.html', 
                          sporty_code=sporty_code,
                          bet9ja_code=bet9ja_code)

if __name__ == '__main__':
    # Make sure we have a directory for templates
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True)