from flask import Flask, render_template
from dotenv import load_dotenv

# Carga las variables de entorno desde .flaskenv o .env
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
