import webbrowser
import threading

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

# wait 4 seconds so Django fully starts
threading.Timer(4, open_browser).start()
