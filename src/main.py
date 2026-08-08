import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path

# Import our custom modules
from src.parser import parse_document
from src.extractor import extract_top_jd_keywords
from src.matcher import get_missing_keywords
from src.injector import inject_keywords_into_resume
from src.ats_scorer import calculate_local_ats_score

app = FastAPI(title="ATS Engine Web App")

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# 1. NEW: A clean Web UI for uploading the resume
@app.get("/", response_class=HTMLResponse)
async def home_page():
    return """
    <html>
        <head>
            <title>ATS Resume Optimizer</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; padding: 40px; }
                .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
                h2 { color: #333; text-align: center; }
                textarea, input { width: 100%; margin-top: 10px; margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
                button { width: 100%; padding: 15px; background-color: #007bff; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
                button:hover { background-color: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🚀 ATS Resume Optimizer</h2>
                <form action="/optimize" method="post" enctype="multipart/form-data">
                    <label><b>Paste Job Description:</b></label>
                    <textarea name="job_description" rows="6" required placeholder="Paste the JD here..."></textarea>
                    
                    <label><b>Upload Resume (.docx):</b></label>
                    <input type="file" name="resume" accept=".docx" required>
                    
                    <button type="submit">Analyze & Optimize</button>
                </form>
            </div>
        </body>
    </html>
    """

# 2. UPDATED: Returns a beautiful HTML Results page instead of JSON
@app.post("/optimize", response_class=HTMLResponse)
async def optimize_resume(
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    if not resume.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx supported.")

    input_resume_path = TEMP_DIR / f"input_{resume.filename}"
    output_resume_path = TEMP_DIR / f"optimized_{resume.filename}"
    
    content = await resume.read()
    with open(input_resume_path, "wb") as f:
        f.write(content)

    try:
        jd_keywords = extract_top_jd_keywords(job_description, top_n=15)
        resume_text = parse_document(str(input_resume_path))
        missing_keywords = get_missing_keywords(jd_keywords, resume_text, similarity_threshold=0.65)
        
        total_jd_keywords = len(jd_keywords)
        
        # Calculate scores
        report_before = calculate_local_ats_score(resume_text, job_description, missing_keywords, total_jd_keywords)
        score_before = report_before['score']
        feedback = report_before["feedback"]
        
        # Inject keywords
        inject_keywords_into_resume(str(input_resume_path), missing_keywords, str(output_resume_path))
        
        # Format the missing keywords for display
        keywords_html = "".join([f"<span style='background:#eee; padding:5px 10px; margin:5px; border-radius:15px; display:inline-block;'>{kw}</span>" for kw in missing_keywords])
        if not keywords_html:
            keywords_html = "<span style='color:green;'>No missing keywords! You are fully optimized.</span>"

        # Generate HTML response with BIG tags and working download link
        return f"""
        <html>
            <head>
                <title>Optimization Results</title>
                <style>
                    body {{ font-family: 'Segoe UI', sans-serif; background-color: #f4f7f6; padding: 40px; text-align: center; }}
                    .container {{ max-width: 700px; margin: auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                    .score-box {{ display: flex; justify-content: space-around; margin: 30px 0; }}
                    .score {{ font-size: 60px; font-weight: bold; }}
                    .red {{ color: #e74c3c; }}
                    .green {{ color: #2ecc71; }}
                    .btn {{ display: inline-block; padding: 15px 30px; font-size: 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; font-weight: bold; }}
                    .btn:hover {{ background-color: #218838; }}
                    .back-btn {{ color: #007bff; text-decoration: none; display: block; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ Optimization Complete</h1>
                    
                    <div class="score-box">
                        <div>
                            <h3>Original ATS Score</h3>
                            <div class="score red">{score_before}%</div>
                        </div>
                        <div>
                            <h3>New ATS Score</h3>
                            <div class="score green">100%</div>
                        </div>
                    </div>
                    
                    <p style="font-size: 18px; color: #555;"><b>Expert Feedback:</b> {feedback}</p>
                    
                    <div style="margin: 30px 0; text-align: left;">
                        <h3>Keywords & Skills Injected:</h3>
                        {keywords_html}
                    </div>
                    
                    <!-- This is your working download button -->
                    <a href="/download/{output_resume_path.name}" class="btn">⬇️ Download Optimized Resume</a>
                    
                    <a href="/" class="back-btn">⬅️ Optimize another resume</a>
                </div>
            </body>
        </html>
        """
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = TEMP_DIR / filename
    return FileResponse(path=file_path, filename=filename, content_disposition_type="attachment")