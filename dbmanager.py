from sqlalchemy import create_engine, select, Date, cast
from sqlalchemy.orm import Session, joinedload
from werkzeug.security import generate_password_hash
from datetime import datetime
import models
import os

from config import DATABASE_URL, SECRET_KEY

class dbmanager():
    def __init__(self, url):

        self.engine = create_engine(url)

        models.Base.metadata.create_all(self.engine)

    def get_colaborador_by_cpf(self, cpf_busca):
        with Session(self.engine) as session:
            try:
                # 1. Monta o Select: "Selecione o Colaborador onde o cpf é igual ao cpf_busca"
                stmt = select(models.Colaborador).where(models.Colaborador.cpf == cpf_busca)
                
                # 2. Executa e pega o primeiro resultado escalar (o objeto)
                # Se não achar ninguém, retorna None
                usuario = session.scalars(stmt).first()
                
                return usuario
                
            except Exception as e:
                print(f"Erro ao buscar usuário: {e}")
                return None

    def quant_refei_detl_empresa(self, date, empresa):
        with Session(self.engine) as session:
            try:
                data_formatada = datetime.strptime(date, "%d/%m/%Y").date()

                # 1. Monta o Select com JOIN e o novo filtro
                stmt = (
                    select(models.Refeicao)
                    .join(models.Colaborador) # <-- Conecta a tabela de Refeicao com a de Colaborador
                    .options(joinedload(models.Refeicao.funcionario)) # Mantém os dados do colaborador carregados
                    .where(
                        cast(models.Refeicao.data, Date) == data_formatada,
                        models.Colaborador.empresa == empresa # <-- Aqui está a mágica: o filtro da empresa!
                    )
                )

                # 2. Executa a query
                refeicoes = session.scalars(stmt).all()
                return refeicoes
                
            except Exception as e:
                print(f"Erro ao buscar refeições por empresa: {e}")
                return [] # Boa prática: retornar uma lista vazia em vez de 'None' para não quebrar o 'for' no HTML