from destination_service import app as destination_app
from user_service import app as user_app
from authentication_service import app as auth_app

if __name__ == '__main__':
    import threading

    def run_app(app, port):
        app.run(port=port)

    threading.Thread(target=run_app, args=(user_app, 5000)).start()
    threading.Thread(target=run_app, args=(auth_app, 5001)).start()
    threading.Thread(target=run_app, args=(destination_app, 5002)).start()
