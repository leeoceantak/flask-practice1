from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def introduce_template_render():
    return render_template("introduce.html")


if __name__ == "__main__":
    app.run(debug=True)
