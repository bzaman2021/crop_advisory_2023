# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 12:24:44 2023

@author: asus
"""


import streamlit as st
import pickle
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from config import price,req_levels,fertilizers_nutrient_pct
from PIL import Image


st.set_page_config(page_title='Crop Recommendation Model',layout='wide')

model=joblib.load("rfc_crop_advisory_model.pkl")
perform_df=pd.read_csv("Model Performance.csv")
env_df=pd.read_excel("new data.xlsx")
env_df=env_df.dropna()

mapping=env_df[['Crop_Name','Crop-Variety']].drop_duplicates().set_index("Crop_Name")

variety_dict={"Horticulture":" Mango, Litchi, Malta, Oranges, Lemon, Aonla, Guava,Pomegranate",
              "Wheat":"UP 2903, UP 2938, UP 2855, UP 2784, UP2628, UP2554, HD3086, HD2967, WH1105, DPW 621-50, PBW 502, WH542, BL 953",
              "Mustard":"VLToria 3, Pant Hill Toria 1, Uttara, Pant Pili Sarson 1, Pant Rye 20, Pant Rye 21, RGN",
              "Maize":"Sankul: Pant Sankul Makka-3 , Sweta, Bajora Makka 1, Vivak Sankul 11, Hybrid: H M 10, H Q PM 1, 4, Pusa HQPM5, Pant Sankar makka 1 & 4, Sartaj, P 3522, Bio 9544",
              "Potato":"Kufri Jyoti, Kufri Giriraj, Kufri Jawahar, kufri Bahar, Kufri satraj, Kufri chipsona, Kufri Lalima, Kufri Chandan",
              "Paddy":"Narendra 359, HKR 47, PR 113 & 114, Pant Dhan 10,12, 19, 24, 26 & 28, Pant Sugandha Dhan-15,17, 25 & 27, Pusa Basmati 1121, 2511 & 1509, Pant Bansmati 1 and 2, Pusa Basmati 1692, Pusa Basmati 1847, Pusa Basmati 1885, Pusa Basmati 1886, Pusa Basmati 1637, Pusa Basmati 1718, Pusa Basmati 1728",
              "Vegetable":"Onion, Chilly, Peas, Radish, Cauliflower",
              " Soyabean":"PS 1225, PS 1347, PS 24, PS 26, PS 19",
              " Maize":"Sankul: Pant Sankul Makka-3 , Sweta, Bajora Makka 1, Vivak Sankul 11, Hybrid: H M 10, H Q PM 1, 4, Pusa HQPM5, Pant Sankar makka 1 & 4, Sartaj, P 3522, Bio 9544",
              " Potato":"Kufri Jyoti, Kufri Giriraj, Kufri Jawahar, kufri Bahar, Kufri satraj, Kufri chipsona, Kufri Lalima, Kufri Chandan"}


def fertilizer_bags_2(crop_name):
    if crop_name in req_levels.keys():
        req_npk_per_hectare=req_levels[crop_name]
        npk_present={"Nitrogen":n,"Phosphorus":p,"Potash":k}
        aux_df=pd.DataFrame([req_npk_per_hectare,npk_present],index=["Required","Present"]).T
        aux_df['Fertilizer req']=aux_df["Required"]-aux_df['Present']
        req_npk_total=aux_df['Fertilizer req']*area
        # Blend 1
        bags_urea_req=int(np.ceil((req_npk_total['Nitrogen']/fertilizers_nutrient_pct['Urea']['Nitrogen'])/50))
        bags_ssp_req=int(np.ceil((req_npk_total['Phosphorus']/fertilizers_nutrient_pct['SSP']['Phosphorus'])/50))
        bags_mop_req=int(np.ceil((req_npk_total['Potash']/fertilizers_nutrient_pct['MOP']['Potash'])/50))
        # Blend 2
        bags_dap_req=int(np.ceil((req_npk_total['Phosphorus']/fertilizers_nutrient_pct['DAP']['Phosphorus'])/50))
        bags_urea_req_2=int(np.ceil(((req_npk_total['Nitrogen']-(fertilizers_nutrient_pct['DAP']['Nitrogen']*bags_dap_req))/fertilizers_nutrient_pct['Urea']['Nitrogen'])/50))
        bags_mop_req_2=int(np.ceil((req_npk_total['Potash']/fertilizers_nutrient_pct['MOP']['Potash'])/50))
        
        final_str=[bags_urea_req,bags_ssp_req,bags_mop_req,bags_dap_req,bags_urea_req_2,bags_mop_req_2]
        blend_1_price=bags_urea_req*price['Urea']+bags_ssp_req*price['SSP']+bags_mop_req*price['MOP']
        blend_2_price=bags_dap_req*price['DAP']+bags_urea_req_2*price['Urea']+bags_mop_req_2*price['MOP']
        
    else:
        final_str,blend_1_price,blend_2_price="Not Found",'NA','NA'
    
    return final_str,blend_1_price,blend_2_price

#%%

# Header Display

st.markdown('<div style="text-align: center; color:#004F92 ;font-size:40px; font-weight:bold">DeepSpatial Agriverse Platform</div>', unsafe_allow_html=True)
st.markdown('<div style="background-color:#00609C;padding:7px"> <h2 style="color:white;text-align:center;">Crop Advisory</h2> </div>',unsafe_allow_html=True)
st.header("")


left,right=st.columns(2)

with right:
# Take Inputs
    district=st.selectbox("District",("Dehradun", "Champawat"),disabled=True)
    block=st.selectbox("Block",("Vikasnagar", "Dalu"),disabled=True)
    village=st.selectbox("Village",env_df['Village Name'].unique())
    farm_num_df=env_df.groupby(['Village Name','Crop_Name'])['Farm_ID'].unique().reset_index()
    pivot_df=pd.pivot_table(farm_num_df,index="Village Name",columns='Crop_Name',values="Farm_ID")
    pivot_df_2=pivot_df.applymap(lambda z:z[:10])
    vlg_df=pivot_df_2.loc[village,:]
    farm_opts=np.append(np.append(vlg_df[0],vlg_df[1]),vlg_df[2])
    farm_opts=np.array(farm_opts,dtype=int)
    farm=st.selectbox("Farm Number",farm_opts)

inp_df=env_df.set_index(['Village Name','Farm_ID'])
n=inp_df.loc[(village,farm),'N']
p=inp_df.loc[(village,farm),'P']
k=inp_df.loc[(village,farm),'K']
ph=inp_df.loc[(village,farm),'pH']
area=inp_df.loc[(village,farm),'Area (Hectares)']
rain=inp_df.loc[(village,farm),'Rainfall']    
temp=inp_df.loc[(village,farm),'Temperature']
humid=inp_df.loc[(village,farm),'Humidity']

with left:
    c1,c2=st.columns(2)
    with c1:
        fig_temp = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = temp,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Temperature","font":{"size":24,"color":"red"}},  
        gauge = {
                'axis': {'range': [None, 40], 'tickwidth': 1, 'tickcolor': "darkred"},
                'bar': {'color': "#8b0000"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 20], 'color': '#FFFF00'},
                    {'range': [20, 40], 'color': '#FFA500'}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 38}}))
        fig_temp.update_layout(height=300)
        st.plotly_chart(fig_temp,use_container_width=True)

    with c2:
        fig_humid = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = humid,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Humidity","font":{"size":24,"color":"darkblue"}},
            gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 50], 'color': 'cyan'},
                        {'range': [50, 100], 'color': 'royalblue'}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 98}}))
        fig_humid.update_layout(height=300)
        st.plotly_chart(fig_humid,use_container_width=True)

if st.button("Predict",use_container_width=True):
    pred=model.predict([[area,humid,k,n,p,rain,temp,ph]])
    crop_list=pred[0].split(",")
    variety_list=[variety_dict[c] for c in crop_list]
    display_df=pd.DataFrame(zip(crop_list,variety_list),columns=["Recommended Crop","Variety"],index=range(1,len(crop_list)+1))
    st.dataframe(display_df,use_container_width=True)
    
    bags_req=[]
    blend_1_price_lst=[]
    blend_2_price_lst=[]
    for c in crop_list:
        ans=fertilizer_bags_2(c)
        bags_req.append(ans[0])
        blend_1_price_lst.append(ans[1])
        blend_2_price_lst.append(ans[2])
        
        
    
    m1,m2,m3,m4,m5,m6,m7=st.columns(7)    
    st.markdown(""" <style> [data-testid="stMetricValue"] {font-size: 20px;}</style>""",unsafe_allow_html=True,)
    if len(crop_list)==4:
        with m1:
            st.write(crop_list[0])
            horti = Image.open('imgs/fruits.jpg')
            image_1=horti.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[0]
                price_1=blend_1_price_lst[0]
                price_2=blend_2_price_lst[0]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[0]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])             
                   st.metric("Total Cost = ",price_2)
    
        with m3:
            st.write(crop_list[1])
            maize = Image.open('imgs/Maize.jpg')
            image_1=maize.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[1]
                price_1=blend_1_price_lst[1]
                price_2=blend_2_price_lst[1]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[1]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])
                   st.metric("Total Cost = ",price_2)    
 
        with m5:
            st.write(crop_list[2])
            potato = Image.open('imgs/potato.jpg')
            image_1=potato.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[2]
                price_1=blend_1_price_lst[2]
                price_2=blend_2_price_lst[2]

                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[2]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])             
                   st.metric("Total Cost = ",price_2)
        
        with m7:
            st.write(crop_list[3])
            soya = Image.open('imgs/soyabean.jpg')
            image_1=soya.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[3]
                price_1=blend_1_price_lst[3]
                price_2=blend_2_price_lst[3]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[3]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])             
                   st.metric("Total Cost = ",price_1)    
    
    elif len(crop_list)==7:
        with m1:
            st.write(crop_list[0])
            horti = Image.open('imgs/fruits.jpg')
            image_1=horti.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[0]
                price_1=blend_1_price_lst[0]
                price_2=blend_2_price_lst[0]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[0]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])
                   st.metric("Total Cost = ",price_2)    
  
        with m2:
            st.write(crop_list[1])
            mustard = Image.open('imgs/mustard.jpg')
            image_1=mustard.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[1]
                price_1=blend_1_price_lst[1]
                price_2=blend_2_price_lst[1]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[1]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])
                   st.metric("Total Cost = ",price_2)    
        
        with m3:
            st.write(crop_list[2])
            wheat = Image.open('imgs/Wheat.jpg')
            image_1=wheat.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[2]
                price_1=blend_1_price_lst[2]
                price_2=blend_2_price_lst[2]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2]) 
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[2]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])
                   st.metric("Total Cost = ",price_2)    

        with m4:
            st.write(crop_list[3])
            maize = Image.open('imgs/Maize.jpg')
            image_1=maize.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[3]
                price_1=blend_1_price_lst[3]
                price_2=blend_2_price_lst[3]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[3]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])
                   st.metric("Total Cost = ",price_2)    

        with m5:
            st.write(crop_list[4])
            paddy = Image.open('imgs/Paddy.jpg')
            image_1=paddy.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[4]
                price_1=blend_1_price_lst[4]
                price_2=blend_2_price_lst[4]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[4]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])
                   st.metric("Total Cost = ",price_2)    

        with m6:
            st.write(crop_list[5])
            potato = Image.open('imgs/potato.jpg')
            image_1=potato.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[5]
                price_1=blend_1_price_lst[5]
                price_2=blend_2_price_lst[5]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[5]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])
                   st.metric("Total Cost = ",price_2)    
    
        with m7:
            st.write(crop_list[6])
            veg = Image.open('imgs/veg.jpg')
            image_1=veg.resize((100,50))
            st.image(image_1,use_column_width=True)
            with st.expander("Blend-1"):
                crp_bags_req=bags_req[6]
                price_1=blend_1_price_lst[6]
                price_2=blend_2_price_lst[6]
                if crp_bags_req=="Not Found":
                    m11,m22,m33=st.columns(3)            
                    with m11:
                        st.metric("Urea","NA")
                    with m22:
                        st.metric("SSP","NA")    
                    with m33:
                        st.metric("MOP","NA")    
                else:
                    m11,m22,m33=st.columns(3)
                    with m11:
                        st.metric("Urea",crp_bags_req[0])    
                    with m22:
                        st.metric("SSP",crp_bags_req[1])    
                    with m33:
                        st.metric("MOP",crp_bags_req[2])
                    st.metric("Total Cost = ",price_1)    
            with st.expander("Blend-2"):
               crp_bags_req=bags_req[6]
               if crp_bags_req=="Not Found":
                   m11,m22,m33=st.columns(3)            
                   with m11:
                       st.metric("DAP","NA")
                   with m22:
                       st.metric("Urea","NA")    
                   with m33:
                       st.metric("MOP","NA")    
               else:
                   m11,m22,m33=st.columns(3)
                   with m11:
                       st.metric("DAP",crp_bags_req[3])    
                   with m22:
                       st.metric("Urea",crp_bags_req[4])    
                   with m33:
                       st.metric("MOP",crp_bags_req[5])
                   st.metric("Total Cost = ",price_2)    




st.markdown("<br></br>",unsafe_allow_html=True)        
x1,x2,x3=st.columns(3)
with x2:
    st.caption("Model Accuracies for Crop Advisory")
    perform_df.index=[1,2,3,4]
    st.dataframe(perform_df)
    


