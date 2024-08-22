from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    clips = get_clips()
    return render_template('index.html', clips=clips)

def get_clips():
    try:
        output = subprocess.check_output(["python3", "hyperdeck.py", "-g"]).decode('utf-8')
        clips = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 5:
                clip_number = parts[0].strip(':')
                filename = parts[1]
                format = parts[2]
                resolution = parts[3]
                duration = parts[4]
                clips.append({
                    'clip_number': clip_number,
                    'filename': filename,
                    'format': format,
                    'resolution': resolution,
                    'duration': duration
                })
        clips = sorted(clips, key=lambda x: x['resolution'])
        return clips
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")
        return []

@app.route('/play', methods=['POST'])
def play():
    filename = request.form['filename']
    try:
        # Clear current clips
        subprocess.check_call(["python3", "hyperdeck.py", "-c"])
        # Add the new clip
        subprocess.check_call(["python3", "hyperdeck.py", "-a", filename])
        # Play the new timeline
        subprocess.check_call(["python3", "hyperdeck.py", "-p"])
        return jsonify(success=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")
        return jsonify(success=False)

@app.route('/add_to_list', methods=['POST'])
def add_to_list():
    filename = request.form['filename']
    clip_number = request.form['clip_number']
    try:
        subprocess.check_call(["python3", "hyperdeck.py", "-a", filename])
        return jsonify(success=True)
    except subprocess.CalledProcessError as e:
        print(f"Add to list failed: {e}, attempting force play")
        try:
            subprocess.check_call(["python3", "hyperdeck.py", "-p"])
            return jsonify(success=True)
        except subprocess.CalledProcessError as e:
            print(f"Force play failed: {e}")
            return jsonify(success=False)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
