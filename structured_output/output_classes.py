from pydantic import BaseModel
from typing import List

class DocumentStructure(BaseModel):
    empresa: str
    unidade_monetaria: str
    ativo_circulante: List[str]
    ativo_nao_circulante: List[str]
    passivo_circulante: List[str]
    passivo_nao_circulante: List[str]
    patrimonio_liquido: List[str]
    demonstracao_do_resultado: List[str]
    datas: List[str]