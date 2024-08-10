import pandas as pd
from settings import engine

import pandas as pd
from settings import engine

def carregar_dados(empresa_id):
    try:
        query = """
        SELECT 
            DATE_TRUNC('month', a.data_abastecimento) AS mes,
            SUM(a.total) AS total_vendido,
            COUNT(*) AS quantidade_abastecimentos,
            SUM(a.quantidade) AS litragem_abastecida
        FROM 
            abastecimento AS a
        JOIN 
            automacao_bomba AS b
        ON 
            a.id_automacao_bomba = b.id_automacao_bomba
        WHERE 
            b.id_empresa = %s
        GROUP BY 
            mes
        ORDER BY 
            mes;
        """
        # Converter o ID da empresa para tipo int
        empresa_id = int(empresa_id)
        df = pd.read_sql(query, engine, params=(empresa_id,))
        return df
    except Exception as e:
        raise Exception(f"Erro ao conectar ao banco de dados: {e}")



def obter_empresas():
    try:
        query = """
        SELECT id_empresa AS id, nome
        FROM sis_empresa
        WHERE registro_ativo = 'S';
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        raise Exception(f"Erro ao consultar empresas: {e}")