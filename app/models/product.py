from sqlalchemy import ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False) # <-- ДОБАВЛЕНО!


    category = relationship("Category", back_populates="products")
