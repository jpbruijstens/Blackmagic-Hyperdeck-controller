from flask import Flask, render_template, request, jsonify
import telnetlib
import re
import socket
import logging

app = Flask(__name__, static_url_path='/hyperdeck/static',
            static_folder='static')

TELNET_IP = '172.19.0.3'
TELNET_PORT = 9993

# Configure logging
logging.basicConfig(level=logging.INFO)


def send_telnet_command(command, tn=None):
    try:
        # If no existing connection is provided, create a new one
        if tn is None:
            tn = telnetlib.Telnet(TELNET_IP, TELNET_PORT, timeout=5)
            connection_provided = False
        else:
            connection_provided = True

        tn.write(command.encode('ascii') + b"\n")
        response = ''
        while True:
            try:
                line = tn.read_until(b"\n", timeout=1)
                if not line:
                    break
                response += line.decode('ascii')
            except EOFError:
                break
            except socket.timeout:
                # Timeout after 1 second of inactivity
                break

        # Close the connection if we created it in this function
        if not connection_provided:
            tn.close()

        return {'success': True, 'response': response.strip()}
    except socket.timeout:
        app.logger.error("Telnet command timed out.")
        return {'success': False, 'error': 'Connection timed out.'}
    except Exception as e:
        app.logger.error(f"Telnet command failed: {e}")
        return {'success': False, 'error': str(e)}


def parse_clips_response(response):
    clips = []
    lines = response.strip().split('\n')
    clip_regex = re.compile(
        r'clip id: (\d+) name: (.+?) duration: ([\d:]+) format: (.+)')
    for line in lines:
        match = clip_regex.match(line)
        if match:
            clip = {
                'id': match.group(1),
                'name': match.group(2).strip(),
                'duration': match.group(3).strip(),
                'format': match.group(4).strip(),
            }
            clips.append(clip)
        else:
            app.logger.warning(f"Failed to parse line: {line}")
    return clips


@app.route('/hyperdeck', methods=['GET', 'POST'])
def hyperdeck():
    if request.method == 'POST':
        action = request.form.get('action')
        app.logger.info(f"Action received: {action}")
        try:
            if action == 'select_disk':
                disk_id = request.form.get('disk_id')
                result = send_telnet_command(
                    f'slot select: slot id: {disk_id}')
                if result['success']:
                    return jsonify({'response': result['response']})
                else:
                    return jsonify({'error': result['error']}), 500

            elif action == 'load_clips':
                sort_by = request.form.get('sort_by')
                result = send_telnet_command('clips get')
                if result['success']:
                    clips = parse_clips_response(result['response'])
                    app.logger.info(f"Clips received: {clips}")
                    if sort_by:
                        clips.sort(key=lambda x: x.get(sort_by, ''))
                    return jsonify({'clips': clips})
                else:
                    return jsonify({'error': result['error']}), 500

            elif action == 'search_clips':
                query = request.form.get('query').lower()
                search_by = request.form.get('search_by')
                result = send_telnet_command('clips get')
                if result['success']:
                    clips = parse_clips_response(result['response'])
                    filtered_clips = []
                    for clip in clips:
                        if query in clip.get(search_by, '').lower():
                            filtered_clips.append(clip)
                    return jsonify({'clips': filtered_clips})
                else:
                    return jsonify({'error': result['error']}), 500

            elif action == 'play_loop':
                result = send_telnet_command('play: loop: true')
                if result['success']:
                    return jsonify({'response': 'Playback started in loop mode.'})
                else:
                    return jsonify({'error': result['error']}), 500

            elif action == 'add_to_timeline':
                clip_names = request.form.getlist('clips[]')
                if clip_names:
                    try:
                        app.logger.info(
                            "Opening Telnet connection for adding clips to timeline.")
                        tn = telnetlib.Telnet(
                            TELNET_IP, TELNET_PORT, timeout=5)
                    except Exception as e:
                        app.logger.error(
                            f"Failed to connect to HyperDeck: {e}")
                        return jsonify({'error': f"Failed to connect to HyperDeck: {e}"}), 500

                    success = True
                    for clip_name in clip_names:
                        app.logger.info(
                            f"Sending command to add clip: {clip_name}")
                        # Send the command to add the clip by name using the existing connection
                        result = send_telnet_command(
                            f'clips add: name: {clip_name}', tn=tn)
                        if not result['success']:
                            app.logger.error(
                                f"Failed to add clip {clip_name}: {result['error']}")
                            success = False
                            error_message = result['error']
                            break  # Stop sending commands if an error occurs

                    tn.close()  # Close the connection after all commands
                    app.logger.info(
                        "Closed Telnet connection after adding clips.")

                    if success:
                        return jsonify({'response': 'Selected clips added to timeline.'})
                    else:
                        return jsonify({'error': error_message}), 500
                else:
                    return jsonify({'error': 'No clips selected.'}), 400

            elif action == 'clear_timeline':
                # Send the command to clear the timeline
                result = send_telnet_command('clips clear')
                if result['success']:
                    return jsonify({'response': 'Timeline cleared successfully.'})
                else:
                    return jsonify({'error': result['error']}), 500

            else:
                return jsonify({'error': 'Unknown action.'}), 400

        except Exception as e:
            app.logger.error(f"An error occurred: {e}")
            return jsonify({'error': f"An error occurred: {e}"}), 500

    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
