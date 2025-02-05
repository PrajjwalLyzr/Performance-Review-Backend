import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def send_message(agent_id, user_id, session_id, message):
        url = os.getenv("AGENT_URL")

        headers = {
            "accept": "application/json",
            "x-api-key":  os.getenv("X_API_KEY")
        }

        payload = json.dumps({
            "user_id": user_id,
            "agent_id": agent_id,
            "session_id": session_id,
            "message": message
        })

        response = requests.post(url, headers=headers, data=payload)


        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None



def performance_analysis_agent(employee_data):
    performance_report = send_message(
         agent_id=os.getenv("PERFORMANE_AGENT_ID"),
         user_id=os.getenv("USER_ID"),
         session_id=os.getenv("PERFORMANE_SESSION_ID"),
         message=f"[!Important] Always give response in just JSON format, data: {employee_data}"
    )


    return performance_report['response']



def things_to_work_on_analysis_agent(performance_report):
    things_to_work = send_message(
         agent_id=os.getenv("THINGS_TO_WORK_AGENT_ID"),
         user_id=os.getenv("USER_ID"),
         session_id=os.getenv("THINGS_TO_WORK_SESSION_ID"),
         message=f"[!Important] Always give response in just JSON format, performance report: {performance_report}"
    )

    return things_to_work['response']


