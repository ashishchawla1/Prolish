import linkedin_graper
import scrapper2
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Application starting...")
# session_cookie = os.getenv("SESSION_COOKIE")
api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class ScrapeAndGradeRequest(BaseModel):
    session_cookie: str
    profile_name: str

@app.post('/scrape_and_grade')
def scrape_and_grade(request: ScrapeAndGradeRequest):
    session_cookie = request.session_cookie
    profile_name = request.profile_name
    
    if not session_cookie or not profile_name:
        raise HTTPException(status_code=400, detail='session_cookie and profile_name are required')

    # Build the LinkedIn profile URL
    profile_url = f"https://www.linkedin.com/in/{profile_name}/"

    # Scrape the LinkedIn profile
    profile_data = scrapper2.scrape_linkedin_profile(profile_url, session_cookie)

    # Load the grading parameters from an Excel file
    # grading_parameters = pd.read_excel('grading_parameters.xlsx')

    # # Grade the LinkedIn profile
    # warm, deep, wide = linkedin_graper.grade_linkedin_profile(grading_parameters, profile_data, api_key)

    # Extract the scores using regex
    # warm_match=warm.split("/n")[-1].strip()
    # if warm_match:
    #     warm_score=warm_match.group(1)
    # else:
    #     warm_score=None

    # deep_match=deep.split("/n")[-1].strip()
    # if deep_match:
    #     deep_score=deep_match.group(1)
    # else:
    #     deep_score=None

    # wide_match=wide.split("/n")[-1].strip()
    # if wide_match:
    #     wide_score=wide_match.group(1)
    # else:
    #     wide_score=None

    # Return the results as a JSON response
    return {
        'profile_data': profile_data,
        # 'warm': warm,
        # 'deep': deep,
        # 'wide': wide,
        # "warm_score": warm.split("/n")[-1][-4:].strip(),
        # "deep_score": deep.split("/n")[-1][-4:].strip(),
        # "wide_score": wide.split("/n")[-1][-4:].strip()
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
