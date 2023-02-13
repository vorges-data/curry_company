# Libraries
import pandas as pd
import re
import plotly.express as px
import folium
from haversine import haversine
import plotly.graph_objects as go
from PIL import Image
import streamlit as st
from streamlit_folium import folium_static

# CSS Style
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


#st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide')

#========================================================================
#========================== Funções =====================================
#========================================================================

def country_maps( df3 ):
        # agrupar
        df_aux = ( df3.loc[:, ['Road_traffic_density', 'City','Delivery_location_latitude','Delivery_location_longitude']]
                                  .groupby(['City','Road_traffic_density'])
                                  .median()
                                  .reset_index() )
        
        # desenhar mapa para com o loop FOR
        map = folium.Map()
        
        for index, location_info in df_aux.iterrows(): # iterrows cria um objeto de iteração
             folium.Marker(
                  [
                      location_info['Delivery_location_latitude' ],
                      location_info['Delivery_location_longitude']
                  ],
                  popup = location_info[['City', 'Road_traffic_density']]
              ).add_to( map )
        
        folium_static( map, width=1024, height=600 )
        
        return None
    
def order_share_by_week( df3 ):
            
        # Quantidade de pedidos por semana / Numero único de entregadores por semana
        df_aux1 = df3.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux2 = df3.loc[:, ['Delivery_person_ID','week_of_year'] ].groupby('week_of_year').nunique().reset_index()
        # merge entre os dataframes
        df_aux = pd.merge(df_aux1, df_aux2, how='inner') 
        # divisao
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        # grafico
        fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
        
        return fig
            

def order_by_week( df3 ):
        # criar a coluna de semana
        df3['week_of_year'] = df3['Order_Date'].dt.strftime( '%U') # %U começa a conta a semana a partir do domingo
        # agrupar
        df_aux = df3.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
        # grafico de linhas
        fig = px.line( df_aux, x='week_of_year', y='ID')
        
        return fig
            

def traffic_order_city ( df3 ):
        # agrupamento
        df_aux = df3.loc[:, ['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
        # grafico
        fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
        
        return fig
    


def traffic_order_share( df3 ):
        # agrupar os pedidos por tipo de tráfego
        df_aux = df3.loc[:, ['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
        # remover o tipo "NaN"
        df_aux = df_aux.loc[ df_aux['Road_traffic_density'] != 'NaN', :]
        # criar a coluna de %
        df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
        # grafico de pizza
        fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
        
        return fig
               

def order_metric( df3 ):
        # 1. Quantidade de Pedidos por dia
        # colunas
        cols = ['ID', 'Order_Date']
        # selecao de linhas
        df_aux = df3.loc[:, cols].groupby('Order_Date').count().reset_index()
        # desenhar o gráfico de linhas
        fig = px.bar(df_aux, x='Order_Date', y='ID' )
        
        return fig

def clean_code ( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe
        
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de data
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
        
        Input: DataFrame
        Output: Dataframe
        
    """
    # excluindo NaN
    linhas_selecionadas = ( df1['Delivery_person_Age'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    # excluindo NaN
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    # excluindo NaN
    linhas_selecionadas = (df1['City'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    # excluindo NaN
    linhas_selecionadas = (df1['Festival'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    
    # 1. convertendo a coluna age de objeto para numero
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # 2. convertendo a coluna Ratings de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # 3. convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    # 4. convertendo multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # 5. Removendo os espacos dentro de string/object/texto
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    # Limpar para retirar (min) e converter em número
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1

#=======================================================================================
#================== Inicio da estrutura lógica do código ===============================
#=======================================================================================

# import dataset
df = pd.read_csv('dataset/train.csv')

df1 = df.copy()

# Limpando os dados
df1 = clean_code( df )


#===========================
# Cópias dos DataFrames
#===========================
df3= df1.copy()


#========================================================================
#========================== Menu Lateral ================================
#========================================================================
st.header('Marketplace - Visão Cliente')

#===========================
# Criar o menu lateral
#===========================

# Importar uma imagem
#image_path = '/home/vinicius/repos/ftc_programacao_python/Logo Preto Sem Fundo.png'
image = Image.open( 'Logo Preto Sem Fundo.png' )
st.sidebar.image(image, width=160)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## A mais rápida entrega da cidade')
st.sidebar.markdown("""---""") #Colocar um divider

# filtro
st.sidebar.markdown('## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""") #Colocar um divider

# filtro 2
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""") #Colocar um divider
st.sidebar.markdown('### Powered by Vorges Data')


#===========================
# Filtros interativos
#===========================

# Filtro de Data
linhas_selecionadas = df3['Order_Date'] < date_slider
df3 = df3.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df3['Road_traffic_density'].isin( traffic_options )
df3 = df3.loc[linhas_selecionadas, :]


#========================================================================
#========================== Layout no Streamlit =========================
#========================================================================

#===========================
# Criar abas para página
#===========================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])


with tab1:
    #============================
    #Container 1
    #============================
    # criar o conteiner da página (dividir em dois)
    with st.container():
        fig = order_metric( df3 )
        st.markdown('# Pedidos por Dia')
        st.plotly_chart( fig, use_container_width=True )
        
    #============================
    #Container 2
    #============================
    with st.container():
        # numero de colunas na página streamlit
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = traffic_order_share( df3 )
            st.header( 'Distribuição dos pedidos por tipo de tráfego.')
            st.plotly_chart(fig, use_container_width=True)
            
            
        with col2:
                st.header( 'Comparação do volume de pedidos por cidade e tipo de tráfego.')
                fig = traffic_order_city ( df3 )
                st.plotly_chart(fig, use_container_width=True)
                
                
with tab2:
    #============================
    #Container 1
    #============================
    with st.container():
        st.header('Pedidos por Semana')
        fig = order_by_week( df3 )
        st.plotly_chart(fig, use_container_width=True)
        
        
    #============================
    #Container 2
    #============================
    with st.container():
        st.header('Quantidade de pedidos por entregador por semana')
        fig = order_share_by_week ( df3 )
        st.plotly_chart(fig, use_container_width=True)
        

#===========================
# TAB III
#===========================        
with tab3:
    st.header('Localização central de cada cidade por tipo de tráfego')
    country_maps ( df3 )
    
