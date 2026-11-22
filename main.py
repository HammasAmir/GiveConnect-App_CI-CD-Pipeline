from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import initialize_database, get_connection
from events import start_event_worker, publish_donation_event

app = FastAPI(title="GiveConnect")

initialize_database()

start_event_worker()

templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )



@app.get("/donor")
def donor_page(request: Request):
    with get_connection() as connection:
        donations = connection.execute(
            "SELECT * FROM donations ORDER BY id DESC"
        ).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="donor.html",
        context={"donations": donations}
    )



@app.get("/beneficiary")
def beneficiary_page(request: Request):
    with get_connection() as connection:
        donations = connection.execute(
            "SELECT * FROM donations WHERE status = 'available' ORDER BY id DESC"
        ).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="beneficiary.html",
        context={"donations": donations}
    )


@app.post("/donate")
def create_donation(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    donor_name: str = Form(...)
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO donations
                (title, description, category, donor_name)
            VALUES (?, ?, ?, ?)
            """,
            (title, description, category, donor_name)
        )

        donation_id = cursor.lastrowid

    publish_donation_event(donation_id, title)

    return RedirectResponse(url="/donor", status_code=303)



@app.get("/check-donations")
def check_donations():
    with get_connection() as connection:
        donations = connection.execute(
            "SELECT * FROM donations"
        ).fetchall()

    return [dict(donation) for donation in donations]
