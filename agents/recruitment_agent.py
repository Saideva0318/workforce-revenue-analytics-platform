#!/usr/bin/env python3
"""
Recruitment AI Agent for Workforce Analytics Platform
Author: Saideva0318
Description: Autonomous agent for candidate screening, resume parsing,
             skills matching, and automated scheduling.
"""

import os
import json
import yaml
import openai
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Candidate:
    """Data class for candidate information"""
    candidate_id: str
    name: str
    email: str
    phone: str
    resume_text: str
    skills: List[str]
    experience_years: float
    education: str
    source: str
    applied_position: str
    match_score: Optional[float] = None
    ai_summary: Optional[str] = None


@dataclass
class JobPosting:
    """Data class for job posting"""
    job_id: str
    title: str
    department: str
    required_skills: List[str]
    experience_required: float
    description: str
    salary_range: str


class RecruitmentAgent:
    """AI-powered recruitment agent for automated candidate screening"""

    def __init__(self, config_path: str = "agent_config.yaml"):
        """Initialize the agent with configuration"""
        self.config = self._load_config(config_path)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        self.db_conn = None
        logger.info("Recruitment Agent initialized")

    def _load_config(self, path: str) -> Dict:
        """Load agent configuration from YAML"""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {path} not found. Using defaults.")
            return self._default_config()

    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "agent_name": "Recruitment AI Agent",
            "version": "1.0.0",
            "screening_threshold": 0.7,
            "auto_schedule_interviews": True,
            "notification_email": "ta-team@company.com"
        }

    def parse_resume(self, resume_text: str) -> Dict:
        """
        Parse resume using AI to extract structured information
        
        Args:
            resume_text: Raw text from resume
            
        Returns:
            Structured dict with skills, experience, education
        """
        logger.info("Parsing resume with AI")
        
        prompt = f"""
        Extract structured information from this resume:
        
        {resume_text}
        
        Return a JSON with:
        - skills: List of technical and professional skills
        - experience_years: Total years of experience (float)
        - education: Highest degree earned
        - summary: 2-sentence candidate summary
        """
        
        try:
            if self.openai_api_key:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                result = json.loads(response.choices[0].message.content)
                return result
            else:
                # Fallback for demo without API key
                logger.warning("No OpenAI API key. Using mock parsing.")
                return self._mock_parse_resume(resume_text)
        except Exception as e:
            logger.error(f"Resume parsing error: {e}")
            return self._mock_parse_resume(resume_text)

    def _mock_parse_resume(self, resume_text: str) -> Dict:
        """Fallback parsing when AI not available"""
        return {
            "skills": ["Python", "SQL", "Data Analysis"],
            "experience_years": 5.0,
            "education": "Bachelor's Degree",
            "summary": "Experienced professional with technical background."
        }

    def calculate_match_score(self, candidate: Candidate, job: JobPosting) -> float:
        """
        Calculate how well candidate matches job requirements
        
        Args:
            candidate: Candidate object
            job: JobPosting object
            
        Returns:
            Match score between 0 and 1
        """
        logger.info(f"Calculating match for {candidate.name} vs {job.title}")
        
        # Skills match (60% weight)
        required_skills_set = set([s.lower() for s in job.required_skills])
        candidate_skills_set = set([s.lower() for s in candidate.skills])
        skills_overlap = len(required_skills_set & candidate_skills_set)
        skills_score = skills_overlap / len(required_skills_set) if required_skills_set else 0
        
        # Experience match (30% weight)
        exp_gap = abs(candidate.experience_years - job.experience_required)
        exp_score = max(0, 1 - (exp_gap / 5))  # Penalty for 5+ year gap
        
        # Education (10% weight) - simplified
        edu_score = 0.8 if "bachelor" in candidate.education.lower() else 0.5
        
        # Weighted total
        total_score = (skills_score * 0.6) + (exp_score * 0.3) + (edu_score * 0.1)
        
        logger.info(f"Match score: {total_score:.2f}")
        return round(total_score, 2)

    def generate_ai_summary(self, candidate: Candidate, job: JobPosting) -> str:
        """
        Generate AI-powered candidate summary for hiring manager
        
        Returns:
            Human-readable summary with recommendation
        """
        prompt = f"""
        Write a brief summary (3-4 sentences) for this candidate:
        
        Candidate: {candidate.name}
        Skills: {', '.join(candidate.skills)}
        Experience: {candidate.experience_years} years
        Position: {job.title}
        Match Score: {candidate.match_score}
        
        Include strengths and any concerns. Be concise and professional.
        """
        
        try:
            if self.openai_api_key:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                return response.choices[0].message.content
            else:
                return f"{candidate.name} has {candidate.experience_years} years of experience with skills in {', '.join(candidate.skills[:3])}. Match score: {candidate.match_score}."
        except Exception as e:
            logger.error(f"AI summary generation error: {e}")
            return f"Candidate with {candidate.experience_years} years experience."

    def screen_candidates(self, candidates: List[Candidate], job: JobPosting) -> List[Candidate]:
        """
        Screen and rank candidates for a job posting
        
        Returns:
            Sorted list of candidates (highest match first)
        """
        logger.info(f"Screening {len(candidates)} candidates for {job.title}")
        
        for candidate in candidates:
            # Calculate match
            candidate.match_score = self.calculate_match_score(candidate, job)
            
            # Generate AI summary
            candidate.ai_summary = self.generate_ai_summary(candidate, job)
        
        # Sort by match score (descending)
        ranked = sorted(candidates, key=lambda c: c.match_score, reverse=True)
        
        logger.info(f"Screening complete. Top candidate: {ranked[0].name} ({ranked[0].match_score})")
        return ranked

    def recommend_interview(self, candidate: Candidate) -> Dict:
        """
        Decide if candidate should proceed to interview
        
        Returns:
            Recommendation dict with decision and reasoning
        """
        threshold = self.config.get("screening_threshold", 0.7)
        
        recommendation = {
            "candidate_id": candidate.candidate_id,
            "candidate_name": candidate.name,
            "match_score": candidate.match_score,
            "recommended": candidate.match_score >= threshold,
            "stage": "Phone Screen" if candidate.match_score >= threshold else "Rejected",
            "reasoning": candidate.ai_summary,
            "timestamp": datetime.now().isoformat()
        }
        
        return recommendation

    def send_notification(self, message: str, recipient: str = None):
        """
        Send notification to TA team (placeholder for email/Slack integration)
        """
        recipient = recipient or self.config.get("notification_email")
        logger.info(f"[NOTIFICATION to {recipient}]: {message}")
        # In production, integrate with SendGrid, AWS SES, or Slack API

    def run_screening_pipeline(self, job_posting: JobPosting, candidate_pool: List[Dict]) -> Dict:
        """
        Main pipeline: Screen candidates and generate recommendations
        
        Args:
            job_posting: JobPosting object
            candidate_pool: List of raw candidate dicts
            
        Returns:
            Pipeline results with recommendations
        """
        logger.info("=" * 60)
        logger.info(f"STARTING RECRUITMENT AGENT PIPELINE FOR: {job_posting.title}")
        logger.info("=" * 60)
        
        # Convert raw data to Candidate objects
        candidates = []
        for data in candidate_pool:
            parsed = self.parse_resume(data.get("resume_text", ""))
            candidate = Candidate(
                candidate_id=data["candidate_id"],
                name=data["name"],
                email=data["email"],
                phone=data.get("phone", "N/A"),
                resume_text=data.get("resume_text", ""),
                skills=parsed["skills"],
                experience_years=parsed["experience_years"],
                education=parsed["education"],
                source=data.get("source", "Unknown"),
                applied_position=job_posting.title
            )
            candidates.append(candidate)
        
        # Screen and rank
        ranked_candidates = self.screen_candidates(candidates, job_posting)
        
        # Generate recommendations
        recommendations = [self.recommend_interview(c) for c in ranked_candidates]
        
        # Summary
        approved_count = sum(1 for r in recommendations if r["recommended"])
        
        pipeline_result = {
            "job_id": job_posting.job_id,
            "job_title": job_posting.title,
            "total_candidates": len(candidates),
            "recommended_for_interview": approved_count,
            "rejection_rate": (len(candidates) - approved_count) / len(candidates) if candidates else 0,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        # Notify TA team
        self.send_notification(
            f"Screening complete for {job_posting.title}: {approved_count}/{len(candidates)} recommended"
        )
        
        logger.info("Pipeline complete. Results:")
        logger.info(json.dumps(pipeline_result, indent=2))
        
        return pipeline_result


if __name__ == "__main__":
    # Demo usage
    agent = RecruitmentAgent()
    
    # Sample job posting
    job = JobPosting(
        job_id="JOB-2026-001",
        title="Senior Data Engineer",
        department="Engineering",
        required_skills=["Python", "SQL", "Snowflake", "dbt", "Airflow"],
        experience_required=5.0,
        description="Build scalable data pipelines",
        salary_range="$120k-$160k"
    )
    
    # Sample candidates
    candidates = [
        {
            "candidate_id": "CAND-001",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "555-1234",
            "resume_text": "5 years experience in Python, SQL, Airflow, and dbt. Built ETL pipelines.",
            "source": "LinkedIn"
        },
        {
            "candidate_id": "CAND-002",
            "name": "Bob Smith",
            "email": "bob@example.com",
            "phone": "555-5678",
            "resume_text": "2 years experience in Java and MySQL.",
            "source": "Referral"
        }
    ]
    
    # Run pipeline
    result = agent.run_screening_pipeline(job, candidates)
    
    print("\n" + "="*60)
    print("RECRUITMENT AGENT EXECUTION COMPLETE")
    print("="*60)
    print(json.dumps(result, indent=2))
