"""
Gemini AI Service
Handles resume parsing, embeddings, and AI-powered features
"""

import os
import json
import time
from typing import Dict, List, Optional
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, EMBEDDING_MODEL

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

def get_chat_model():
    """Get the chat model with current config"""
    from config import GEMINI_MODEL
    return genai.GenerativeModel(GEMINI_MODEL)

def get_embedding_model():
    """Get the embedding model name"""
    from config import EMBEDDING_MODEL
    return EMBEDDING_MODEL


class GeminiService:
    """Service for AI-powered features using Google Gemini"""

    @staticmethod
    def parse_resume(resume_text: str) -> Dict:
        """
        Parse resume text and extract structured information

        Args:
            resume_text: Raw text extracted from resume PDF

        Returns:
            Dict with parsed resume data:
            {
                'full_name': str,
                'email': str,
                'phone': str,
                'major': str,
                'graduation_year': int,
                'skills': [str],
                'work_experience': [{'company': str, 'title': str, 'duration': str, 'description': str}],
                'education': [{'school': str, 'degree': str, 'major': str, 'graduation_year': int}],
                'projects': [{'name': str, 'description': str, 'technologies': [str]}],
                'clubs': [str],
                'courses': [str],
                'industries': [str]
            }
        """

        prompt = f"""You are an expert resume parser. Extract structured information from the following resume text.

Resume Text:
{resume_text}

Extract and return the following information in valid JSON format:
{{
    "full_name": "Full name of the person (if found)",
    "email": "Email address (if found)",
    "phone": "Phone number (if found)",
    "linkedin_url": "LinkedIn profile URL (if found, look for linkedin.com/in/... links)",
    "major": "Primary major/field of study",
    "graduation_year": Expected or actual graduation year (as integer),
    "location": "Current city/location (if found)",
    "skills": ["List of technical and professional skills"],
    "work_experience": [
        {{
            "company": "Company name",
            "title": "Job title",
            "duration": "Time period (e.g., 'Jan 2023 - Present')",
            "description": "Brief description of role and achievements"
        }}
    ],
    "education": [
        {{
            "school": "University/College name",
            "degree": "Degree type (e.g., 'Bachelor of Science')",
            "major": "Major/field of study",
            "graduation_year": Year of graduation (as integer)
        }}
    ],
    "projects": [
        {{
            "name": "Project name",
            "description": "Brief description",
            "technologies": ["Technologies used"]
        }}
    ],
    "clubs": ["Student organizations and clubs"],
    "courses": ["Relevant coursework"],
    "industries": ["Industries of experience or interest (e.g., 'Technology', 'Finance', 'Healthcare')"]
}}

Important:
- Return ONLY valid JSON, no additional text
- Use null for missing fields
- Be thorough but concise
- Infer graduation year from context if not explicit
- Extract all skills mentioned (technical, soft skills, tools, languages)
- Look for LinkedIn URL in the contact information section
"""

        try:
            chat_model = get_chat_model()
            response = chat_model.generate_content(prompt)

            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            parsed_data = json.loads(response_text)

            return parsed_data

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini response: {e}")
            print(f"Response text: {response_text}")
            # Return minimal structure
            return {
                'full_name': None,
                'email': None,
                'phone': None,
                'major': None,
                'graduation_year': None,
                'skills': [],
                'work_experience': [],
                'education': [],
                'projects': [],
                'clubs': [],
                'courses': [],
                'industries': []
            }
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise

    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """
        Generate embedding vector for text using Gemini Embedding API

        Args:
            text: Text to embed (profile + resume combined)

        Returns:
            List of 768 floats representing the embedding vector
        """

        try:
            embedding_model = get_embedding_model()
            result = genai.embed_content(
                model=embedding_model,
                content=text,
                task_type="retrieval_document"
            )

            return result['embedding']

        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    @staticmethod
    def generate_profile_embedding(user_profile: Dict, resume_text: str = "") -> List[float]:
        """
        Generate embedding for a user profile

        Args:
            user_profile: Dict containing user profile data
            resume_text: Optional raw resume text

        Returns:
            768-dimensional embedding vector
        """

        # Combine all relevant profile information into text
        profile_parts = []

        if resume_text:
            profile_parts.append(f"Resume: {resume_text[:2000]}")  # Limit resume length

        if user_profile.get('full_name'):
            profile_parts.append(f"Name: {user_profile['full_name']}")

        if user_profile.get('major'):
            profile_parts.append(f"Major: {user_profile['major']}")

        if user_profile.get('current_title'):
            profile_parts.append(f"Title: {user_profile['current_title']}")

        if user_profile.get('current_company'):
            profile_parts.append(f"Company: {user_profile['current_company']}")

        if user_profile.get('career_interests'):
            interests = ', '.join(user_profile['career_interests'])
            profile_parts.append(f"Industries: {interests}")

        if user_profile.get('bio'):
            profile_parts.append(f"Bio: {user_profile['bio']}")

        # Combine into single text
        combined_text = '\n'.join(profile_parts)

        # Generate embedding
        return GeminiService.generate_embedding(combined_text)

    @staticmethod
    def generate_networking_email(sender_profile: Dict, recipient_profile: Dict) -> Dict[str, str]:
        """
        Generate a personalized networking email

        Args:
            sender_profile: Dict with sender's profile data
            recipient_profile: Dict with recipient's profile data

        Returns:
            Dict with 'subject' and 'body' keys
        """

        # Extract relevant info
        sender_name = sender_profile.get('full_name', 'A fellow member')
        sender_title = sender_profile.get('current_title', '')
        sender_company = sender_profile.get('current_company', '')
        sender_major = sender_profile.get('major', '')

        recipient_name = recipient_profile.get('full_name', 'there')
        recipient_title = recipient_profile.get('current_title', '')
        recipient_company = recipient_profile.get('current_company', '')
        recipient_major = recipient_profile.get('major', '')

        # Find common ground
        shared_interests = []
        if sender_profile.get('career_interests') and recipient_profile.get('career_interests'):
            sender_interests = set(sender_profile['career_interests'])
            recipient_interests = set(recipient_profile['career_interests'])
            shared_interests = list(sender_interests & recipient_interests)

        prompt = f"""Generate a professional networking email from {sender_name} to {recipient_name}.

Sender Info:
- Name: {sender_name}
- Title: {sender_title}
- Company: {sender_company}
- Major: {sender_major}

Recipient Info:
- Name: {recipient_name}
- Title: {recipient_title}
- Company: {recipient_company}
- Major: {recipient_major}

Shared interests: {', '.join(shared_interests) if shared_interests else 'None explicitly shared'}

Instructions:
1. The email should be 3-4 sentences maximum
2. Mention that both are Purdue Think members
3. Reference ONE specific thing about the recipient (their company, title, or industry)
4. Be warm but professional
5. Request a brief conversation or coffee chat
6. Sign off with just the sender's name

Return ONLY a JSON object with this exact format:
{{
    "subject": "A brief, professional subject line",
    "body": "The email body (3-4 sentences, no signature line needed)"
}}

Do not include greetings like "Dear" or "Hi" - just the body text. Do not include a signature or "Best regards" - just end with the content.
"""

        try:
            chat_model = get_chat_model()
            response = chat_model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean up response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            email_data = json.loads(response_text)

            # Add proper greeting and signature
            body = f"Hi {recipient_name},\n\n{email_data['body']}\n\nBest,\n{sender_name}"

            return {
                'subject': email_data.get('subject', f'Connecting from Purdue Think'),
                'body': body
            }

        except Exception as e:
            print(f"Error generating email: {e}")
            # Return a simple fallback email
            return {
                'subject': f'Connecting from Purdue Think',
                'body': f"Hi {recipient_name},\n\nMy name is {sender_name} and I'm a fellow Purdue Think member. I noticed your experience{' at ' + recipient_company if recipient_company else ''} and would love to connect and learn more about your work.\n\nWould you be open to a brief conversation?\n\nBest,\n{sender_name}"
            }

    @staticmethod
    def chat_response(user_message: str, conversation_history: List[Dict] = None, context: Dict = None) -> str:
        """
        Generate chatbot response

        Args:
            user_message: The user's message
            conversation_history: Previous messages in format [{'role': 'user'/'assistant', 'content': '...'}]
            context: Additional context (user profile, member data, etc.)

        Returns:
            Assistant's response text
        """

        system_prompt = """You are the Think Networking Advisor, an AI assistant for Purdue Think members.

Your role:
- Help members with networking advice and strategies
- Provide career guidance
- Recommend connections based on shared interests
- Answer questions about member profiles
- Give specific, actionable advice

Guidelines:
- Be warm, professional, and encouraging
- Keep responses concise (3-5 sentences)
- Give specific examples when possible
- When recommending connections, explain WHY they'd be a good match
- Reference member details when relevant
"""

        # Build conversation
        messages = [system_prompt]

        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                if msg['role'] == 'user':
                    messages.append(f"User: {msg['content']}")
                else:
                    messages.append(f"Assistant: {msg['content']}")

        messages.append(f"User: {user_message}")

        full_prompt = '\n\n'.join(messages) + '\n\nAssistant:'

        try:
            chat_model = get_chat_model()
            response = chat_model.generate_content(full_prompt)
            return response.text.strip()

        except Exception as e:
            print(f"Error generating chat response: {e}")
            return "I apologize, but I'm having trouble responding right now. Please try again in a moment."


# Convenience functions
def parse_resume(resume_text: str) -> Dict:
    """Parse resume text"""
    return GeminiService.parse_resume(resume_text)


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text"""
    return GeminiService.generate_embedding(text)


def generate_profile_embedding(user_profile: Dict, resume_text: str = "") -> List[float]:
    """Generate embedding for user profile"""
    return GeminiService.generate_profile_embedding(user_profile, resume_text)


def generate_networking_email(sender_profile: Dict, recipient_profile: Dict) -> Dict[str, str]:
    """Generate networking email"""
    return GeminiService.generate_networking_email(sender_profile, recipient_profile)


def chat_response(user_message: str, conversation_history: List[Dict] = None, context: Dict = None) -> str:
    """Generate chat response"""
    return GeminiService.chat_response(user_message, conversation_history, context)
