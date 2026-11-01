import os
import json
import re
from pathlib import Path
from typing import List

import pymupdf as fitz
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field, ValidationError


# =====================================================
# 1. CONFIGURATION
# =====================================================

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=API_KEY)
MODEL = "openai/gpt-oss-20b"

# Update this path to your resume folder.
RESUME_FOLDER = Path(
    r"C:\Users\adity\OneDrive\Desktop\padho-ai-engineer\week1\day5\resumes"
)

OUTPUT_FOLDER = RESUME_FOLDER / "results"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# =====================================================
# 2. PYDANTIC MODELS
# =====================================================

class Education(BaseModel):
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""


class Experience(BaseModel):
    company: str = ""
    role: str = ""
    description: str = ""
    start_date: str = ""
    end_date: str = ""


class Project(BaseModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    name: str = ""
    email: str = ""
    phone_number: str = ""
    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)


class MatchResult(BaseModel):
    skills_score: float = 0
    experience_score: float = 0
    projects_score: float = 0
    education_score: float = 0
    overall_score: float = 0
    matched_requirement: List[str] = Field(default_factory=list)
    missing_requirement: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    recommendation: str = "Moderate Match"


class ResumeEvaluation(BaseModel):
    resume: ResumeData
    evaluation: MatchResult


# =====================================================
# 3. JOB DESCRIPTION
# =====================================================

job_description = """
We are hiring a Python Developer.

Required skills:
- Python
- FastAPI
- SQL
- REST APIs
- Git

Preferred:
- Machine Learning
- Docker
- Relevant projects
"""


# =====================================================
# 4. PROMPTS
# =====================================================

schema = ResumeEvaluation.model_json_schema()

system_prompt = f"""
You are a resume information extraction and job matching assistant.

Extract resume information and evaluate it against the job description.
Return one JSON object matching this schema exactly:

{json.dumps(schema, indent=2)}

Rules:
1. Use only information explicitly present in the resume.
2. Never invent skills, experience, education, or projects.
3. Use empty strings/lists when information is missing.
4. education, experience, and projects must be arrays of structured objects.
5. Include BOTH top-level keys: "resume" and "evaluation".
6. Evaluate required and preferred skills against the job description.
7. Include evidence for important evaluation claims.
8. All scores must be numbers from 0 to 100.
9. Do not use name, email, phone, gender, age, or other personal
   characteristics to determine suitability.
10. Do not automatically reject candidates.
11. recommendation must be exactly one of:
    "Strong Match", "Moderate Match", "Weak Match".

Scoring weights:
- Skills: 40%
- Experience: 25%
- Projects: 25%
- Education: 10%

overall_score = skills_score*0.40 + experience_score*0.25
              + projects_score*0.25 + education_score*0.10

Return only valid JSON. Do not use Markdown fences.
"""


# =====================================================
# 5. PDF TEXT EXTRACTION
# =====================================================

def extract_pdf_text(pdf_path: Path) -> str:
    pages_text = []

    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            pages_text.append(page.get_text())

    return "\n".join(pages_text).strip()


# =====================================================
# 6. GROQ JSON CALL
# =====================================================

def call_groq_json(messages: list) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0
    )

    answer = response.choices[0].message.content
    if not answer:
        raise ValueError("Groq returned an empty response")

    # Remove accidental Markdown fences if present.
    answer = answer.strip()
    answer = re.sub(r"^```(?:json)?\s*", "", answer)
    answer = re.sub(r"\s*```$", "", answer)

    try:
        return json.loads(answer)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Groq returned invalid JSON: {exc}\nResponse:\n{answer}")


# =====================================================
# 7. RESUME EVALUATION
# =====================================================

