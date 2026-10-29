from email.parser import BytesParser
from email.policy import default
from uuid import UUID
from fastapi import APIRouter, Request
from app.errors import AppError
from app.schemas import IngestionReceipt, MaterialPage, MaterialDetail, LibraryChunk

router = APIRouter()


@router.post(
    "/api/materials",
    response_model=IngestionReceipt,
    status_code=202,
    operation_id="uploadMaterial",
)
async def upload_material(request: Request):
    content_type = request.headers.get("content-type", "")
    if not content_type.lower().startswith("multipart/form-data;"):
        raise AppError(
            "INVALID_MARKDOWN", "Envie um arquivo Markdown pelo formulário.", 422
        )
    body = (
        await request.body()
    )  # ASGI byte cap has already bounded this stream, no spool.
    message = BytesParser(policy=default).parsebytes(
        b"Content-Type: "
        + content_type.encode("ascii", errors="ignore")
        + b"\r\nMIME-Version: 1.0\r\n\r\n"
        + body
    )
    parts = list(message.iter_parts()) if message.is_multipart() else []
    if (
        len(parts) != 1
        or parts[0].get_param("name", header="content-disposition") != "file"
    ):
        raise AppError("INVALID_MARKDOWN", "Envie apenas um arquivo Markdown.", 422)
    part = parts[0]
    return await request.app.state.ingestion.accept_markdown(
        part.get_filename() or "", part.get_payload(decode=True) or b""
    )


@router.get("/api/materials", response_model=MaterialPage, operation_id="listMaterials")
async def list_materials(request: Request, cursor: UUID | None = None):
    return await request.app.state.ingestion.list_materials(cursor)


@router.get(
    "/api/materials/{material_id}",
    response_model=MaterialDetail,
    operation_id="getMaterial",
)
async def get_material(request: Request, material_id: UUID):
    return await request.app.state.ingestion.material_detail(material_id)


@router.get(
    "/api/materials/{material_id}/versions/{version_id}/chunks",
    response_model=dict[str, list[LibraryChunk]],
    operation_id="listLibraryChunks",
)
async def get_library_chunks(request: Request, material_id: UUID, version_id: UUID):
    return {"items": await request.app.state.ingestion.chunks(material_id, version_id)}


@router.get(
    "/api/materials/{material_id}/versions/{version_id}/chunks/{chunk_id}",
    response_model=LibraryChunk,
    operation_id="getLibraryChunk",
)
async def get_library_chunk(
    request: Request, material_id: UUID, version_id: UUID, chunk_id: str
):
    return (
        await request.app.state.ingestion.chunks(material_id, version_id, chunk_id)
    )[0]
