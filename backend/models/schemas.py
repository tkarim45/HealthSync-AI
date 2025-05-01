from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "user"  # Default to regular user


class UserInDB(BaseModel):
    id: str
    username: str
    email: str
    hashed_password: str
    role: str
    created_at: datetime


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str


class Token(BaseModel):
    token: str
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


class HospitalCreate(BaseModel):
    name: str
    address: str
    lat: float
    lng: float


class HospitalAdminAssign(BaseModel):
    user_id: str


class HospitalResponse(BaseModel):
    id: str
    name: str
    address: str
    lat: float
    lng: float


class HospitalAdminCreate(BaseModel):
    hospital_id: str
    username: str


class ChatbotRequest(BaseModel):
    query: str


class DepartmentCreate(BaseModel):
    name: str


class DepartmentResponse(BaseModel):
    id: str
    hospital_id: str
    name: str
    hospital_name: Optional[str]


class DoctorResponse(BaseModel):
    user_id: str
    username: str
    email: str
    department_id: str
    department_name: str
    specialty: str
    title: str
    phone: Optional[str]
    bio: Optional[str]


class AvailabilityCreate(BaseModel):
    user_id: str
    day_of_week: str
    start_time: str
    end_time: str


class AvailabilityResponse(BaseModel):
    id: str
    user_id: str
    day_of_week: str
    start_time: str
    end_time: str


class AppointmentCreate(BaseModel):
    doctor_id: str
    department_id: str
    hospital_id: str
    appointment_date: str
    start_time: str
    end_time: str


class AppointmentResponse(BaseModel):
    id: str
    user_id: str
    username: str
    doctor_id: str
    doctor_username: str
    department_id: str
    department_name: str
    appointment_date: str
    start_time: str
    end_time: str
    status: str
    created_at: str


class DoctorCreate(BaseModel):
    department_id: str
    username: str
    email: str
    password: str
    specialty: str
    title: str
    phone: Optional[str] = None
    bio: Optional[str] = None


class MedicalHistoryResponse(BaseModel):
    id: str
    user_id: str
    conditions: Optional[str]
    allergies: Optional[str]
    notes: Optional[str]
    updated_at: Optional[str]
    updated_by: Optional[str]


class TimeSlotResponse(BaseModel):
    start_time: str
    end_time: str


class AdminResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    hospital_name: Optional[str]


class AdminCreate(BaseModel):
    username: str
    email: str
    password: str
    hospital_id: Optional[str]


class GeneralQueryRequest(BaseModel):
    query: str
