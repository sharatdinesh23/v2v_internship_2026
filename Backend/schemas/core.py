from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SubmissionStatus(str, Enum):
    PENDING = "Pending"
    GRADED = "Graded"
    LATE = "Late"


class AttendanceStatus(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"


class InternshipCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    is_active: bool = True
    teacher_ids: Optional[List[UUID]] = []


class InternshipUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    teacher_ids: Optional[List[UUID]] = None


class TeacherCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    internship_id: Optional[UUID] = None


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    college_name: Optional[str] = Field(default=None, max_length=255)
    internship_id: Optional[UUID] = None


class TeacherPasswordReset(BaseModel):
    password: str = Field(..., min_length=8)


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    internship_id: Optional[UUID] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ProfileResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role_id: UUID
    internship_id: Optional[UUID] = None
    created_at: datetime


class ProfileUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    internship_id: Optional[UUID] = None


class PasswordUpdate(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class AssignmentCreate(BaseModel):
    internship_id: UUID
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    doc_link: Optional[str] = None
    due_date: datetime


class AssignmentResponse(AssignmentCreate):
    id: UUID
    created_by: UUID
    created_at: datetime


class NoteCreate(BaseModel):
    internship_id: UUID
    title: str = Field(..., min_length=3, max_length=255)
    file_name: str = Field(..., min_length=1, max_length=255)
    markdown_content: str = Field(..., min_length=1)


class NoteResponse(NoteCreate):
    id: UUID
    created_by: UUID
    created_at: datetime


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    markdown_content: Optional[str] = Field(default=None, min_length=1)
    internship_id: Optional[UUID] = None


class SubmissionCreate(BaseModel):
    assignment_id: UUID
    repo_link: str = Field(..., max_length=512)


class SubmissionResponse(SubmissionCreate):
    id: UUID
    student_id: UUID
    status: SubmissionStatus
    grade: Optional[str] = None
    submitted_at: datetime


class GradeUpdate(BaseModel):
    grade: str
    feedback: Optional[str] = None


class AttendanceRecord(BaseModel):
    student_id: UUID
    status: AttendanceStatus


class AttendanceBatch(BaseModel):
    date: str
    records: List[AttendanceRecord]
