from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from sqlalchemy.orm import relationship
from app.models.role import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, nullable=False)
    role: Mapped[Role] = relationship(back_populates="users")
    
    categories = relationship("Category", back_populates="owner")
    cart_items = relationship("CartItem", back_populates="user")
