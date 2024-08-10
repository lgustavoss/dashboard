import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import locale
from config_plotly import configurar_plotly, get_colors
from database import carregar_dados, obter_empresas

# Configurar a página
st.set_page_config(page_title="Dashboard", page_icon=":car:", layout="wide")

# Adicionar a logomarca acima dos filtros na barra lateral
st.sidebar.image("./logo.png", use_column_width=True)

# Configurar localidade para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

configurar_plotly()
cores = get_colors()

try:
    # Obter a lista de empresas
    df_empresas = obter_empresas()
    empresa_ids = df_empresas['id'].tolist()
    empresa_nomes = df_empresas['nome'].tolist()
except Exception as e:
    st.error(str(e))
    empresa_ids = []
    empresa_nomes = []

# Selecionar a empresa
if empresa_nomes:
    empresa_selecionada = st.sidebar.selectbox('Selecione a Empresa', empresa_nomes)
    empresa_id = int(df_empresas[df_empresas['nome'] == empresa_selecionada]['id'].values[0])
else:
    st.error("Não foi possível carregar a lista de empresas.")
    empresa_id = None

if empresa_id:
    try:
        df = carregar_dados(empresa_id)
    except Exception as e:
        st.error(str(e))
        df = pd.DataFrame()

    if not df.empty:
        # Converter a coluna 'mes' para datetime
        df['mes'] = pd.to_datetime(df['mes'])
        
        # Extrair ano e mês
        df['ano'] = df['mes'].dt.year
        df['mes_nome'] = df['mes'].dt.strftime('%B')
        df['mes_num'] = df['mes'].dt.month  # Número do mês para ordenação

        # Sidebar para filtro de ano e mês
        st.sidebar.title('Filtros')

        anos_disponiveis = df['ano'].unique()
        anos_selecionados = st.sidebar.multiselect('Selecione os Anos', anos_disponiveis, default=anos_disponiveis)

        meses_disponiveis = df['mes_nome'].unique()
        meses_selecionados = st.sidebar.multiselect('Selecione os Meses', meses_disponiveis, default=meses_disponiveis)

        # Filtrar DataFrame com base nos anos e meses selecionados
        df_filtrado = df[(df['ano'].isin(anos_selecionados)) & (df['mes_nome'].isin(meses_selecionados))]

        # Criar DataFrame com todos os meses e anos selecionados
        anos_selecionados = df['ano'].unique()
        meses = pd.DataFrame({
            'mes_num': range(1, 13),
            'mes_nome': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        })

        # Criar DataFrame com todos os meses e anos selecionados
        df_completo = pd.merge(pd.MultiIndex.from_product([anos_selecionados, meses['mes_num']], names=['ano', 'mes_num']).to_frame(index=False), 
                              meses, 
                              on='mes_num', 
                              how='left')
        df_completo = pd.merge(df_completo, df_filtrado[['ano', 'mes_num', 'total_vendido', 'litragem_abastecida', 'quantidade_abastecimentos']], 
                               on=['ano', 'mes_num'], 
                               how='left')

        # Calcular totais
        total_vendido = df_filtrado['total_vendido'].sum()
        total_litragem = df_filtrado['litragem_abastecida'].sum()
        total_abastecimentos = df_filtrado['quantidade_abastecimentos'].sum()

        # Formatar valores para o padrão brasileiro
        total_vendido_str = locale.format_string('%.2f', total_vendido, grouping=True)
        total_litragem_str = locale.format_string('%.2f', total_litragem, grouping=True)
        total_abastecimentos_str = locale.format_string('%d', total_abastecimentos, grouping=True)

        # Mostrar cards com totais
        st.markdown("### Resumo do Período")
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Vendido (R$)", f"R$ {total_vendido_str}")
        col2.metric("Total de Litragem (L)", f"{total_litragem_str} L")
        col3.metric("Total de Abastecimentos", f"{total_abastecimentos_str}")

        # Gráficos
        fig1 = go.Figure()
        fig2 = go.Figure()
        fig3 = go.Figure()

        # Paleta de cores para diferentes anos
        cores_anos = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        for i, ano in enumerate(anos_selecionados):
            df_ano = df_completo[df_completo['ano'] == ano]

            # Gráfico de Total Vendido
            fig1.add_trace(go.Scatter(
                x=df_ano['mes_nome'],
                y=df_ano['total_vendido'],
                mode='lines+markers',
                name=f'Total Vendido (R$) - {ano}',
                line=dict(color=cores_anos[i % len(cores_anos)])
            ))

            # Gráfico de Litragem Abastecida
            fig2.add_trace(go.Scatter(
                x=df_ano['mes_nome'],
                y=df_ano['litragem_abastecida'],
                mode='lines+markers',
                name=f'Litragem Abastecida - {ano}',
                line=dict(color=cores_anos[i % len(cores_anos)])
            ))

            # Gráfico de Quantidade de Abastecimentos
            fig3.add_trace(go.Scatter(
                x=df_ano['mes_nome'],
                y=df_ano['quantidade_abastecimentos'],
                mode='lines+markers',
                name=f'Quantidade de Abastecimentos - {ano}',
                line=dict(color=cores_anos[i % len(cores_anos)])
            ))

        # Atualizar layout dos gráficos
        for fig in [fig1, fig2, fig3]:
            fig.update_layout(
                xaxis_title='Mês',
                yaxis_title='Valor',
                xaxis=dict(
                    tickmode='array',
                    tickvals=[i for i in range(12)],
                    ticktext=['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                ),
                template='plotly_white'
            )

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.error("Não foi possível carregar os dados para a empresa selecionada.")
