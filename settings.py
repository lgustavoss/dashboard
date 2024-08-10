from sqlalchemy import create_engine

# Configuração da URL de conexão com SQLAlchemy
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/petros"

# Cria o engine de conexão com o SQLAlchemy
engine = create_engine(DATABASE_URL)
