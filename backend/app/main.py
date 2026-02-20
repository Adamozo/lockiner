from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import transactions, receipts, categories, analytics, import_csv, settings, auth, households, invitations, food, fitness, admin, notifications, journal, medicine, backup, todo
from .services.scheduler import start_scheduler, stop_scheduler

# ---------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="LockIner API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(households.router)
app.include_router(invitations.router)
app.include_router(transactions.router)
app.include_router(receipts.router)
app.include_router(categories.router)
app.include_router(analytics.router)
app.include_router(import_csv.router)
app.include_router(settings.router)
app.include_router(food.router)
app.include_router(fitness.router)
app.include_router(admin.router)
app.include_router(notifications.router)
app.include_router(journal.router)
app.include_router(medicine.router)
app.include_router(backup.router)
app.include_router(todo.router)


# ---------------------------------------

@app.get("/")
async def root():
    return {
        "message": "LockIner API",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ---------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