def evaluate_resume(resume_text: str) -> ResumeEvaluation:
    user_prompt = f"""
JOB DESCRIPTION:
{job_description}

RESUME CONTENT:
<<<RESUME
{resume_text}
RESUME>>>

Extract the resume and evaluate the candidate for this job.
The response MUST include both "resume" and "evaluation".
Return only the JSON object matching the schema.
"""

    raw_data = call_groq_json([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    # Some model responses may omit the required evaluation object.
    # If so, make a second call asking it to complete the missing field.
    if not isinstance(raw_data, dict):
        raise ValueError("Groq response must be a JSON object")

    if "resume" not in raw_data:
        # Sometimes the model returns the resume object directly.
        expected_resume_fields = set(ResumeData.model_fields.keys())
        if expected_resume_fields.intersection(raw_data.keys()):
            raw_data = {"resume": raw_data}

    if "evaluation" not in raw_data:
        repair_prompt = f"""
The previous response omitted the required top-level "evaluation" object.

JOB DESCRIPTION:
{job_description}

EXTRACTED RESUME JSON:
{json.dumps(raw_data.get("resume", {}), ensure_ascii=False)}

Return a COMPLETE JSON object with exactly these top-level keys:
- "resume": preserve the extracted resume data without inventing facts
- "evaluation": score skills, experience, projects, and education against
  the job description; include overall_score, matched_requirement,
  missing_requirement, evidence, and recommendation.

Use scores 0-100 and the scoring weights in the system instructions.
Return only valid JSON.
"""
        repaired = call_groq_json([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": repair_prompt}
        ])

        # Preserve the original extracted resume if repair omitted it.
        if isinstance(repaired, dict):
            if "resume" not in repaired and "resume" in raw_data:
                repaired["resume"] = raw_data["resume"]
            raw_data = repaired

    # Final validation. This will raise a useful Pydantic error if malformed.
    return ResumeEvaluation.model_validate(raw_data)


# =====================================================
# 8. SAVE RESULT TO JSON
# =====================================================

def save_result(filename: str, result: ResumeEvaluation) -> Path:
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", Path(filename).stem)
    output_path = OUTPUT_FOLDER / f"{safe_name}_result.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            result.model_dump(),
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"\nResult saved to: {output_path}")
    return output_path


# =====================================================
# 9. DISPLAY RESULT
# =====================================================

def display_result(result: ResumeEvaluation) -> None:
    resume = result.resume
    evaluation = result.evaluation

    print("\n--- CANDIDATE INFORMATION ---")
    print("Name:", resume.name)
    print("Email:", resume.email)
    print("Phone:", resume.phone_number)

    print("\nSkills:")
    for skill in resume.skills:
        print("-", skill)

    print("\nEducation:")
    for edu in resume.education:
        print(
            f"- {edu.degree} in {edu.field_of_study}"
            f" | {edu.institution}"
            f" | {edu.start_date} - {edu.end_date}"
        )

    print("\nExperience:")
    for exp in resume.experience:
        print(f"- {exp.role} at {exp.company} | {exp.start_date} - {exp.end_date}")
        print("  ", exp.description)

    print("\nProjects:")
    for project in resume.projects:
        print("-", project.name)
        print("  Description:", project.description)
        print("  Technologies:", ", ".join(project.technologies))

    print("\n--- JOB MATCH EVALUATION ---")
    print("Skills Score:", evaluation.skills_score)
    print("Experience Score:", evaluation.experience_score)
    print("Projects Score:", evaluation.projects_score)
    print("Education Score:", evaluation.education_score)
    print("Overall Score:", evaluation.overall_score)

    print("\nMatched Requirements:")
    for item in evaluation.matched_requirement:
        print("-", item)

    print("\nMissing Requirements:")
    for item in evaluation.missing_requirement:
        print("-", item)

    print("\nEvidence:")
    for item in evaluation.evidence:
        print("-", item)

    print("\nRecommendation:", evaluation.recommendation)


# =====================================================
# 10. PROCESS ALL RESUMES
# =====================================================

def main() -> None:
    if not RESUME_FOLDER.exists():
        raise FileNotFoundError(f"Resume folder not found: {RESUME_FOLDER}")

    pdf_files = [
        file for file in RESUME_FOLDER.iterdir()
        if file.is_file()
        and file.suffix.lower() == ".pdf"
        and file.parent != OUTPUT_FOLDER
    ]

    if not pdf_files:
        print("No PDF resumes found.")
        return

    print(f"Found {len(pdf_files)} resumes.")

    for index, pdf_path in enumerate(pdf_files, start=1):
        print("\n" + "=" * 70)
        print(f"Resume {index}/{len(pdf_files)}")
        print(f"Processing: {pdf_path.name}")
        print("=" * 70)

        try:
            resume_text = extract_pdf_text(pdf_path)

            if not resume_text:
                print("No text extracted. This PDF may be scanned and require OCR.")
                continue

            result = evaluate_resume(resume_text)
            display_result(result)
            save_result(pdf_path.name, result)

        except ValidationError as error:
            print("\nPydantic validation error:")
            print(error)

        except Exception as error:
            print("\nError processing resume:")
            print(error)

    print("\n" + "=" * 70)
    print("RESUME PROCESSING COMPLETED")
    print(f"Results folder: {OUTPUT_FOLDER}")
    print("=" * 70)


if __name__ == "__main__":
    main()
