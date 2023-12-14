from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from database.client import db_client
from schemas.encuesta import Survey, SurveyAnswerModel, UserSurveyModel, UserSurveyResponse

router = APIRouter(
    prefix="/survey",
    tags=["survey"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}},
)

@router.get("/", response_model=list[Survey], status_code=status.HTTP_200_OK)
async def get_surveys():
    surveys = db_client.surveys.find_one()
    if not surveys:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se han encontrado encuestas")
    return db_client.surveys.find()


@router.post("/add", response_model=Survey, status_code=status.HTTP_201_CREATED)
async def create_survey(survey: Survey):
    existing_survey = db_client.surveys.find_one({"surveyId": survey.surveyId})
    if existing_survey:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una encuesta con ese id.",
        )

    survey_id = db_client.surveys.insert_one(survey.dict()).inserted_id
    return survey 

@router.get("/get/{survey_id}", response_model=Survey)
async def get_survey(survey_id: str):
    survey_data = db_client.surveys.find_one({"surveyId": survey_id})
    if not survey_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return Survey(**survey_data)

@router.delete("/delete/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(survey_id: str):
    result = db_client.surveys.delete_one({"surveyId": survey_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La Encuesta con id {survey_id} no ha sido encontrada",
        )

    return {"message": f"La Encuesta con id {survey_id} ha sido eliminada"}

"------------------------------------------------------------------------------------------------------"
@router.post("/start", response_model=UserSurveyResponse, status_code=status.HTTP_201_CREATED)
async def start_survey(survey_id: str, user_id: str):
    # Verificar si el usuario ya ha iniciado esta encuesta
    existing_survey = db_client.user_surveys.find_one({
        "userId": user_id,
        "surveyId": survey_id
    })

    if existing_survey:
        # Si el usuario ya ha iniciado la encuesta, retornar la respuesta existente
        existing_response = existing_survey.get('answer')
        if existing_response:
            return UserSurveyResponse(answer=existing_response, userId=user_id, surveyId=survey_id, status='pending')

    # Obtener la encuesta original desde la colección de encuestas
    survey_data = db_client.surveys.find_one({"surveyId": survey_id})
    if not survey_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")

    # Crear objeto UserSurveyModel con la respuesta de la encuesta original
    user_survey_response = SurveyAnswerModel(surveyId=survey_id, answer=Survey(**survey_data))
    user_survey_dict = {
        "surveyId": survey_id,
        "answer": user_survey_response.dict(),  # Ensure 'answer' field is correctly populated
        "userId": user_id,
        "status": 'pending'
    }

    # Almacenar la respuesta de la encuesta en la colección user_surveys
    db_client.user_surveys.insert_one(user_survey_dict)

    # Return UserSurveyResponse with the populated answer field
    return UserSurveyResponse(**user_survey_dict)

@router.get("/get/status_surveys/{user_id}", response_model=List[UserSurveyResponse])
async def get_user_surveys(user_id: str, status_survey: Optional[str] = None):
    user_surveys = db_client.user_surveys.find({
        "userId": user_id,
        "status": status_survey  
    })

    if not user_surveys:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron encuestas para el usuario con ID {user_id} y estado {status_survey}",
        )

    return [
        UserSurveyResponse(
            surveyId=survey['surveyId'],
            answer=survey['answer'],
            userId=user_id,
            status=survey['status']
        ) for survey in user_surveys
    ]

@router.patch("/update/{user_id}/{survey_id}", response_model=UserSurveyResponse, status_code=status.HTTP_200_OK)
async def update_user_survey(user_id: str, survey_id: str, updated_survey: Survey):
    # Verificar si la encuesta original existe
    original_survey_data = db_client.surveys.find_one({"surveyId": survey_id})
    if not original_survey_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta original no encontrada")

    # Verificar si el usuario ya ha iniciado esta encuesta
    existing_user_survey = db_client.user_surveys.find_one({
        "userId": user_id,
        "surveyId": survey_id
    })

    if not existing_user_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta de usuario no encontrada")

    # Actualizar la encuesta en la colección user_surveys
    db_client.user_surveys.update_one(
        {"userId": user_id, "surveyId": survey_id},
        {"$set": {"answer": updated_survey.dict()}}
    )

    # Construir manualmente la respuesta sin utilizar el modelo UserSurveyResponse
    updated_user_survey_dict = {
        "surveyId": survey_id,
        "answer": {"surveyId": survey_id, "answer": updated_survey.dict()},
        "userId": user_id,
        "status": existing_user_survey['status']
    }

    return updated_user_survey_dict
