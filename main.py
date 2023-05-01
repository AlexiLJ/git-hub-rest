from fastapi import FastAPI

from datetime import datetime
import os
import matplotlib.pyplot as plt
from fastapi.responses import HTMLResponse
import uvicorn
import io
import base64
from utilities import get_requested_events, get_average_time_btwn_pull_req, calculate_requested_events


app = FastAPI()
token = os.environ['GIT_HUB_TOCKEN']


@app.get("/github-events/{offset}")
def get_github_events(offset: int):
    events = get_requested_events(offset, token=token)
    avg_pulls = get_average_time_btwn_pull_req(events=events, token=token)
    response = [{'Requested Events': calculate_requested_events(events=events),  'Offset': offset},
                {'Average Time Between Pull Request': avg_pulls} ]
    return response


@app.get("/github-events-plot/{offset}")
def get_github_events(offset: int):
    events = get_requested_events(offset=offset, token=token)
    avg_pulls = get_average_time_btwn_pull_req(events=events, token=token)

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


if __name__ == '__main__':

    uvicorn.run(app, host="127.0.0.1", port=8000)