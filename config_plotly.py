import plotly.io as pio

def configurar_plotly():
    pio.templates.default = "plotly_white"
    
    pio.templates["plotly_white"].layout.update({
        'xaxis': {
            'title': {'text': 'Mês'},
            'showticklabels': True,
            'tickformat': '%Y-%m',
            'showgrid': True
        },
        'yaxis': {
            'title': {'text': 'Total Vendido (R$)'},
            'showticklabels': True,
            'showgrid': True
        },
        'title': {'text': 'Título do Gráfico'},
        'legend': {
            'orientation': 'h'
        }
    })

def get_colors():
    return {
        'cor_meio': 'rgba(82, 137, 228, 0.5)',  # Azul com 50% de transparência
        'cor_borda': '#104cae'  # Azul neon
    }
