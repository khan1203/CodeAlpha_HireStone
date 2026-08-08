from datetime import datetime
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 379ca77 (resumes stored in aws s3 bucket)

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

<<<<<<< HEAD
=======
=======
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
>>>>>>> 7e52a1e (resume stored into aws_s3_buckets)
>>>>>>> 379ca77 (resumes stored in aws s3 bucket)
from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"
<<<<<<< HEAD

=======
<<<<<<< HEAD

=======
>>>>>>> 7e52a1e (resume stored into aws_s3_buckets)
>>>>>>> 379ca77 (resumes stored in aws s3 bucket)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    headline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 379ca77 (resumes stored in aws s3 bucket)

    user: Mapped["User"] = relationship(back_populates="candidate")
    resumes: Mapped[list["Resume"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
<<<<<<< HEAD
=======
=======
    user: Mapped["User"] = relationship(back_populates="candidate")
    resumes: Mapped[list["Resume"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
>>>>>>> 7e52a1e (resume stored into aws_s3_buckets)
>>>>>>> 379ca77 (resumes stored in aws s3 bucket)
