import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.models.base import Base


class Role(Base):
    __tablename__ = 'roles'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False, unique=True)
    
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"
