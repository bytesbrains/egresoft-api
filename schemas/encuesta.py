from typing import List, Optional
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    isRequired: bool
    inputType: Optional[str] = None
    title: str


class Element(BaseModel):
    type: str
    name: str
    title: str
    description: Optional[str] = None
    hideNumber: bool
    isRequired: Optional[bool] = None
    requiredErrorText: Optional[str] = None
    choices: Optional[List[str]] = None
    showOtherItem: Optional[bool] = None
    showNoneItem: Optional[bool] = None
    items: Optional[List[Item]] = None


class Page(BaseModel):
    name: str
    elements: List[Element]
    title: Optional[str] = None
    description: Optional[str] = None


class Survey(BaseModel):
    title: str
    description: Optional[str] = None
    pages: List[Page]
