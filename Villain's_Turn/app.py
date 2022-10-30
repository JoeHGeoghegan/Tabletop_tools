# Imports
from inspect import Attribute
import streamlit as st
import pandas as pd
import numpy as np
from dataclasses import dataclass

###############################
######## Steamlit Data ########
###############################
@dataclass
class datablock:
    turn_track:pd.DataFrame

    def __init__(self):
        headers = ["name","health","armor_class","initiative","initiative_bonus","team","group","attributes"]
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
st.image(".\Images\Villains_turn_logo.png")
tabOverview, tabModifications, tabSettings, tabImportExport = st.tabs(["Overview", "Modifications", "Settings", "Import/Export"])
with tabOverview:
    # Current Turn #TODO
    # On Deck #TODO
    # Combat expander #TODO
    pass
with tabSettings:
    with st.expander("Turn Tracker Visuals"):
        show_turn_tracker = st.checkbox('Show Turn Tracker',value=True)
        if show_turn_tracker:
            show_health = st.checkbox('Show Health')
            show_ac = st.checkbox('Show Armor Class')
            show_init = st.checkbox('Show Initiative',value=True)
            show_team = st.checkbox('Show Teams',value=True)
            show_group = st.checkbox('Show Combat Groups',value=True)
            show_attributes = st.checkbox('Show Additional Attributes')
    with st.expander("Audit Settings"): #TODO
        enable_audit = st.checkbox('Enable Audit',value=True)
    
with tabImportExport:
    st.header("Importing")
    uploaded_files = st.file_uploader("Select Villain's Turn CSV file(s)", accept_multiple_files=True)
    keep_imported_groups = st.checkbox("Keep Imported Groups? (If they exist)",value=True)
    if uploaded_files : # If a single file or more has been added
        if st.button("Add to Turn Track?"):
            for uploaded_file in uploaded_files:
                data.turn_track = pd.concat([data.turn_track,fx.read_import(uploaded_file,import_groups=keep_imported_groups)])
            uploaded_files = None
    st.header("Exporting")
    #TODO Exporting
with tabModifications:
    selected_modification = st.selectbox(
        "What do you want to Modify",
        options=["Select Function","Add Person","Remove Person","Change Initiatives"]
    )
    if (selected_modification == "Select Function"): #TODO
        pass
    elif (selected_modification == "Add Person"):
        newPerson_name = st.text_input('Character Name')
        newPerson_hp = st.number_input('HP',value=0)
        newPerson_ac = st.number_input('Armor Class',value=0)
        man_init = st.checkbox('Manually Roll Initiative?')
        if man_init :
            newPerson_init = st.number_input('Initiative',value=0)
        newPerson_b_init = st.number_input('Bonus Initiative',value=0)
        newPerson_team = st.text_input('Team')
        newPerson_group = st.text_input("Group")
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
    elif (selected_modification == "Remove Person"): #TODO
        # select person and a button using drop pd.drop(index of character)
        pass
    elif (selected_modification == "Change Initiatives"):
        col_init_random, col_init_sort = st.columns(2)
        with col_init_random:
            if st.button("Auto Reroll all Initiatives?"):
                data.turn_track = fx.auto_initiative(data.turn_track)
        with col_init_sort:
            if st.button("Sort Initiatives"):
                data.turn_track = fx.sort_by_initiatives(data.turn_track)
        # select person, initiative field, and a button
        with st.expander("Manually Set/Change Initiatives"):
            selected_character = st.selectbox("Character",options=fx.character_list(data.turn_track))
            new_initiative = st.number_input(
                "New Initiative",
                value = 1
            )
            if st.button("Set Initiative"):
                data.turn_track.loc[selected_character,'initiative']=new_initiative #TODO For some reason breaks the DF

########## SideBar ##########
selected_group_function = st.sidebar.selectbox(
    "Select Group Functions",
    options=["Select Function","Assign Groups","Move Group","Move Person to Other Group","Disruption","Merge Groups","Split Group","Change Group Name"]
)

if (selected_group_function == "Select Function"):
        pass
if (selected_group_function == "Assign Groups"):
    if st.sidebar.button("Assign based on current initiatve"):
        data.turn_track = fx.initiative_based_group_assignment(data.turn_track)
    if st.sidebar.button("Remove All Group Assignments"):
        data.turn_track = fx.remove_group_assignments(data.turn_track)
    if st.sidebar.button("Give Everyone their Own Group"):
        data.turn_track = fx.individual_groups(data.turn_track)
elif (selected_group_function == "Move Group"): #TODO
    pass
elif (selected_group_function == "Move Person to Other Group"): #TODO
    pass
elif (selected_group_function == "Disruption"): #TODO should probably put in the combat section because of logging. selects target group, similar code to split stuff below
    pass
elif (selected_group_function == "Merge Groups"): #TODO
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
elif (selected_modification == "Change Group Name"): #TODO
    # select group, new name fields and a button which uses pd's replace
    pass

if show_turn_tracker :
    st.header("Turn Track")
    st.write(data.turn_track[data.turn_track.columns[[
        True, # Always show name
        show_health,
        show_ac,
        show_init, #Initiative
        show_init, #Bonus Init
        show_team,
        show_group,
        show_attributes
    ]]].set_index('name'))