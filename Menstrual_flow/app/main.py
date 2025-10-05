from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, data
from app.api import feedback
from app.database import SessionLocal
from app.storage.model import Feedback
from app.api import ml


app = FastAPI(
    title="FemPlus API",
    version="0.1.0",
    description="API for tracking menstrual flow"
)


# Enable CORS for local development and file:// origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],  # include file:// origin as "null"
    allow_origin_regex=".*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(data.router, prefix="/flow", tags=["Flow"])
app.include_router(data.router, prefix="/data", tags=["Data"])  # Add data router for gas sensor endpoints
app.include_router(ml.router)
app.include_router(feedback.router)

@app.get("/")
async def root():
    return {"FemPlus  API is running!"}

@app.on_event("startup")
async def startup_event():
    print("FemPlus API started successfully!")
    # Seed a few feedback rows if table is empty
    try:
        db = SessionLocal()
        count = db.query(Feedback).count()
        if count == 0:
            samples = [
                Feedback(rating=5, comment="Love the clean design and easy tracking!", user_email="anita@example.com", context_type="home"),
                Feedback(rating=4, comment="Analysis cards are helpful. Waiting for more features.", user_email="meera@example.com", context_type="features"),
                Feedback(rating=5, comment="Teleconsult option is great!", user_email="ria@example.com", context_type="labs"),
            ]
            for s in samples:
                db.add(s)
            db.commit()
    except Exception as e:
        print(f"Feedback seed skipped: {e}")
    finally:
        try:
            db.close()
        except Exception:
            pass

