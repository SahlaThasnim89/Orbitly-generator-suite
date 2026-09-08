import os
import shutil
import uuid
import subprocess
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Orbitly Generator API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure a temp directory exists for processing
os.makedirs("temp_uploads", exist_ok=True)

@app.post("/generate/{doc_type}")
async def generate_document(doc_type: str, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    job_dir = f"temp_uploads/{job_id}"
    os.makedirs(job_dir, exist_ok=True)
    
    # Save uploaded file
    input_path = os.path.join(job_dir, file.filename)
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    script_name = ""
    output_filename = ""
    
    try:
        if doc_type == "audio":
            script_name = "make_audio.py"
            # Pass the uploaded file as an argument to your script
            cmd = ["python", script_name, input_path]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=job_dir)
            
            # Your audio script outputs f"{base}_audio.wav"
            base = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base}_audio.wav"
            
        elif doc_type == "pdf":
            script_name = "make_pdf.py"
            cmd = ["python", script_name]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=job_dir)
            output_filename = "orbitly_case_studies.pdf"
            
        elif doc_type == "pptx":
            script_name = "make_pptx.py"
            cmd = ["python", script_name]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=job_dir)
            output_filename = "orbitly_sales_deck_meridian.pptx"
            
        elif doc_type == "docx":
            script_name = "make_docx.py"
            cmd = ["python", script_name]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=job_dir)
            output_filename = "orbitly_product_specs.docx"
            
        else:
            raise HTTPException(status_code=400, detail="Invalid document type")

        # Check for script errors
        if process.returncode != 0:
            print(f"Error: {process.stderr}")
            raise HTTPException(status_code=500, detail=f"Script failed: {process.stderr}")

        output_path = os.path.join(job_dir, output_filename)
        
        if not os.path.exists(output_path):
            # Fallback: search for the generated file type in the dir
            for f in os.listdir(job_dir):
                if f.endswith(('.wav', '.pdf', '.pptx', '.docx')):
                    output_path = os.path.join(job_dir, f)
                    output_filename = f
                    break

        return FileResponse(output_path, filename=output_filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve the frontend (optional, you can also just open index.html locally)
app.mount("/", StaticFiles(directory=".", html=True), name="static")