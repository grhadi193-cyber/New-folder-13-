from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional
import re


def normalize_phone(value: str) -> str:
    """Normalize phone number to 09XXXXXXXXX format."""
    # Strip whitespace, dashes, parentheses, dots
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', value.strip())

    # Handle +98 prefix (Iran country code)
    if cleaned.startswith('+98'):
        cleaned = '0' + cleaned[3:]
    elif cleaned.startswith('98') and len(cleaned) == 12:
        cleaned = '0' + cleaned[2:]

    # If starts with 9 (missing leading 0), prepend it
    if cleaned.startswith('9') and len(cleaned) == 10:
        cleaned = '0' + cleaned

    return cleaned


class SendOTPIn(BaseModel):
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = normalize_phone(v)
        if not re.match(r"^09[0-9]{9}$", v):
            raise ValueError("شماره موبایل معتبر نیست (مثال: 09123456789)")
        return v


class VerifyOTPIn(BaseModel):
    phone_number: str
    code: str
    password: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def normalize(cls, v: str) -> str:
        return normalize_phone(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 6:
            raise ValueError("رمز عبور باید حداقل ۶ کاراکتر باشد")
        return v


class LoginIn(BaseModel):
    phone_number: str
    password: str

    @field_validator("phone_number")
    @classmethod
    def normalize(cls, v: str) -> str:
        return normalize_phone(v)


class ForgotPasswordIn(BaseModel):
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def normalize(cls, v: str) -> str:
        return normalize_phone(v)


class ResetPasswordIn(BaseModel):
    phone_number: str
    code: str
    new_password: str

    @field_validator("phone_number")
    @classmethod
    def normalize(cls, v: str) -> str:
        return normalize_phone(v)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("رمز عبور جدید باید حداقل ۶ کاراکتر باشد")
        return v


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("رمز عبور جدید باید حداقل ۶ کاراکتر باشد")
        return v


class TokenOut(BaseModel):
    access: str
    refresh: str


class AddressIn(BaseModel):
    title:       str  = ""
    province:    str
    city:        str
    street:      str
    postal_code: str
    is_default:  bool = False


class AddressOut(BaseModel):
    id:          int
    title:       str
    province:    str
    city:        str
    street:      str
    postal_code: str
    is_default:  bool

    model_config = {"from_attributes": True}


class ProfileOut(BaseModel):
    id:          int
    phone_number: str
    full_name:   str
    email:       Optional[str] = None
    national_id: Optional[str] = None
    date_joined: datetime

    model_config = {"from_attributes": True}


class UpdateProfileIn(BaseModel):
    full_name:   Optional[str] = None
    email:       Optional[str] = None
    national_id: Optional[str] = None
