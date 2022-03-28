from flask import Flask, render_template

app = Flask(__name__)


@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html', title="ржач")


@app.route("/example")
def about():
    return render_template('example.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
