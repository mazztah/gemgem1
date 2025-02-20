from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('advanced_snake.html')

if __name__ == '__main__':
    app.run(debug=True)
