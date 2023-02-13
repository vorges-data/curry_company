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

#st.set_page_config( page_title='Visão Entregadores', page_icon='🚲', layout='wide')
    
#========================================================================
#========================== Funções =====================================
#========================================================================
def top_delivers( df4, top_asc ):
                
        delivery_slow =  ( df4.loc[:, ['Delivery_person_ID','City','Time_taken(min)']]
                            .groupby( ['City', 'Delivery_person_ID'])
                            .mean()
                            .sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index() )
    
        df_aux01 = delivery_slow.loc[ delivery_slow ['City'] == 'Metropolitian', : ].head(10)
        df_aux02 = delivery_slow.loc[ delivery_slow ['City'] == 'Urban', : ].head(10)
        df_aux03 = delivery_slow.loc[ delivery_slow ['City'] == 'Semi-Urban', : ].head(10)
                        
        d5 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

        return d5
                               
                               
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

# import dataset
df1 = pd.read_csv('dataset/train.csv')

# cleaning dataset
df2 = clean_code( df1 )

#===========================
# Cópias dos DataFrames
#===========================
df4 = df2.copy()


#========================================================================
#========================== Menu Lateral ================================
#========================================================================
st.header('Marketplace - Visão Entregadores')

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
    'Quais as condições do trânsito:',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""") #Colocar um divider

weather_options = st.sidebar.multiselect(
       'Quais as condições climáticas:',
        ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'],
        default = ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy']
)

st.sidebar.markdown("""---""") #Colocar um divider

st.sidebar.markdown('### Powered by Vorges Data')


#===========================
# Filtros interativos
#===========================

# Filtro de Data
linhas_selecionadas = df4['Order_Date'] < date_slider
df4 = df4.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df4['Road_traffic_density'].isin( traffic_options )
df4 = df4.loc[linhas_selecionadas, :]

#Filtro de condições climáticas
linhas_selecionadas = df4['Weatherconditions'].isin( weather_options )
df4 = df4.loc[linhas_selecionadas, :]


#========================================================================
#========================== Layout no Streamlit =========================
#========================================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '', ''])

#===========================
# TAB I
#===========================
with tab1:
    #============================
    #Container 1
    #============================
    with st.container():
        st.subheader('Métricas')
        col1, col2, col3, col4 = st.columns(4)#, #gap='large')
        
        with col1:
            # A maior idade dos entregadores
            age_max = df4.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', age_max)
            
        with col2:
            # A maior idade dos entregadores
            age_min = df4.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', age_min)
        
        with col3:
            # Melhor condição do veículo
            condition_max = df4.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', condition_max)
            
        with col4:
            # Pior condição
            condition_min = df4.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', condition_min)
            
    #============================
    #Container 2
    #============================
    
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_avg_ratings_per_deliver = ( df4.loc[: ,['Delivery_person_ID','Delivery_person_Ratings']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index() )
            st.dataframe(df_avg_ratings_per_deliver)
        
        
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            # funçao agg
            # hack - para pular uma linha o código muito grande é só colocar entre ()
            agg_traffic = ( df4.loc[:, ['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density')
                              .agg({'Delivery_person_Ratings':['mean','std']} ) )
            
            # mudança de nome das colunas
            agg_traffic.columns = ['delivery_mean','delivery_std']
            
            #reset do index
            agg_traffic.reset_index()
            
            st.dataframe(agg_traffic)
            
            
            st.markdown('##### Avaliação média por clima')
            # media e desvio padrao
            agg_weather = ( df4.loc[:, ['Delivery_person_Ratings','Weatherconditions']]
                                .groupby('Weatherconditions')
                                .agg({'Delivery_person_Ratings': ['mean','std']} ) )
            
            # renomeando as colunas
            agg_weather.columns = ['delivery_mean','delivery_std']
            
            # reset index
            agg_weather.reset_index()
            
            st.dataframe(agg_weather)
            
            
    #============================
    #Container 3
    #============================
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            d5 = top_delivers( df4, top_asc=True )
            st.dataframe(d5)
              
        
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            d5 = top_delivers( df4, top_asc=False )
            st.dataframe(d5)
            
            
            
