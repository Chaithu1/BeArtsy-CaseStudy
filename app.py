from flask import Flask

app = Flask(__name__)

@app.get("/")
def health_check():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(port=8080, debug=True)
