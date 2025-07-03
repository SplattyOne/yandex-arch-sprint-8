from db.base import BaseDAO
from db.models import Report, User


class UsersDAO(BaseDAO):
    model = User


class ReportsDAO(BaseDAO):
    model = Report
