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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the main project directory
HERE = os.path.dirname(os.path.abspath(__file__))

# Ensure a temp directory exists for processing
os.makedirs(os.path.join(HERE, "temp_uploads"), exist_ok=True)

@app.post("/generate/{doc_type}")
async def generate_document(doc_type: str, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(HERE, "temp_uploads", job_id)
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
            # Pass the uploaded file as an absolute path argument
            cmd = ["python", os.path.join(HERE, script_name), input_path]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
            
            base = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base}_audio.wav"
            
        elif doc_type == "pdf":
            script_name = "make_pdf.py"
            cmd = ["python", os.path.join(HERE, script_name)]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
            output_filename = "orbitly_case_studies.pdf"
            
        elif doc_type == "pptx":
            script_name = "make_pptx.py"
            cmd = ["python", os.path.join(HERE, script_name)]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
            output_filename = "orbitly_sales_deck_meridian.pptx"
            
        elif doc_type == "docx":
            script_name = "make_docx.py"
            cmd = ["python", os.path.join(HERE, script_name)]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
            output_filename = "orbitly_product_specs.docx"
            
        else:
            raise HTTPException(status_code=400, detail="Invalid document type")

        # Check for script errors
        if process.returncode != 0:
            print(f"Error stdout: {process.stdout}")
            print(f"Error stderr: {process.stderr}")
            raise HTTPException(status_code=500, detail=f"Script failed: {process.stderr}")

        # The scripts save files in the main HERE directory
        output_path = os.path.join(HERE, output_filename)
        
        if not os.path.exists(output_path):
            # Fallback: search for the generated file type in the main dir
            for f in os.listdir(HERE):
                if f.endswith(('.wav', '.pdf', '.pptx', '.docx')) and not f.startswith("temp_"):
                    output_path = os.path.join(HERE, f)
                    output_filename = f
                    break

        if not os.path.exists(output_path):
             raise HTTPException(status_code=500, detail="Generated file not found on server.")

        # Send the file back to the user
        return FileResponse(output_path, filename=output_filename)

    except Exception as e:
        # Clean up temp folder if needed, but leave generated files for download
        raise HTTPException(status_code=500, detail=str(e))

# Serve the frontend
app.mount("/", StaticFiles(directory=".", html=True), name="static")