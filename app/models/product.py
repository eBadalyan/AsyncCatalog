from sqlalchemy import Integer, String, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base 

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Numeric, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True) 
    
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False) 

    category = relationship("Category", back_populates="products")