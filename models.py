# models.py
from flask_login import UserMixin
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

# 1. Criamos a Base aqui
class Base(DeclarativeBase):
    pass

# 2. Definimos as tabelas
class Colaborador(Base, UserMixin):
    __tablename__ = "colaborador"
    
    cpf: Mapped[str] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    empresa: Mapped[str] = mapped_column(String(50))
    cargo: Mapped[str] = mapped_column(String(50))
    senha: Mapped[str] = mapped_column(String(255))
    
    # Relacionamento para facilitar acesso às refeições
    refeicoes: Mapped[list["Refeicao"]] = relationship(back_populates="funcionario")
    
    def get_id(self):
        # O Flask-Login exige que o ID seja retornado como STRING
        return str(self.cpf)

class Refeicao(Base):
    __tablename__ = "refeicao"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(50))
    data: Mapped[datetime] =  mapped_column(DateTime, default=datetime.now)
    
    # FK
    funcionario_cpf: Mapped[str] = mapped_column(ForeignKey("colaborador.cpf"))
    
    # Relacionamento reverso
    funcionario: Mapped["Colaborador"] = relationship(back_populates="refeicoes")