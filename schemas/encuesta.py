from typing import List, Optional
from pydantic import BaseModel

class Choice(BaseModel):
    value: str
    text: str

class Item(BaseModel):
    name: str
    title: str

class Element(BaseModel):
    type: str
    name: str
    title: str
    isRequired: bool
    choices: Optional[List[Choice]] = None
    showOtherItem: Optional[bool] = None
    showNoneItem: Optional[bool] = None
    items: Optional[List[Item]] = None

class Page(BaseModel):
    name: str
    elements: List[Element]
    title: str
    description: Optional[str] = None

class Survey(BaseModel):
    title: str
    description: Optional[str] = None
    pages: List[Page]