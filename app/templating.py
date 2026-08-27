"""Jinja2テンプレートエンジンの設定。"""
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")