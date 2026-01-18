from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route("/")
def home():
    return redirect("/api/login")

@app.route("/api/login", methods=["GET"])
def login_page():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(port=3000, debug=True)
