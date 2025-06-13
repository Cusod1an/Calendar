# app/models.py
from app import db
from sqlalchemy.dialects.mysql import TINYINT

class Equipment(db.Model):
    __tablename__ = 'Equipment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    model = db.Column(db.String(100))
    maintenance_tasks = db.relationship('MaintenanceTask', backref='equipment', lazy=True, cascade="all, delete-orphan")

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('admin', 'technician'), nullable=False)
    maintenance_tasks = db.relationship('MaintenanceTask', backref='user', lazy=True)

class MaintenanceTask(db.Model):
    __tablename__ = 'MaintenanceTask'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('Equipment.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date_scheduled = db.Column(db.Date, nullable=False)
    date_completed = db.Column(db.Date)
    status = db.Column(db.Enum('pending', 'completed', 'overdue'), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='SET NULL'), nullable=True)
    notifications = db.relationship('Notification', backref='maintenance_task', cascade="all, delete-orphan", lazy=True)

class Notification(db.Model):
    __tablename__ = 'Notification'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('MaintenanceTask.id', ondelete='CASCADE'), nullable=False)
    notify_time = db.Column(db.DateTime, nullable=False)
    sent = db.Column(TINYINT, default=0)
