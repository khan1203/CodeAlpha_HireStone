from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
<<<<<<< HEAD
    filepath: Mapped[str] = mapped_column(String(512), nullable=False)
=======
<<<<<<< HEAD
    filepath: Mapped[str] = mapped_column(String(512), nullable=False)
=======
#   filepath: Mapped[str] = mapped_column(String(512), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(512), nullable=False)
>>>>>>> 7e52a1e (resume stored into aws_s3_buckets)
>>>>>>> 379ca77 (resumes stored in aws s3 bucket)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    candidate: Mapped["Candidate"] = relationship(back_populates="resumes")
    applications: Mapped[list["Application"]] = relationship(back_populates="resume")
