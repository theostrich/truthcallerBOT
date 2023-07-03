from flask import Flask

app = Flask('')
app.config['MONGODB_CONNECT'] = False


@app.route('/')
def main():
  return "Your bot is alive!"

def run():
  app.run(host="0.0.0.0", port=8080)
