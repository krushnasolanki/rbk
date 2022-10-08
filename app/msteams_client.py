import os
import requests


def post_to_msteams(content: str):
    """
      - Send a teams notification to the desired webhook_url
      - Returns the status code of the HTTP request
        - webhook_url : the url you got from the teams webhook configuration
        - content : your formatted notification content
        - title : the message that'll be displayed as title, and on phone notifications
        - color (optional) : hexadecimal code of the notification's top line color, default corresponds to black
    """

    msteams_channel = os.environ.get("EXCEP_MSTEAMS_CHANNEL").strip()
    webhook_url = os.environ.get("WEBHOOK_URL").strip()

    color = "000000"
    title = "CBE ERROR"

    resp = requests.post(
        url=webhook_url,
        headers={"Content-Type": "application/json"},
        json={
            "themeColor": color,
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": content
            }],
        },
    )
    return resp
