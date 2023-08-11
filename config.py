# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 17:05:49 2023

@author: asus
"""

# For conversion of areas to one metric i.e. Hectare
area_dict={"Nali":0.020067,"Mutthi":0.00125,"Bigha":0.080937,"Acre":0.404686,"Hectare":1}



# Required levels of NPK for every crop in Kg/ha
req_levels={"Wheat":{"Nitrogen":135,"Phosphorus":60,"Potash":50},
            "Paddy":{"Nitrogen":135,"Phosphorus":40,"Potash":30},
            "Sugarcane":{"Nitrogen":135,"Phosphorus":40,"Potash":30},
            "Mustard":{"Nitrogen":120,"Phosphorus":40,"Potash":30}}


# Amount of NPK present in different fertilizers
fertilizers_nutrient_pct={"Urea":{"Nitrogen":0.46,"Phosphorus":0,"Potash":0},
                          "SSP":{"Nitrogen":0,"Phosphorus":0.16,"Potash":0},
                          "MOP":{"Nitrogen":0,"Phosphorus":0,"Potash":0.6},
                          "DAP":{"Nitrogen":0.18,"Phosphorus":0.46,"Potash":0}}

price={"Urea":266,"SSP":2500,"MOP":1700,"DAP":1300}





