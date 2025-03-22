from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from pydantic import BaseModel

app = FastAPI()

tasks_csv = Path("data/tasks.csv")
users_csv = Path("data/users.csv")

if Path(tasks_csv).exists():
    df = pd.DataFrame(columns=['task', 'deadline', 'user'])
    df.to_csv(tasks_csv, index=False)

if Path(users_csv).exists():
    df = pd.DataFrame(columns=['username', 'password'])
    df.to_csv(users_csv, index=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # This allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # This allows all headers
)
class User(BaseModel):
    username: str
    password: str 

class Task(BaseModel):
    task: str
    deadline: str 
    user: str

@app.post("/login/")
async def user_login(User: User):
    df = pd.read_csv(users_csv)

    username = User.username in df['username']
    password = User.password in df['password']

    if username and not password:
        return {"status": "Failed"}
    
    return {"status": "Logged in"}

@app.post("/create_user/")
async def create_user(User: User):
    df = pd.read_csv(users_csv)

    if User.username in df['username'].values:
        return {"status": "User already exists"}
    
    df.loc[len(df)] = User.dict()
    df.to_csv(users_csv, index=False)
    return {"status": "User Created"}

@app.post("/create_task/")
async def create_task(Task: Task):
    df = pd.read_csv(tasks_csv)

    df.loc[len(df)] = Task.dict()

    df.to_csv(tasks_csv, index=False)
    return {"status": "Task Created"}

@app.get("/get_tasks/")
async def get_tasks(name: str):
    df = pd.read_csv(tasks_csv)

    user_tasks = df[df["user"] == name]

    return {"tasks": user_tasks.to_dict(orient="records")}
