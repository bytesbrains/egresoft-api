from fastapi import APIRouter, Depends, HTTPException, status
from database.client import db_client
from schemas.encuesta import Survey

router = APIRouter(
    prefix="/survey",
    tags=["survey"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}},
)

@router.post("/add", response_model=Survey, status_code=status.HTTP_201_CREATED)
async def create_survey(survey: Survey):
    existing_survey = db_client.surveys.find_one({"title": survey.title})
    if existing_survey:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una encuesta con ese titulo.",
        )

    survey = db_client.surveys.insert_one(survey.dict()).inserted_id
    return survey 

@router.get("/get/{survey_title}", response_model=Survey)
async def get_survey(survey_title: str):
    survey_data = db_client.surveys.find_one({"title": survey_title})
    if not survey_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return Survey(**survey_data)

@router.delete("/delete/{survey_title}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(survey_title: str):
    result = db_client.surveys.delete_one({"title": survey_title})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La Encuesta con titulo {survey_title} no ha sido encontrada",
        )

    return {"message": f"La Encuesta con titulo {survey_title} ha sido eliminada"}