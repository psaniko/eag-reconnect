import os
from datetime import datetime

from flask import Flask, request, render_template
import requests


GOALS = {  # level: (meetings, sessions)
    1: (5, 1),
    2: (10, 2),
    3: (15, 3),
}
API_BASE = 'https://eagreconnect.converve.io/api/v1/'
app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # get basic data
    user_id = request.args.get('user_id')
    user_hash = request.args.get('user_hash')
    if not user_id or not user_hash:
        return ''
    stats_data = converve_get(f'persinfo/{user_id}/{user_hash}')
    if not stats_data:
        return {}
    stats_data = stats_data.json()

    # set goal meetings and sessions
    goal_level = int(stats_data['goal_package'])
    goal_meetings, goal_sessions = GOALS[goal_level]

    # count current meetings and sessions
    meetings_scheduled = len(stats_data.get('meetings', []))
    sessions_attended = len([
        session
        for session in stats_data.get('sessions', [])
        if datetime.now() > datetime.strptime(session['utc_datetime_end'], '%Y-%m-%d %H:%M:%S')
    ])

    return render_template(
        'index.html',
        goal_meetings=goal_meetings,
        goal_sessions=goal_sessions,
        meetings_scheduled=meetings_scheduled,
        sessions_attended=sessions_attended,
        session_percent=min(goal_sessions, sessions_attended) / goal_sessions * 100,
        session_background_color='#90ee90' if sessions_attended >= goal_sessions else 'lightgrey',
        level=goal_level,
    )


def converve_get(path):
    converve_user = os.environ['CONVERVE_USER']
    converve_pass = os.environ['CONVERVE_PASSWORD']

    return requests.get(API_BASE + path, auth=(converve_user, converve_pass))
