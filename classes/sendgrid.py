import requests
import datetime

def send_email(email, key):

    endpoint_url = "https://api.sendgrid.com/v3/mail/send"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    headers = {
        "Authorization": "Bearer ",
        'content-type': "application/json"
    }

    payload = {
        "personalizations": [{
            "to": [{
                "email": email
            }],
            "subject": "Welcome",
            "dynamic_template_data": {
                "timestamp": timestamp,
                "key": key
            }
        }],
        "from": {
            "email": "no-reply@rose.io",
            "name": "Rose Supreme"
        },

        "template_id": "d-863a8d509ee345fe9d21957be4b0fb28"
    }

    resp = requests.post(endpoint_url, headers=headers, json=payload)

    try:
        resp.raise_for_status()
        return(f"Email sent to: {email}")
    except:
        return(f"Email failed to send to: {email}")
