
import models
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models

import os # chapter 6 추가

Base.metadata.create_all(bind=engine)   # 앱 시작 시 테이블이 없으면 생성

app = FastAPI()


origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")# chapter 6 추가

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],
    allow_origins=origins, # chapter 6 변경
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

# 요청마다 DB 세션을 열고, 끝나면 반드시 닫는 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MemoIn(BaseModel):
    content: str
class MemoOut(BaseModel):
    id: int
    content: str
    model_config = {"from_attributes": True}  # ORM 객체 → Pydantic 변환 허용(v2 문법)

@app.get("/memos", response_model=list[MemoOut])
def list_memos(db: Session = Depends(get_db)):
    return db.query(models.Memo).all()

@app.post("/memos", response_model=MemoOut)
def create_memo(memo: MemoIn, db: Session = Depends(get_db)):
    new = models.Memo(content=memo.content)
    db.add(new); db.commit(); db.refresh(new)
    return new

@app.delete("/memos/{memo_id}")
def delete_memo(memo_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Memo, memo_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Memo not found")
    db.delete(obj); db.commit()
    return {"ok": True}


# # main.py (1/4) — 임포트와 앱 생성(chapter3) 
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# app = FastAPI()

# #main.py — CORS 허용(chapter3)
# # ── CORS 설정 ──────────────────────────────────────────
# # 브라우저는 다른 출처(도메인/포트)로의 요청을 기본 차단한다.
# # 프론트(localhost:5173)에서 백엔드(localhost:8000)를 부르려면 허용이 필요.
# origins = ["http://localhost:5173"]   # 로컬 Vite 개발 서버
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,        # 허용할 출처 목록
#     allow_credentials=True,
#     allow_methods=["*"],          # GET, POST, DELETE 등 모두 허용
#     allow_headers=["*"],
# )

# # main.py (3/4 — 데이터 모델과 인메모리 저장소 (chapter3)
# # ── 데이터 모델 (Pydantic v2) ──────────────────────────
# class MemoIn(BaseModel):        # 요청 본문: 클라이언트가 보내는 데이터
#     content: str
# class MemoOut(BaseModel):       # 응답 본문: 서버가 돌려주는 데이터
#     id: int
#     content: str

# # ── 인메모리 저장소 ────────────────────────────────────
# memos: list[dict] = []          # 리스트에 저장(서버 재시작 시 사라짐)
# next_id = 1

# # main.py (4/4 · 같은 파일에 이어서) — 엔드포인트 3종 (chapter3)
# @app.get("/memos", response_model=list[MemoOut])
# def list_memos():
#     return memos                # 전체 메모 목록 반환

# @app.post("/memos", response_model=MemoOut)
# def create_memo(memo: MemoIn):
#     global next_id
#     new = {"id": next_id, "content": memo.content}
#     memos.append(new)
#     next_id += 1
#     return new

# @app.delete("/memos/{memo_id}")
# def delete_memo(memo_id: int):
#     global memos
#     for m in memos:
#         if m["id"] == memo_id:
#             memos = [x for x in memos if x["id"] != memo_id]
#             return {"ok": True}
#     raise HTTPException(status_code=404, detail="Memo not found")