from sqlalchemy.orm import Session
from . import models

def get_user(db: Session, tg_id: int):
    return db.query(models.User).filter(models.User.tg_id == tg_id).first()

def create_order(db: Session, user_id: int, title: str, description: str, price: int, deadline: str):
    db_order = models.Order(
        customer_id=user_id,
        title=title,
        description=description,
        price=price,
        deadline=deadline
    )
    db.add(db_order)
    db.commit()
    return db_order
