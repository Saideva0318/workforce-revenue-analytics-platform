#!/usr/bin/env python3
"""
Recruitment AI Agent - Make Call Script
Places a real Twilio voice call to Sai Deva Puttur with Data Engineer screening questions.
Credentials loaded from environment variables / GitHub Actions Secrets.
"""
import os
import sys
from twilio.rest import Client

# Credentials loaded from environment variables (set as GitHub Secrets)
ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN  = os.environ["TWILIO_AUTH_TOKEN"]
FROM_NUMBER = os.environ["TWILIO_FROM_NUMBER"]
TO_NUMBER   = os.environ["TWILIO_TO_NUMBER"]

# TwiML voice script - read aloud by Twilio text-to-speech (Amazon Polly)
TWIML_SCRIPT = """
<Response>
  <Pause length="15"/>
  <Say voice="Polly.Joanna" rate="90%">
    Hello! May I please speak with Sai Deva Puttur?
  </Say>
  <Pause length="15"/>
  <Say voice="Polly.Joanna" rate="90%">
    Hi Sai Deva! This is Aria, the AI Recruitment Assistant calling on behalf
    of the Talent Acquisition team at Laksan Technologies LLC.
    I hope I am not catching you at a bad time.
  </Say>
  <Pause length="2"/>
  <Say voice="Polly.Joanna" rate="90%">
    We have a few quick screening questions for the Senior Data Engineer position.
    This will only take about 5 minutes.
  </Say>
  <Pause length="6"/>
  <Say voice="Polly.Joanna" rate="90%">
    Question 1. Can you describe your hands-on experience with Snowflake and dbt?
    Have you built data models or transformations using these tools in a production environment?
  </Say>
  <Pause length="10"/>
  <Say voice="Polly.Joanna" rate="90%">
    Thank you. Question 2. Can you walk me through how you have designed
    an ETL or ELT pipeline end to end?
    What tools did you use and what was the data volume?
  </Say>
  <Pause length="10"/>
  <Say voice="Polly.Joanna" rate="90%">
    Great. Question 3. Tell me about a time you optimized a slow SQL query or pipeline.
    What was the problem and how did you fix it?
  </Say>
  <Pause length="10"/>
  <Say voice="Polly.Joanna" rate="90%">
    Question 4. What is your experience with Apache Airflow?
    Have you written DAGs and managed pipeline failures?
  </Say>
  <Pause length="10"/>
  <Say voice="Polly.Joanna" rate="90%">
    Question 5. Are you open to hybrid or on-site work in New Jersey?
    And what is your current work authorization status?
  </Say>
  <Pause length="10"/>
  <Say voice="Polly.Joanna" rate="90%">
    Last question. What is your expected salary range for a Senior Data Engineer role?
  </Say>
  <Pause length="10"/>
  <Say voice="Polly.Joanna" rate="90%">
    Wonderful, Sai Deva! Thank you so much for your time today.
    Based on your responses, our recruiting team will follow up within 2 business days
    to schedule a technical interview.
    You will receive a calendar invite at your registered email address.
    Have a great afternoon and we look forward to speaking with you again!
  </Say>
  <Pause length="1"/>
</Response>"""

def make_screening_call():
    """Place Twilio outbound voice call to the candidate."""
    print("=" * 60)
    print("  RECRUITMENT AI AGENT - INITIATING REAL CALL")
    print("=" * 60)
    print(f"  Candidate : Sai Deva Puttur")
    print(f"  Calling   : {TO_NUMBER}")
    print(f"  From      : {FROM_NUMBER}")
    print("=" * 60)

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    call = client.calls.create(
        twiml=TWIML_SCRIPT,
        to=TO_NUMBER,
        from_=FROM_NUMBER
    )

    print(f"\n  CALL INITIATED SUCCESSFULLY!")
    print(f"  Call SID  : {call.sid}")
    print(f"  Status    : {call.status}")
    print(f"  Direction : {call.direction}")
    print("\n  Twilio is now dialing the candidate...")
    print("  The candidate will hear the Data Engineer screening questions.")
    print("=" * 60)
    print("  Track live: https://console.twilio.com/us1/monitor/calls")
    print("=" * 60)
    return call.sid

if __name__ == "__main__":
    make_screening_call()
