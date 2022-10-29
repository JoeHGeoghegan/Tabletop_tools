# Imports
import streamlit as st
import pandas as pd
import numpy as np
from dataclasses import dataclass

from LoopGroup import Character, GroupLoop

###############################
######## Steamlit Data ########
###############################
@dataclass
class datablock:
    turn_track:pd.DataFrame

    def __init__(self):
        headers = ["name","health","armor_class","initiative","initiative_bonus","team","group"]
        self.turn_track = pd.DataFrame(columns=headers)

@st.cache(allow_output_mutation=True)
def setup():
    return datablock()
data = setup()

###############################
########## Functions ##########
###############################
# Function imports
import app_functions as fx

################################
######## Streamlit Code ########
################################
tabOverview, tabAddPerson, tabImportExport = st.tabs(["Overview", "Add Person", "Import/Export"])

with tabOverview:
    st.image(".\Images\Villains_turn_logo.png")

with tabImportExport:
    st.image(".\Images\Villains_turn_logo.png")

    uploaded_files = st.file_uploader("Select Villain's Turn CSV file(s)", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        # bytes_data = uploaded_file.read()
        # st.write("filename:", uploaded_file.name)
        # st.write(bytes_data)
        data.turn_track = pd.concat([data.turn_track,pd.read_csv(uploaded_file)])
    uploaded_files = None
    # if st.button("Clear Data"):
    #     if st.button("Are you sure?"):
    #         data.turn_track = data.turn_track[0:0]
    #         st.write("Data cleared")

with tabAddPerson:
    st.image(".\Images\Villains_turn_logo.png")

    newPerson_group = st.text_input("Group")
    newPerson_name = st.text_input('Character Name')
    newPerson_hp = st.text_input('HP')
    newPerson_ac = st.text_input('Armor Class')
    man_init = st.checkbox('Manually Roll Initiative?')
    if man_init :
        newPerson_init = st.text_input('Initiative')
    newPerson_b_init = st.text_input('Bonus Initiative')
    newPerson_team = st.text_input('Team')
    if st.button('Add Character'):
        character = {
            "name":newPerson_name,
            "health":newPerson_hp,
            "armor_class":newPerson_ac,
            "initiative": newPerson_init if man_init else fx.roll(20),
            "initiative_bonus":newPerson_b_init,
            "team":newPerson_team,
            "group":newPerson_group
        }
        data.turn_track=data.turn_track.append(character,ignore_index=True)

st.write("Turn Track")
st.write(data.turn_track)

########## SideBar ##########
selected_group_function = st.sidebar.selectbox(
    "Select Group Functions",
    options=["Move Group","Move Person to Other Group","Disruption","Merge Groups","Split Group"]
)

if (selected_group_function == "Move Group"):
    pass
elif (selected_group_function == "Move Person to Other Group"):
    pass
elif (selected_group_function == "Disruption"):
    pass
elif (selected_group_function == "Merge Groups"):
    pass
elif (selected_group_function == "Split Group"):
    group_to_split = st.sidebar.selectbox(
        "Select Group to Split",
        options=fx.groups_list(data.turn_track)
        )
    if(group_to_split!=None):
        group_to_split_1st = st.sidebar.text_input("First Half Name",value=f"{group_to_split} 1")
        group_to_split_2nd = st.sidebar.text_input("Second Half Name",value=f"{group_to_split} 2")
        group_to_split_df = fx.df_match_slice(data.turn_track,"group",group_to_split)
        st.sidebar.write("Selected Group:")
        st.sidebar.write(group_to_split_df)
        split_decicions = []
        st.sidebar.write("Where is:")
        for member in group_to_split_df['name']:
            split_decicions.append(st.sidebar.select_slider(member,options=[group_to_split_1st,group_to_split_2nd]))
        # st.sidebar.write(split_decicions)
        if st.sidebar.button("Split") :
            data.turn_track = fx.df_set_match_slice(data.turn_track,"group",group_to_split,split_decicions)