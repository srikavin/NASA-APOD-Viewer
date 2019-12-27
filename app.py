import datetime
import os

import requests
from flask import Flask, make_response, abort
from flask import request, render_template
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

API_KEY = os.environ.get('API_KEY') or 'DEMO_KEY'


@cache.memoize(60 * 60 * 24)
def query_nasa_apod(date):
    params = {'hd': 'true', 'api_key': API_KEY}

    if date != 'today':
        params['date'] = date

    r = requests.get('https://api.nasa.gov/planetary/apod', params=params)
    if r.status_code != 200:
        abort(404)
    return r.json(), r.text


@app.route('/hdimg')
def get_hdimg():
    """
    Used to bypass CORS issues with the images being served by the NASA APOD API
    """
    date = request.args.get('date')

    @cache.memoize(60 * 60 * 24)
    def fetch_img(date):
        data, raw = query_nasa_apod(date)
        r = requests.get(data['hdurl'], stream=True)
        r.raw.decode_content = True
        return r.content, r.headers['content-type'], data['hdurl'].split('/')[-1]

    content, content_type, filename = fetch_img(date)

    response = make_response(content)
    response.headers.set('Cache-Control', 'max-age=1209600')
    response.headers.set('Content-Type', content_type)
    response.headers.set(
        'Content-Disposition', 'attachment', filename=filename)

    return response


@app.route('/')
def apod_api():
    date = request.args.get('date')
    if not date:
        date = "today"

    data, raw = query_nasa_apod(date)
    date = data['date']
    datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%d")

    prev_day = datetime_obj + datetime.timedelta(days=-1)
    next_day = datetime_obj + datetime.timedelta(days=1)
    prev_day_str = datetime.datetime.strftime(prev_day, "%Y-%m-%d")
    next_day_str = datetime.datetime.strftime(next_day, "%Y-%m-%d")

    context = {
        'data': data,
        'date': datetime.datetime.strftime(datetime_obj, "%Y-%m-%d"),
        'raw': raw,
        'prev_day': prev_day_str
    }

    if next_day < datetime.datetime.now():
        context['next_day'] = next_day_str

    return render_template('index.html', **context)


if __name__ == '__main__':
    app.run()
