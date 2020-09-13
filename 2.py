from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/hello/<name>')
def hello_name(name):
    res = f'Hello {name}!'
    return jsonify({'name': res})


@app.route('/get_post', methods=['POST', 'GET'])
def get_post():
    if request.method == 'POST':
        user = request.form['name']
        return jsonify({'user from post': user})
    else:
        user = request.args.get('name')
        return jsonify({'user from get': user})


if __name__ == '__main__':
    app.run(debug=True)
