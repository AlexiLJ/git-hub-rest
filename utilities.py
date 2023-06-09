from datetime import datetime, timedelta
import time
import requests

def get_requested_events(offset: int, token: str) -> list:
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

def get_average_time_btwn_pull_req(events: list,  token: str) -> dict:

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
