from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def introduce_template_render():
    return render_template("introduce.html")


@app.route("/profile")
def profile():
    hobbies = ["영화", "운동", "게임"]
    return render_template("profile.html", hobbies=hobbies)


if __name__ == "__main__":
    app.run(debug=True)
