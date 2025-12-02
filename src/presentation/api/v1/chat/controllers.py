from fastapi import APIRouter, BackgroundTasks, HTTPException
from sse_starlette.sse import EventSourceResponse

from src.presentation.api.dependencies.auth import Auth, UserId
from src.presentation.api.dependencies.database import DBSession

from .schemas import ChangeIdDto
from .services import ChatService

router = APIRouter()

chat_service = ChatService(system_type="enhanced_shared")


@router.get("/chats")
async def list_chats(session: DBSession, user_id: str):
    try:
        response = await chat_service.list_chats(session, user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list-messages/{thread_id}")
async def list_messages(session: DBSession, thread_id: str, user_id: str):
    try:
        return await chat_service.list_messages(session, thread_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream")
async def chat(
    session: DBSession,
    prompt: str,
    thread_id: str,
    user_id: str,
    background_tasks: BackgroundTasks,
):
    try:
        event_generator = chat_service.stream_chat(
            session, prompt, thread_id, user_id, background_tasks
        )
        return EventSourceResponse(event_generator)
    except Exception as e:
        print(f"Erro no endpoint de chat SSE: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/change-id", dependencies=[Auth])
async def change_id(session: DBSession, dto: ChangeIdDto, user_id: UserId):
    try:
        return await chat_service.change_id(
            session, user_id=user_id, user_identifier=dto.user_identifier
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{thread_id}")
async def delete_Chat(session: DBSession, user_id: UserId, thread_id: str):
    try:
        response = await chat_service.delete_thread(
            session, user_id=user_id, thread_id=thread_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/ibvi")
# async def chat_ibvi(session: DBSession, dto: ChatPostDto):
#     try:
#         return await chat_service.chat_ibvi(session, dto.prompt)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
