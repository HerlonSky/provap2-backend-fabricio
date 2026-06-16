import os
from contextlib import asynccontextmanager
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import Boolean, Column, Float, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/produtos_db",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, nullable=False, default=True)


class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    preco: float = Field(..., gt=0)
    estoque: int = Field(default=0, ge=0)
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_vazio(cls, nome: str) -> str:
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("nome nao pode ser vazio")
        return nome_limpo


class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    preco: float
    estoque: int
    ativo: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="API de Produtos", lifespan=lifespan)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/produtos", response_model=list[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)) -> list[Produto]:
    return db.query(Produto).order_by(Produto.id).all()


@app.post(
    "/produtos",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)) -> Produto:
    novo_produto = Produto(**produto.model_dump())
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


@app.get("/produtos/{id}", response_model=ProdutoResponse)
def buscar_produto(id: int, db: Session = Depends(get_db)) -> Produto:
    produto = db.get(Produto, id)
    if produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto nao encontrado")
    return produto


@app.delete("/produtos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_produto(id: int, db: Session = Depends(get_db)) -> Response:
    produto = db.get(Produto, id)
    if produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto nao encontrado")

    db.delete(produto)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
