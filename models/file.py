"""File database"""

from config import db


class File(db.Model):
    """File database associated with users"""

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    __table_args__ = (
        db.UniqueConstraint("user_id", "filename", name="unique_user_filename"),
    )
