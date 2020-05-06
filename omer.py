from util import process_args
from hebrew import textforday
from flask import Flask, request, send_from_directory, make_response
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
    response = make_response(send_from_directory('', 'omer.html'))
    response.cache_control.no_cache = True
    return response

@app.route('/fonts/<hash>/<path:path>')
def send_font(hash, path):
    response = make_response(send_from_directory('data/fonts', path))
    response.cache_control.max_age = 60 * 60 * 24 * 365
    return response

@app.route('/icon/<hash>/<path:path>')
def send_icon(hash, path):
    response = make_response(send_from_directory('data/icon', path))
    response.cache_control.max_age = 60 * 60 * 24 * 365
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')