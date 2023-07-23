from quart import Quart

app = Quart('')
app.config['MONGODB_CONNECT'] = False


@app.route('/')
def main():
  return "Your bot is alive!"
