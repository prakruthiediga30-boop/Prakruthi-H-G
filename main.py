from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3

app = FastAPI(title="EWB Students CRUD")

# Database setup
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            course TEXT,
            address TEXT,
            enrollment_date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Model
class Student(BaseModel):
    name: str
    dob: str
    email: str
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[str] = None

# 1. CREATE - POST /students
@app.post("/students")
def create_student(student: Student):
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO students (name,dob,email,phone,course,address,enrollment_date) VALUES (?,?,?,?,?,?,?)",
            (student.name, student.dob, student.email, student.phone, student.course, student.address, student.enrollment_date)
        )
        conn.commit()
        return {"id": cur.lastrowid, **student.dict(), "message": "Student created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# 2. READ ALL - GET /students
@app.get("/students")
def list_students(course: Optional[str] = None):
    conn = get_db()
    if course:
        rows = conn.execute("SELECT * FROM students WHERE course=?", (course,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# 3. READ ONE - GET /students/{id}
@app.get("/students/{student_id}")
def get_student(student_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")
    return dict(row)

# 4. UPDATE - PUT /students/{id}
@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    conn = get_db()
    cur = conn.execute(
        "UPDATE students SET name=?, dob=?, email=?, phone=?, course=?, address=?, enrollment_date=? WHERE id=?",
        (student.name, student.dob, student.email, student.phone, student.course, student.address, student.enrollment_date, student_id)
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated successfully"}

# 5. DELETE - DELETE /students/{id}
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db()
    cur = conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}

@app.get("/")
def home():
    return {"message": "EWB Student CRUD API is running"}