"""ResumeAgent — Extracts structured data from resume text or PDF.

LangGraph node that:
1. Reads resume_content from state (plain text or .pdf file path).
2. If PDF: extracts text via PyPDF.
3. Sends text to DeepSeek for structured extraction.
4. Stores structured result in resume_data for downstream agents.

Output schema stored in resume_data:
{
  "projects": [{"name": str, "tech_stack": [str], "highlights": [str]}],
  "skills": [str],
  "experience": [{"title": str, "company": str, "years": int, "description": str}]
}
"""

import json
import os
from typing import Dict, Any, Optional

from services.deepseek_service import DeepSeekClient
from agents.state import InterviewState


SYSTEM_PROMPT = """You are a resume parsing specialist. Extract structured information from the candidate's resume text.

Return ONLY valid JSON — no markdown, no explanation, no code fences.

Schema:
{
  "projects": [
    {
      "name": "<project name>",
      "tech_stack": ["<technology>", ...],
      "highlights": ["<key achievement or responsibility>", ...]
    }
  ],
  "skills": ["<skill>", ...],
  "experience": [
    {
      "title": "<job title>",
      "company": "<company name>",
      "years": <number of years>,
      "description": "<brief description of role and responsibilities>"
    }
  ]
}

Extraction rules:
- projects: extract 2-5 most relevant projects. Include name, technologies used, and 1-3 highlights each.
- skills: extract ALL technical skills mentioned (programming languages, frameworks, tools, platforms).
- experience: extract all work experiences. If years is unclear, estimate from the date range.
- If a section is missing from the resume, use an empty array [].
- Do NOT invent or hallucinate information not present in the text."""

_client = DeepSeekClient(system_prompt=SYSTEM_PROMPT)


def _extract_text_from_pdf(path: str) -> Optional[str]:
    """Extract text content from a PDF file path.

    Args:
        path: Absolute or relative path to a .pdf file.

    Returns:
        Extracted text as a single string, or None on failure.
    """
    try:
        from pypdf import PdfReader

        reader = PdfReader(path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages) if pages else None
    except FileNotFoundError:
        return None
    except Exception:
        return None


def _is_pdf_path(text: str) -> bool:
    """Check if the resume_content looks like a PDF file path."""
    text = text.strip()
    if not text.lower().endswith(".pdf"):
        return False
    # Must exist as a file
    return os.path.isfile(text)


async def resume_agent(state: InterviewState) -> Dict[str, Any]:
    """Extract structured resume data from text or PDF.

    Node: resume_agent
    Reads: resume_content
    Writes: resume_content (plain text if PDF was extracted),
            resume_data (structured JSON)

    Behaviour:
    - If resume_content is a path to a .pdf file:
        1. Extract text via PyPDF
        2. Update resume_content with plain text
        3. Parse with DeepSeek → structured JSON
    - If resume_content is plain text:
        1. Parse directly with DeepSeek → structured JSON
    - If resume_content is empty:
        1. Set resume_data to None (no-op)
    """
    resume_content = state.get("resume_content", "").strip()
    position = state.get("position", "")

    if not resume_content:
        return {
            "resume_content": "",
            "resume_data": None,
        }

    plain_text = resume_content

    # If it's a PDF path, extract text
    if _is_pdf_path(resume_content):
        extracted = _extract_text_from_pdf(resume_content)
        if extracted:
            plain_text = extracted
        # If extraction failed, keep original path as fallback

    # Send to DeepSeek for structured extraction
    prompt = (
        f"Target position: {position}\n\n"
        f"Resume text:\n{plain_text[:6000]}"
    )

    try:
        response = await _client.generate_response(
            [{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2048,
        )

        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        resume_data = json.loads(cleaned)
    except (json.JSONDecodeError, Exception) as e:
        resume_data = {
            "projects": [],
            "skills": [],
            "experience": [],
            "_parse_error": str(e),
        }

    return {
        "resume_content": plain_text,
        "resume_data": resume_data,
    }
