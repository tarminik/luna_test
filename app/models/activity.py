from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("activities.id"), nullable=True)

    parent: Mapped[Optional["Activity"]] = relationship(
        back_populates="children", remote_side="Activity.id"
    )
    children: Mapped[list["Activity"]] = relationship(back_populates="parent")

    MAX_DEPTH = 3

    def depth(self) -> int:
        """Calculate depth by walking up the in-memory parent chain."""
        level = 1
        node = self
        while node.parent is not None:
            level += 1
            node = node.parent
        return level
