import telnetlib
import argparse
import time

# Global variable to store the disk list
disk_list = []

# Function to send telnet commands to the Hyperdeck
def send_telnet_command(host, port, command):
    with telnetlib.Telnet(host, port) as tn:
        tn.write(command.encode('ascii') + b'\n')
        time.sleep(0.5)  # Wait for response
        response = tn.read_very_eager().decode('ascii')
        return response.strip()

# Function to get the disk list
def get_disk_list(host, port):
    global disk_list
    response = send_telnet_command(host, port, 'disk list')
    disk_list = response.split('\n')
    return response

# Function to clear clips
def clear_clips(host, port):
    response = send_telnet_command(host, port, 'clips clear')
    return response

# Function to add a clip
def add_clip(host, port, name):
    command = f'clips add: name: {name}'
    response = send_telnet_command(host, port, command)
    return response

# Function to get clips
def get_clips(host, port):
    response = send_telnet_command(host, port, 'clips get')
    return response

# Function to play clips in loop
def play_clips_loop(host, port):
    response = send_telnet_command(host, port, 'play: loop: true')
    return response

# Main function to parse arguments and execute commands
def main():
    parser = argparse.ArgumentParser(description='Control Blackmagic Hyperdeck via Telnet.')
    parser.add_argument('-a', '--add', type=str, help='Add a clip with the given name.')
    parser.add_argument('-c', '--clear', action='store_true', help='Clear all clips.')
    parser.add_argument('-g', '--get', action='store_true', help='Get list of clips.')
    parser.add_argument('-p', '--play', action='store_true', help='Play clips in loop.')

    args = parser.parse_args()

    host = '10.1.12.201'
    port = 9993

    # Get the disk list at the start
    print("Getting disk list...")
    disks = get_disk_list(host, port)
    print("Disk list:", disks)

    if args.clear:
        print("Clearing clips...")
        response = clear_clips(host, port)
        print("Response:", response)

    if args.add:
        print(f"Adding clip: {args.add}")
        response = add_clip(host, port, args.add)
        print("Response:", response)

    if args.get:
        print("Getting clips...")
        response = get_clips(host, port)
        print("Response:", response)

    if args.play:
        print("Playing clips in loop...")
        response = play_clips_loop(host, port)
        print("Response:", response)

if __name__ == '__main__':
    main()
