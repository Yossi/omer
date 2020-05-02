from util import process_args
from hebrew import textforday
from flask import Flask, request, send_from_directory
app = Flask(__name__)

@app.route('/omer')
def omer():
    args = {}

    form = request.args
    args['zipcode'] = form.get('zipcode') or '94303'
    args['ll'] = form.get('lat'), form.get('lng')
    args['date'] = form.get('date') or ''
    args['dateline'] = form.get('dateline') or ''
    args['passed_day'] = form.get('day') # override calculated day if user passes a day explicitly
    process_args(args)

    return textforday(args)

@app.route('/')
@app.route('/omer.html')
def send_index():
    return send_from_directory('', 'omer.html')

@app.route('/fonts/<path:path>')
def send_font(path):
    return send_from_directory('data/fonts', path)

@app.route('/icon/<path:path>')
def send_icon(path):
    return send_from_directory('data/icon', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')