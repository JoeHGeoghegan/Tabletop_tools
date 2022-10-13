# Imports
import streamlit as st
from dataclasses import dataclass

from LoopGroup import Character, GroupLoop

# Steamlit Data
@dataclass
class datablock:
    selected_group_name:str
    selected_group:list
    turn_track:GroupLoop

@st.cache(allow_output_mutation=True)
def setup():
    return datablock()
data = setup()

###############################
########## Functions ##########
###############################
# TODO load a csv into a list of characters
def loadGroup(path):
    group_list = []
    return "",group_list

################################
######## Streamlit Code ########
################################

########## SideBar ##########
# Load Group Button
if st.sidebar.button("Load Team Data"):
    path = "" # TODO Browser to generate file path
    data.selected_group_name, data.selected_group = loadGroup(path) 
    st.sidebar.write(f"You have Loaded the \n{data.groupLoop.name} group. The team has been added to the end of the turn order as a new group")

