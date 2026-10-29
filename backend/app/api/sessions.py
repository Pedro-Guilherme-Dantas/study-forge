from fastapi import APIRouter, Request, Response
from app.errors import AppError
from app.schemas import SessionReceipt

router = APIRouter()


@router.post(
    "/api/sessions",
    response_model=SessionReceipt,
    status_code=201,
    operation_id="createSession",
)
async def create_session(request: Request, response: Response):
    store = request.app.state.store
    try:
        session = store.get_session(request.cookies.get("sf_session"))
    except AppError:
        session = store.create_session()
    response.set_cookie(
        "sf_session", session.id, httponly=True, samesite="strict", path="/"
    )
    return SessionReceipt(
        session_id=session.id,
        server_instance_id=store.instance_id,
        csrf_token=session.csrf,
    )
