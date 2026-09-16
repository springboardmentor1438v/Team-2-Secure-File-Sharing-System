from fastapi import FastAPI

app = FastAPI(title="Secure File Sharing System")

@app.get("/")
def read_root():
    return {"message": "Secure file sharing system is running"}
