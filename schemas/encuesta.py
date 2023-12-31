from typing import List, Optional
from pydantic import BaseModel

# The above code defines a set of classes for creating surveys, including items, elements, pages, and
# the survey itself.


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
    noneText: Optional[str] = None
    items: Optional[List[Item]] = None


class Page(BaseModel):
    name: str
    elements: List[Element]
    title: Optional[str] = None
    description: Optional[str] = None


class Survey(BaseModel):
    surveyId: str
    title: str
    description: Optional[str] = None
    pages: List[Page]


"----------------------------------------------------------------------------------------"
class SurveyAnswerModel(BaseModel):
    surveyId: str
    answer: Survey

class UserSurveyResponse(BaseModel):
    surveyId: str
    answer: Optional[dict] = None
    survey: SurveyAnswerModel
    userId: str
    status: str = "pending" or "completed"