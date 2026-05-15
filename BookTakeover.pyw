import os
import time
import threading

import requests
import server
import gui


def run_server():
    os.chdir(os.path.dirname(__file__) or ".")
    server.init_db()
    server.app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__) or ".")

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    for _ in range(20):
        try:
            requests.get("http://127.0.0.1:5000/books", timeout=1)
            break
        except requests.exceptions.RequestException:
            time.sleep(0.25)

    gui.root.mainloop()
