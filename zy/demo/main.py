from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
from typing import List, Optional
from config import DB_CONFIG

app = FastAPI()

class Student(BaseModel):
    name: str
    age: Optional[int] = None
    position: Optional[str] = None
    awards: Optional[str] = None

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

# 添加新学生
@app.post("/students/")
def create_student(student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, position, awards) VALUES (%s, %s, %s, %s)",
                   (student.name, student.age, student.position, student.awards))
    cursor.close()
    conn.close()
    return {"message": "Student added successfully"}

# 更新学生信息
@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name = %s, age = %s, position = %s, awards = %s WHERE id = %s",
                   (student.name, student.age, student.position, student.awards, student_id))
    updated = cursor.rowcount
    cursor.close()
    conn.close()
    if updated == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated successfully"}

# 删除学生信息
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    deleted = cursor.rowcount
    cursor.close()
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}

