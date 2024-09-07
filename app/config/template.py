from fastapi.templating import Jinja2Templates


def get_templates() -> Jinja2Templates:
    return Jinja2Templates(directory="templates", autoescape=False, auto_reload=True)
