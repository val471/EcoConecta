from pydantic import BaseModel, ConfigDict


class ContenidoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    categoria: str
    resumen: str
    cuerpo: str
