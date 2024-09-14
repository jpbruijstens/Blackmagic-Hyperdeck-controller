import socket
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to stderr (usually the console)
    ]
)

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 9993       # Port to listen on (same as TELNET_PORT in your app)


def handle_command(command):
    command = command.strip()
    logging.info(f'Handling command: "{command}"')
    if command.startswith('slot select: slot id:'):
        return '200 ok'
    elif command == 'clips get':
        # Return a sample list of clips
        response = '\n'.join([
            'clip id: 1 name: clip1.mov duration: 00:01:00:00 format: QuickTimeUncompressed',
            'clip id: 2 name: clip2.mov duration: 00:02:00:00 format: QuickTimeProResHQ',
            'clip id: 3 name: clip3.mov duration: 00:03:00:00 format: DNxHD',
            'clip id: 4 name: test_clip.mov duration: 00:04:00:00 format: QuickTimeProResLT',
        ])
        return response
    elif command == 'play: loop: true':
        return '200 ok'
    elif command.startswith('clips add: name:'):
        return '200 ok'
    else:
        return '500 unknown command'


def client_thread(conn, addr):
    logging.info(f'Connected by {addr}')
    with conn:
        buffer = b''
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data
                if b'\n' in buffer:
                    # Split the buffer into lines
                    lines = buffer.split(b'\n')
                    # Keep the last part (incomplete command) in the buffer
                    buffer = lines[-1]
                    # Process all complete commands
                    for line in lines[:-1]:
                        command = line.decode('ascii').strip()
                        if command:
                            logging.info(f'Received command: "{command}"')
                            response = handle_command(command)
                            conn.sendall(response.encode('ascii') + b'\n')
            except ConnectionResetError:
                logging.warning(f'Connection reset by {addr}')
                break
            except Exception as e:
                logging.error(f'Error: {e}')
                break
        logging.info(f'Connection closed by {addr}')


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logging.info(f'Mock HyperDeck server listening on port {PORT}')
        while True:
            conn, addr = s.accept()
            threading.Thread(target=client_thread, args=(
                conn, addr), daemon=True).start()


if __name__ == '__main__':
    start_server()
