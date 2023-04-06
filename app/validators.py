from pydantic import BaseModel, validator
from typing import Optional
import re


def _check_email_format(email):
    pattern = r'(\w+)@(\w+)\.(\w+)'
    result = re.search(pattern, email, re.IGNORECASE)
    return result


def _check_text_len(text, min_len, max_len, description):
    len_text = len(text)
    if len_text > max_len or len_text < min_len:
        raise ValueError(f'Incorrect length of {description}')


def is_acceptable_password(password, min_len, max_len):
    return 'password' not in password.lower()\
           and max_len >= len(password) >= min_len \
           and any(map(lambda x: x.isdigit(), password)) \
           and not password.isdigit()


class AbcUser(BaseModel):
    name: str
    password: str

    @validator('name')
    def validate_name(cls, value):
        if not value.isalpha():
            raise ValueError('Name should contain only letters')
        return value

    @validator('password')
    def validate_password(cls, value):
        if not is_acceptable_password(value, 8, 99):
            raise ValueError('Too easy password')
        return value


class PostUser(AbcUser, BaseModel):
    email: str

    @validator('email')
    def validate_email(cls, value):
        if ' ' in value:
            raise ValueError('Email should not contain spacebars')
        _check_text_len(value, 10, 50, 'email')
        email_ = _check_email_format(value)
        if not email_:
            raise ValueError('Incorrect email format')
        return value


class PatchUser(AbcUser, BaseModel):
    name: Optional[str]
    password: Optional[str]


class AbcAdv(BaseModel):
    title: str
    description: str

    @validator('title')
    def validate_title(cls, value):
        _check_text_len(value, 5, 70, 'title')
        return value

    @validator('description')
    def validate_description(cls, value):
        _check_text_len(value, 10, 500, 'description')
        return value


class PostAdv(AbcAdv, BaseModel):
    pass


class PatchAdv(AbcAdv, BaseModel):
    title: Optional[str]
    description: Optional[str]
