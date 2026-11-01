# AI Resume Analyzer

An AI-powered resume analysis system that extracts candidate information from PDF resumes and evaluates how well a candidate's skills, experience, education, and projects match a given job description.

The system uses structured data validation and AI-based evaluation to generate resume match scores, identify missing requirements, and provide evidence-based insights for improving a resume.

## Features

- **PDF Resume Parsing** – Extract text from PDF resumes.
- **Structured Information Extraction** – Identify candidate details, skills, education, experience, and projects.
- **AI-Based Resume Evaluation** – Analyze resumes against job descriptions.
- **Category-Wise Scoring** – Evaluate skills, experience, projects, and education.
- **Requirement Matching** – Identify matched and missing job requirements.
- **Evidence-Based Analysis** – Provide supporting evidence from the resume.
- **Pydantic Validation** – Ensure structured and consistent AI-generated output.
- **Batch Resume Processing** – Analyze multiple resumes.

## Tech Stack

- Python
- Pydantic
- Large Language Models (LLMs)
- PDF Text Extraction
- JSON
- Pytest

## Project Workflow

```text
Resume PDF + Job Description
            |
            v
     PDF Text Extraction
            |
            v
    Resume Information
       Extraction
            |
            v
   Structured Data Validation
        (Pydantic)
            |
            v
     AI Resume Evaluation
            |
            v
    Match Scores & Insights
            |
            v
 Matched and Missing Requirements
```

## Evaluation Categories

| Category | Description |
|---|---|
| Skills | Match between candidate skills and job requirements |
| Experience | Relevance of professional or practical experience |
| Projects | Alignment of projects with the role |
| Education | Relevance of academic qualifications |
| Overall Match | Combined assessment of resume suitability |

## Example Output

```json
{
  "skills_score": 85.0,
  "experience_score": 78.0,
  "projects_score": 90.0,
  "education_score": 80.0,
  "matched_requirement": [
    "Python",
    "Machine Learning",
    "Data Analysis"
  ],
  "missing_requirement": [
    "Cloud Computing",
    "Kubernetes"
  ],
  "evidence": [
    "Machine learning project listed in resume",
    "Python experience demonstrated through projects"
  ]
}
```

*Example output for demonstration purposes.*

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Adityasinghrajput01/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

If your project uses an LLM API, create a `.env` file:

```env
API_KEY=your_api_key_here
```

Keep API keys private and never commit them to GitHub.

## Usage

1. Provide one or more resume PDFs.
2. Enter the job description or required qualifications.
3. Run the resume analysis script.
4. Review extracted candidate information, match scores, matched requirements, missing skills, and supporting evidence.

Run the main script:

```bash
python main.py
```

*Adjust the command according to your project's entry-point filename.*

## Testing

Run the test suite using:

```bash
pytest
```

## Applications

- Resume-job description matching
- Candidate profile analysis
- Skill gap identification
- Resume improvement recommendations
- Recruitment and career guidance tools

## Future Improvements

- Web-based interface using Streamlit or FastAPI
- ATS compatibility analysis
- Resume ranking and comparison
- Detailed improvement recommendations
- Support for DOCX resumes
- Explainable scoring and evaluation reports

## Disclaimer

This project is intended for educational and research purposes. Resume scores are AI-generated estimates and should not be treated as definitive hiring decisions. Human review is necessary to evaluate candidates fairly.

## Author

**Aditya Kumar Singh**

B.Tech Computer Science and Engineering

GitHub: [Adityasinghrajput01](https://github.com/Adityasinghrajput01)

LinkedIn: [Aditya Kumar Singh](https://www.linkedin.com/in/aditya-kumar-singh-173911321/)

---

If you find this project useful, consider giving the repository a ⭐.
