from secure_scaffold import factories


app = factories.AppFactory().generate()


@app.route('/')
def home():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
