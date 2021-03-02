import os
from datetime import datetime

from flask import Flask, request
import requests


API_BASE = 'https://eagreconnect.converve.io/api/v1/'
app = Flask(__name__)


@app.route('/')
def catch_all():
    user_id = request.args.get('user_id')
    user_hash = request.args.get('user_hash')
    stats_data = converve_get(f'persinfo/{user_id}/{user_hash}')
    if not stats_data:
        return {}

    stats_data = stats_data.json()

    # get goal meetings and sessions
    goal_meetings = 10  # TODO
    goal_sessions = 2  # TODO

    # count current meetings and sessions
    meetings_scheduled = len(stats_data.get('meetings', []))
    sessions_attended = len([
        session
        for session in stats_data.get('sessions', [])
        if datetime.now() > datetime.strptime(session['utc_datetime_end'], '%Y-%m-%d %H:%M:%S')
    ])

    return {
        'status': 200,
        'data': {
            'goal_meetings': goal_meetings,
            'goal_sessions': goal_sessions,
            'meetings_scheduled': meetings_scheduled,
            'sessions_attended': sessions_attended,
        },
    }


def converve_get(path):
    converve_user = os.environ['CONVERVE_USER']
    converve_pass = os.environ['CONVERVE_PASSWORD']

    return requests.get(API_BASE + path, auth=(converve_user, converve_pass))
