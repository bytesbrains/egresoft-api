from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status
from database.client import db_client
from schemas.encuesta import Survey, SurveyAnswerModel, UserSurveyResponse

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
    existing_survey = db_client.user_surveys.find_one({
        "userId": user_id,
        "surveyId": survey_id
    })

    if existing_survey:
        existing_response = existing_survey.get('survey')
        if existing_response:
            return UserSurveyResponse(
                surveyId=survey_id,
                answer=existing_survey.get('answer'),  # Añadido para incluir el campo answer
                survey=existing_response,
                userId=user_id,
                status='pending'
            )

    survey_data = db_client.surveys.find_one({"surveyId": survey_id})
    if not survey_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")

    user_survey_response = SurveyAnswerModel(surveyId=survey_id, answer=Survey(**survey_data))
    user_survey_dict = {
        "surveyId": survey_id,
        "answer": None,  # Añadido para inicializar el campo answer como None
        "survey": user_survey_response.dict(),
        "userId": user_id,
        "status": 'pending'
    }

    db_client.user_surveys.insert_one(user_survey_dict)
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
    
    return [UserSurveyResponse(**survey) for survey in user_surveys]

@router.patch("/update/{survey_id}/{user_id}", response_model=UserSurveyResponse)
async def update_survey_answer(
    survey_id: str,
    user_id: str,
    updated_answer: dict = Body(..., embed=True)
):
    existing_survey = db_client.user_surveys.find_one({
        "userId": user_id,
        "surveyId": survey_id
    })

    if not existing_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la encuesta para el usuario con ID {user_id} y survey ID {survey_id}",
        )

    # Obtén la respuesta existente o crea una nueva si no existe
    existing_answer = existing_survey.get('answer', {})
    
    if existing_answer is None:
        existing_answer = {}

    existing_answer.update(updated_answer)

    result = db_client.user_surveys.update_one(
        {"userId": user_id, "surveyId": survey_id},
        {"$set": {"answer": existing_answer}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo actualizar la respuesta para la encuesta con ID {survey_id} y usuario {user_id}",
        )

    # Recupera el documento de la encuesta actualizado después de la actualización
    updated_survey_document = db_client.user_surveys.find_one({
        "userId": user_id,
        "surveyId": survey_id
    })

    return UserSurveyResponse(
        surveyId=survey_id,
        answer=updated_survey_document.get('answer'),
        survey=existing_survey.get('survey'),
        userId=user_id,
        status=existing_survey.get('status')
    )
