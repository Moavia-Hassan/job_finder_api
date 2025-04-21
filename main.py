import uvicorn

if __name__ == "__main__":
    print("Starting Job Finder API server...")
    uvicorn.run("app.integrated_api:app", host="127.0.0.1", port=8000, reload=True)