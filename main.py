from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

user_data_list: list[dict] = []
tasks_list: list[dict] = []

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
    
@app.get("/login/", response_class=HTMLResponse)
async def get_login_page():
    with open("index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200) 

@app.get("/create_user/", response_class=HTMLResponse)
async def get_register_page():
    with open("register.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200) 

@app.get("/create_task/", response_class=HTMLResponse)
async def get_create_task_page():
    with open("create_task.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200) 
    
    
@app.post("/login/")
async def user_login(user: User):
    for user in user_data_list:
        if user["username"] == user.username:
            if user["password"] == user.password:
                return {"status": "Logged in"}
            else:
                return {"status": "Incorrect password"}
    return {"status": "User not found"}

@app.post("/create_user/")
async def create_user(user: User):
    for user in user_data_list:
        if user["username"] == user.username:
            return {"status": "User already exists"}
    
    user_data_list.append({"username": user.username, "password": user.password})
    df = pd.DataFrame(user_data_list)
    df.to_csv("user_data.csv", index=False)
    return {"status": "User Created"}

@app.post("/create_task/")
async def create_task(task: Task):
    user_found = False
    for user in user_data_list:
        if user["username"] == task.user:
            user_found = True
            break

    if not user_found:
        return {"status": "User not found"}
    
    tasks_list.append({"task": task.task, "deadline": task.deadline, "user": task.user})
    df_tasks = pd.DataFrame(tasks_list)
    df_tasks.to_csv("tasks_data.csv", index=False)   
    return {"status": "task Created"}


@app.get("/get_tasks/", response_class=HTMLResponse)
async def get_tasks(name: str):
    user_tasks = [task for task in tasks_list if task["user"] == name]

    if user_tasks:
        tasks_html = "".join(
            f"<li>Task: {task['task']}, Deadline: {task['deadline']}</li>" for task in user_tasks
        )
    else:
        tasks_html = "<li>No tasks found.</li>"
    
    with open("main.html", "r") as file:
        html_content = file.read().replace("{{ tasks }}", tasks_html)
    
    return HTMLResponse(content=html_content, status_code=200)

try:
    df = pd.read_csv("user_data.csv")
    user_data_list = df.to_dict(orient="records")
except FileNotFoundError:
    pass

try:
    df_tasks = pd.read_csv("tasks_data.csv")
    tasks_list = df_tasks.to_dict(orient="records")
except FileNotFoundError:
    pass