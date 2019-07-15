from app import app
import webbrowser


def run_app():
    app.run()


def open_browser():
    webbrowser.open('http://127.0.0.1:5000', new=2, autoraise=True)


if __name__ == '__main__':
    open_browser()
    run_app()
