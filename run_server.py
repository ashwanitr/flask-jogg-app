from flask_app import app

"""
Starting point for Flask Application
Run `python run_server.py` from command line to start the server
Make sure to complete following things before running the server:
 -> requirements.txt file contains all the python dependencies required by this application. 
    Create a virtual env and pip install all the required dependencies.
 -> Initialize the sqlite database first before running the flask server
"""

if __name__ == '__main__':
    app.run(debug=True)
