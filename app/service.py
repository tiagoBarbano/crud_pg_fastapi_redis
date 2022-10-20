from fastapi import APIRouter, Body, HTTPException, status, Depends
from app.schema import UserSchema
from app.repository import get_all_users, get_user_by_id, update_user
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.cache import get_all
from app.model import UserModel


router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def add_user(user: UserSchema = Body(...), db: AsyncSession = Depends(get_db)):
    new_user = UserModel(nome=user.nome, idade=user.idade, email=user.email)
    db.add(new_user)
    await db.commit()
    return new_user
    
@router.get("/cache")
async def get_users():
    users = await get_all()
    return users

@router.get("/", response_model=list[UserSchema])
async def get_users_default():
    users = await get_all_users()
    return users

@router.get("/{id}", response_model=UserSchema)
async def get_user_data(id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, id)
    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuer not found")    

@router.put("/{id}")
async def update_user_data(id: str, req: UserSchema = Body(...), db: AsyncSession = Depends(get_db)):
    updated_user = await update_user(db, id, req)
    
    if updated_user:
        return updated_user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")    

    
@router.delete("/{id}", response_description="user data deleted from the database")
async def delete_user_data(id: str,  db: AsyncSession = Depends(get_db)):
    delete_user = await delete_user(db, id)
    
    if delete_user:
        return delete_user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")    