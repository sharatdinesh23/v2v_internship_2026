from fastapi import APIRouter, Depends, HTTPException

from core.security import verify_supabase_jwt, verify_teacher_or_admin
from database import supabase
from schemas.core import NoteCreate, NoteUpdate

router = APIRouter(prefix="/api/notes", tags=["Notes"])


def _normalize_note_payload(note: NoteCreate, auth_data: dict) -> dict:
    payload = note.model_dump()
    if auth_data["role"] == "teacher":
        if not auth_data["internship_id"]:
            raise HTTPException(status_code=400, detail="Teacher is not assigned to an internship.")
        payload["internship_id"] = str(auth_data["internship_id"])
    else:
        payload["internship_id"] = str(payload["internship_id"])

    file_name = payload["file_name"].strip()
    if not file_name.endswith(".md"):
        file_name = f"{file_name}.md"
    payload["file_name"] = file_name
    payload["created_by"] = auth_data["user"]["id"]
    return payload


@router.post("/", status_code=201)
async def create_note(
    note: NoteCreate,
    auth_data: dict = Depends(verify_teacher_or_admin),
):
    try:
        payload = _normalize_note_payload(note, auth_data)
        res = supabase.table("Notes").insert(payload).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Failed to create note.")
        return res.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/", status_code=200)
async def get_notes(auth_data: dict = Depends(verify_supabase_jwt)):
    try:
        query = (
            supabase.table("Notes")
            .select("*, Internships(name)")
            .order("created_at", desc=True)
        )
        if auth_data["role"] != "admin":
            if not auth_data["internship_id"]:
                return []
            query = query.eq("internship_id", auth_data["internship_id"])

        res = query.execute()
        return res.data or []
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _get_note(note_id: str) -> dict:
    note_res = supabase.table("Notes").select("id, internship_id").eq("id", note_id).limit(1).execute()
    if not note_res.data:
        raise HTTPException(status_code=404, detail="Note not found.")
    return note_res.data[0]


def _ensure_note_scope(note: dict, auth_data: dict):
    if auth_data["role"] == "teacher" and str(note.get("internship_id")) != str(auth_data["internship_id"]):
        raise HTTPException(status_code=403, detail="Teacher cannot manage notes outside their internship.")


@router.put("/{note_id}", status_code=200)
async def update_note(
    note_id: str,
    payload: NoteUpdate,
    auth_data: dict = Depends(verify_teacher_or_admin),
):
    try:
        note = _get_note(note_id)
        _ensure_note_scope(note, auth_data)

        update_data = payload.model_dump(exclude_none=True)
        if "internship_id" in update_data:
            if auth_data["role"] == "teacher":
                update_data["internship_id"] = str(auth_data["internship_id"])
            else:
                update_data["internship_id"] = str(update_data["internship_id"])

        if not update_data:
            raise HTTPException(status_code=400, detail="No changes provided.")

        res = supabase.table("Notes").update(update_data).eq("id", note_id).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Failed to update note.")
        return res.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{note_id}", status_code=200)
async def delete_note(
    note_id: str,
    auth_data: dict = Depends(verify_teacher_or_admin),
):
    try:
        note = _get_note(note_id)
        _ensure_note_scope(note, auth_data)

        res = supabase.table("Notes").delete().eq("id", note_id).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Failed to delete note.")
        return {"message": "Note deleted successfully."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
