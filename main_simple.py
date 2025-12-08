from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS amplio temporalmente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "✅ FastAPI is RUNNING!"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "ecommerce-api"}

@app.get("/api/v1/products")
def get_products():
    return {"products": ["Product 1", "Product 2"], "test": True}