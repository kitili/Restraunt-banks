from fastapi import FastAPI

app = FastAPI(title="Food Surplus Matcher")

@app.get("/health")
def health():
	return {"status": "ok"}
