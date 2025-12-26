# test_minimal.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TestModel(BaseModel):
    name: str
    email: str  # ← Usar str en vez de EmailStr

@app.get("/")
async def root():
    return {"message": "Working"}

@app.post("/test")
async def test(data: TestModel):
    return {"received": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)