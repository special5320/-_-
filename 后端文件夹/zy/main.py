from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from config import DB_CONFIG

app = FastAPI()

# 允许所有域名跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    name: str
    age: Optional[int] = None
    position: Optional[str] = None
    awards: Optional[str] = None
    account: int

def get_db_connection():
    connection = pymysql.connect(**DB_CONFIG)
    return connection

# 获取所有学生信息
@app.get("/students/", response_model=List[Student])
def read_students():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return students

# 获取单个学生信息
@app.get("/students/{student_account}", response_model=Student)
def read_student(student_account: int):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM students WHERE account = %s", (student_account,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    if student is None:  # 如果未找到学生，返回404错误
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# 添加新学生
@app.post("/students/")
def create_student(student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, position, awards, account) VALUES (%s, %s, %s, %s, %s)",
                   (student.name, student.age, student.position, student.awards, student.account))
    cursor.close()
    conn.close()
    return {"message": "Student added successfully"}

# 更新学生信息
@app.put("/students/{student_account}")
def update_student(student_account: int, student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name = %s, age = %s, position = %s, awards = %s WHERE account = %s",
                   (student.name, student.age, student.position, student.awards, student_account))
    updated = cursor.rowcount
    cursor.close()
    conn.close()
    if updated == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated successfully"}

# 删除学生信息
@app.delete("/students/{student_account}")
def delete_student(student_account: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE account = %s", (student_account,))
    deleted = cursor.rowcount
    cursor.close()
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}

