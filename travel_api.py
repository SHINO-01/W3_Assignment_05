import threading
import logging
import socket
from destination_service import app as destination_app
from user_service import app as user_app
from authentication_service import app as auth_app

logging.basicConfig(level=logging.INFO)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_app(app, port):
    if is_port_in_use(port):
        logging.error(f"Port {port} is already in use.")
        return
    try:
        logging.info(f"Starting app on port {port}")
        app.run(host='localhost', port=port)
    except Exception as e:
        logging.error(f"Error running app on port {port}: {e}")

if __name__ == '__main__':
    threads = [
        threading.Thread(target=run_app, args=(user_app, 5000), daemon=True),
        threading.Thread(target=run_app, args=(auth_app, 5001), daemon=True),
        threading.Thread(target=run_app, args=(destination_app, 5002), daemon=True)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
