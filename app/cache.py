import time
from fastapi import HTTPException, status, APIRouter
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, JsonModel, Field, Migrator
from sqlalchemy.future import select
from app.database import async_session
from app.model import UserModel
from app.config import Settings

settings = Settings()

router = APIRouter()

redis = get_redis_connection(host=settings.redis_host, 
                             port=settings.redis_port, 
                             password=settings.redis_password, 
                             decode_responses=True)

class Order(JsonModel):
    id: int = Field(index=True)    
    nome: str = Field(index=True)
    idade: int = Field(index=True)
    email: str = Field(index=True)

    class Meta:
        database = redis

async def init_cache_user():
    # Busca os dados do banco SQL
    async with async_session() as db:
        query = select(UserModel)
        users = await db.execute(query)
        users_sql = users.scalars().all()

    # Consulta o cache atual
    orders = await get_all()
    
    # Deleta o Cache atual
    for order in orders:
        await delete_by_pk(order.pk)                    
        
    # Insere novo Cache        
    for user_sql in users_sql:
        new_order = Order(id=user_sql.id,
                      nome=user_sql.nome,
                      idade=user_sql.idade,
                      email=user_sql.email)
        new_order.save()
    

#@router.get('/orders/quantity/{quantity}')
async def get_by_quantity(quantity: str):
  orders = await Order.find((Order.quantity == quantity)).all()
  return orders


#@router.get('/orders/status/{status}')
async def get_by_status(status: str):
  orders = Order.find((Order.status == status)).all()
  return orders


#@router.get('/orders/{pk}')
async def get_by_pk(pk: str):
    try: 
        order = Order.get(pk)
        return order
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    

@router.get('/orders')
async def get_all():
    return Order.find().all()

#@router.delete('/orders/{pk}')
async def delete_by_pk(pk: str):
    return Order.delete(pk)

#@router.post('/orders')
async def create(order: Order, background_tasks: BackgroundTasks):  # id, quantity
    order.save()
    #background_tasks.add_task(order_completed, order)
    return order

def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')
    
Migrator().run()