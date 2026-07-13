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
  <Pause length="3"/>
  <Say voice="Polly.Joanna" rate="90%">
    Hello! May I please speak with Dhananjaya Sirasati?
  </Say>
  <Pause length="6"/>
  <Say voice="Polly.Joanna" rate="90%">
    Hi Dananjaya! This is Aria, the AI Assistant calling on behalf
    of the Talent Acquisition team at Kashiv biosciences.
    I hope I am not catching you at a bad time.
  </Say>
  <Pause length="2"/>
  <Say voice="Polly.Joanna" rate="90%">
    We have a few quick questions for the todays Onboarding.
    This will only take about 5 minutes.
  </Say>
  <Pause length="6"/>
  <Say voice="Polly.Joanna" rate="90%">
    Question 1. Can you describe how is your 1st day of the work production environment?
  </Say>
  <Pause length="15"/>
  <Say voice="Polly.Joanna" rate="90%">
    Thank you. Question 2. Can you walk me through your Onboarding process how they treated you?
  </Say>
  <Pause length="15"/>
  <Say voice="Polly.Joanna" rate="90%">
    Question 3. why are you planning to take a car instead of bycycle?
  </Say>
  <Pause length="10"/>
  <Say voice="Polly.Joanna" rate="90%">
    Wonderful, Dananjaya! Thank you so much for your time today.
    Based on your responses, our team will follow up within 2 business days
    to schedule a interview and let you know Bycycle or Car, let's discuss.
    You will receive a calendar invite at your registered email address.
    Have a great evening and we look forward to speaking with you again!
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
