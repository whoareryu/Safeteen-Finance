from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from apps.friday_13th.app.ports.input.pamela_signup_use_case import PamelaSignupUseCase

logger = logging.getLogger(__name__)

pamela_signup_router = APIRouter(prefix="/pamela", tags=["pamela"])

