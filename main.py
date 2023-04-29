from fastapi import FastAPI
from datetime import datetime, timedelta
import requests
import uvicorn

app = FastAPI()
token = ''
@app.get("/github-events/{offset}")
def get_github_events(offset: int):
    url = "https://api.github.com/events"
    offset_time = datetime.now() - timedelta(minutes=offset)
    offset_str = offset_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }
    params = {
        "per_page": 100,  # Increase per_page to retrieve more events per request
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

    # test = calculate_events(events=events)

    return [{'requested Events': calculate_events(events=events),  'Offset': offset} ]


def calculate_events(events: list):

    response = {}
    for event in events:
        response[event["type"]] = response.get(event["type"], 0) + 1
    return response
if __name__ == '__main__':

    uvicorn.run(app, host="127.0.0.1", port=8000)