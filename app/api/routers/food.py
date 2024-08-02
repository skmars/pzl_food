# pylint: disable=broad-except
from typing import (
    Dict,
    List,
    Union,
)

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    status,
)

from app.core.database import Database
from app.schemas import (
    DeletedFoodSchema,
    DeleteFoodSchema,
    RequestFoodSchema,
    ResponseFoodCategorySchema,
    ResponseFoodSchema,
    SaveFoodSchema,
)
from app.services import (
    delete_foods,
    get_foods_grouped_by_category,
    save_foods,
)

router = APIRouter(tags=["Food"])


@router.get("/get_food", response_model=ResponseFoodCategorySchema, description="Получить блюдо")
async def get_food(request: Request) -> Union[List[ResponseFoodSchema], HTTPException]:
    db: Database = request.database
    try:
        return ResponseFoodCategorySchema(**await get_foods_grouped_by_category(db, RequestFoodSchema(**request.data)))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error


@router.post("/create_food", response_model=ResponseFoodSchema, description="Создать блюдо")
async def create_food(request: Request) -> Union[List[ResponseFoodSchema], HTTPException]:
    db: Database = request.database
    try:
        return ResponseFoodSchema(**await save_foods(db, SaveFoodSchema(**request.data)))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error


@router.put("/update_food", response_model=ResponseFoodSchema, description="Обновить блюдо")
async def update_food(request: Request) -> Union[List[ResponseFoodSchema], HTTPException]:
    db: Database = request.database
    try:
        return ResponseFoodSchema(**await save_foods(db, SaveFoodSchema(**request.data)))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error


@router.delete("/delete_food", response_model=DeletedFoodSchema, description="Удалить блюдо")
async def delete_food(request: Request) -> Union[Dict[str, str], HTTPException]:
    db: Database = request.database
    try:
        return DeletedFoodSchema(**await delete_foods(db, DeleteFoodSchema(**request.data)))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error
