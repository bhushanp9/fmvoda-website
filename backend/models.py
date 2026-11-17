
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from database import Base


class MembershipApplicationDB(Base):
    __tablename__ = "membership_applications"

    id = Column(Integer, primary_key=True, index=True)

    organization_name = Column(String(200), nullable=False)
    contact_person = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=False)

    organization_type = Column(
        String(50), default="MSME"
    )

    city = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    primary_sector = Column(String(150), nullable=False)

    status = Column(String(30), default="received")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

