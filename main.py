from fastapi import FastAPI
import time
from datetime import datetime, timedelta
import requests
import os
import matplotlib.pyplot as plt
from fastapi.responses import HTMLResponse
import uvicorn
import io
import base64


app = FastAPI()
token = os.environ['GIT_HUB_TOCKEN']


@app.get("/github-events/{offset}")
def get_github_events(offset: int):
    events = get_requested_events(offset=offset)
    avg_pulls = get_average_time_btwn_pull_req(events=events)
    response = [{'Requested Events': calculate_requested_events(events=events),  'Offset': offset},
                {'Average Time Between Pull Request': avg_pulls} ]
    return response


@app.get("/github-events-plot/{offset}")
def get_github_events(offset: int):
    events = get_requested_events(offset=offset)
    avg_pulls = get_average_time_btwn_pull_req(events=events)

    avg_pulls = {k: v for k, v in avg_pulls.items() if v} # getting rid of None
    avg_pulls = dict(sorted(avg_pulls.items(), key=lambda x: datetime.strptime(x[1], "%H:%M:%S")))
    fig, ax = plt.subplots()
    ax.bar(*zip(*avg_pulls.items()))
    ax.set_xlabel('Directory')
    ax.set_ylabel('Average time between pull requests', fontsize=10)
    ax.set_xticklabels(avg_pulls.keys(), rotation=45, ha='right', fontsize=5)
    ax.set_yticklabels(avg_pulls.values(), fontsize=8)

    plt.subplots_adjust(bottom=0.4, left=0.2, right=0.9, top=0.9)

    # Save the plot as a PNG image
    png_output = io.BytesIO()
    fig.savefig(png_output, format='png', dpi=200)
    plt.close(fig)
    png_base64 = base64.b64encode(png_output.getvalue()).decode("ascii")
    img_html = f'<img src="data:image/png;base64,{png_base64}"/>'

    return HTMLResponse(content=img_html, status_code=200)

def get_requested_events(offset: int):
    url = "https://api.github.com/events"
    offset_time = datetime.now() - timedelta(minutes=offset)
    offset_str = offset_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }
    params = {
        "per_page": 100,
        "event_type": "WatchEvent,PullRequestEvent,IssuesEvent",
        "since": offset_str
    }
    events = []
    page = 1
    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            break
        page_events = response.json()

        filtered_events = [event for event in page_events if event['type'] in ['WatchEvent', 'PullRequestEvent', 'IssuesEvent']]
        events.extend(filtered_events)
        page += 1
    return events

def calculate_requested_events(events: list) -> dict:

    response = {}
    for event in events:
        response[event["type"]] = response.get(event["type"], 0) + 1
    return response

def get_average_time_btwn_pull_req(events: list) -> dict:

    times = {}
    for event in events:
        url = f"https://api.github.com/repos/{event['repo']['name']}/pulls"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"state": "closed"}
        response = requests.get(url, headers=headers, params=params)
        pulls = response.json()
        total_time = 0
        num_pulls = 0

        # Loop through the pull requests and calculate the time between opening and closing
        for pull in pulls:

            try:
                created_at = datetime.strptime(pull["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                closed_at = datetime.strptime(pull["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
                time_diff = (closed_at - created_at).total_seconds()
            except:
                print('corrupt', pull)
                continue
            # Add the time difference to the total time
            total_time += time_diff
            num_pulls += 1

        # Calculate the average time between pull requests
        if num_pulls > 0:
            avg_time = total_time / num_pulls
            avg_time = time.strftime('%H:%M:%S', time.gmtime(avg_time))
        else:
            avg_time = None
        times[event['repo']['name']] = avg_time
    return times


if __name__ == '__main__':

    uvicorn.run(app, host="127.0.0.1", port=8000)