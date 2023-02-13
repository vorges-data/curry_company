import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='📊'
)


#image_path = '/home/vinicius/repos/ftc_programacao_python/Logo Preto Sem Fundo.png'
image = Image.open( 'Logo Preto Sem Fundo.png' )
st.sidebar.image( image, width = 120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## A mais rápida entrega da cidade')
st.sidebar.markdown("""---""") #Colocar um divider

st.write ('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Team Data Science at Vorges Data
    """ )