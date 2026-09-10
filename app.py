from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)



# IBM WATSONX SETTINGS

IBM_API_KEY = os.getenv("wtRpJuVI0UoyqeJVR0ATx2hu-Pu0DZ-sU2HkQCdPSUbg")
WATSONX_PROJECT_ID = os.getenv("5f5886ca-b9a4-4eae-860c-ee24f03df6f8")
WATSONX_URL = os.getenv(
    "WATSONX_URL",
    "https://us-south.ml.cloud.ibm.com"
)

MODEL_ID = "ibm/granite-3-2-8b-instruct"



# GET IBM ACCESS TOKEN


def get_access_token():

    if not IBM_API_KEY:
        return None

    url = "https://iam.cloud.ibm.com/identity/token"

    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": IBM_API_KEY
    }

    response = requests.post(url, data=data)

    if response.status_code != 200:
        print("IBM authentication error:")
        print(response.text)
        return None

    return response.json()["access_token"]




def generate_ai_response(prompt):


    if not IBM_API_KEY or not WATSONX_PROJECT_ID:

        return """
        DEMO AI RESPONSE

        The Research Agent analyzed the requested topic.

        The system identified important research themes,
        current approaches, limitations and possible future
        research directions.

        Add your IBM Cloud API key and watsonx.ai project ID
        in the .env file to connect the application to IBM
        Granite.
        """

    token = get_access_token()

    if not token:
        return "Unable to authenticate with IBM watsonx.ai."

    url = (
        WATSONX_URL
        + "/ml/v1/text/generation?version=2024-05-31"
    )

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    data = {
        "input": prompt,
        "model_id": MODEL_ID,
        "project_id": WATSONX_PROJECT_ID,
        "parameters": {
            "max_new_tokens": 700,
            "temperature": 0.6,
            "top_p": 0.9
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        print("Watsonx error:")
        print(response.text)

        return "IBM watsonx.ai returned an error."

    result = response.json()

    try:
        return result["results"][0]["generated_text"]
    except Exception:
        return "No response was generated."


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "index.html",
        result=None
    )


# ---------------------------------------------------------
# RESEARCH API
# ---------------------------------------------------------

@app.route("/research", methods=["POST"])
def research():

    data = request.get_json()

    topic = data.get("topic", "").strip()

    if not topic:

        return jsonify({
            "success": False,
            "message": "Please enter a research topic."
        })

    # -----------------------------------------------------
    # STEP 1 - SEARCH QUERIES
    # -----------------------------------------------------

    query_prompt = f"""
You are an academic research query generation agent.

Research topic:
{topic}

Generate 5 highly relevant academic search queries
for finding research papers.

Give only the five queries as a numbered list.
"""

    queries = generate_ai_response(query_prompt)


    # -----------------------------------------------------
    # STEP 2 - LITERATURE ANALYSIS
    # -----------------------------------------------------

    analysis_prompt = f"""
You are an AI literature review assistant.

Research topic:
{topic}

Based on this research topic, provide:

1. Overview of the research area
2. Important research themes
3. Common methodologies
4. Major findings
5. Current challenges

Use clear academic language.
"""

    analysis = generate_ai_response(analysis_prompt)


    # -----------------------------------------------------
    # STEP 3 - RESEARCH GAPS
    # -----------------------------------------------------

    gap_prompt = f"""
You are a research gap detection agent.

Research topic:
{topic}

Identify:

1. Major research gaps
2. Current limitations
3. Unexplored areas
4. Possible future research directions
5. Potential innovative approaches

Provide the answer in clear sections.
"""

    gaps = generate_ai_response(gap_prompt)


  
    # STEP 4 - LITERATURE REVIEW
    

    report_prompt = f"""
You are an academic literature review generation agent.

Research topic:
{topic}

Prepare a concise literature review containing:

1. Introduction
2. Current research
3. Key themes
4. Research gaps
5. Future directions
6. Conclusion

Use formal academic language.
"""

    report = generate_ai_response(report_prompt)



    # RETURN RESULT
  

    return jsonify({

        "success": True,

        "topic": topic,

        "queries": queries,

        "analysis": analysis,

        "gaps": gaps,

        "report": report

    })


# RUN APPLICATION


if __name__ == "__main__":

    print("=" * 60)
    print("AI RESEARCH AGENT")
    print("=" * 60)
    print("Starting Flask server...")
    print("Open http://127.0.0.1:5000")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )