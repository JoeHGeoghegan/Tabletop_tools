# Imports
from inspect import Attribute
import streamlit as st
import pandas as pd
import numpy as np
from dataclasses import dataclass

###############################
########## Functions ##########
###############################
# Function imports
import app_functions as fx


###############################
######## Steamlit Data ########
###############################
@dataclass
class datablock:
    turn_track:pd.DataFrame

    def __init__(self):
        track_headers = ["name","health","armor_class","initiative","initiative_bonus","team","group","attributes"]
        self.turn_track = pd.DataFrame(columns=track_headers)
        self.current_turn = None
        audit_headers = ["source","source_tags","action","recipient","recipient_tags"] 
        self.audit = pd.DataFrame(columns=audit_headers)
        self.audit_actions,self.audit_tags = fx.read_audit("data\default_audit_actions.csv")
        

@st.cache(allow_output_mutation=True)
def setup():
    return datablock()
data = setup()

################################
######## Streamlit Code ########
################################
st.image(".\Images\Villains_turn_logo.png")
tabOverview, tabModifications, tabSettings, tabImportExport = st.tabs(["Overview", "Modifications", "Settings", "Import/Export"])
with tabOverview:
    # TODO Group grouped detections
    if True :
        col_current_turn, col_on_deck, col_turn_controls = st.columns(3)
        with col_current_turn:
            st.write(f"{data.current_turn}'s turn")
            st.write(data.turn_track.loc[data.turn_track['group']==data.current_turn,'name'])
        with col_on_deck:
            next_turn = fx.next_turn(data.turn_track,data.current_turn)
            st.write(f"{next_turn} is on deck")
            st.write(data.turn_track.loc[data.turn_track['group']==next_turn,'name'])
        with col_turn_controls:
            if st.button("Next Turn"):
                data.current_turn = fx.next_turn(data.turn_track,data.current_turn)
    else:
        st.write("Groups are not gathered, move groups to desired order or reset initiative")

    with st.expander("Combat"):
        st.write(fx.character_list)
    # TODO Combat Tree
    # NOTE Actions from audit + Manual checkbox and allow 2 fillable forms, with audit text preview
    # NOTE Trees choices as items are selected "_<XXX>"
    #   NOTE Dynamic? - probably not, would be silly to go multiple layers. And can be done in manual anyway
    # TODO Select attributes to either side
    # TODO display for each audit tag type have
    #TODO disruption (similar UI for splitting and moving)
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
        if enable_audit :
            enable_tags = st.checkbox('Use Combat Tags?',value=True)
with tabImportExport:
    st.header("Importing")
    with st.expander("Click to Open - Import"):
        if st.button("Clear Whole Turn Track",key='import_clear'):
            data.turn_track = data.turn_track[data.turn_track['name'] == None]
        uploaded_files = st.file_uploader("Select Villain's Turn CSV file(s)", accept_multiple_files=True)
        keep_imported_groups = st.checkbox("Keep Imported Groups? (If they exist)",value=True)
        if uploaded_files : # If a single file or more has been added
            if st.button("Add to Turn Track?"):
                for uploaded_file in uploaded_files:
                    data.turn_track = pd.concat([data.turn_track,fx.read_import(uploaded_file,import_groups=keep_imported_groups)])
                if data.current_turn == None :
                    data.current_turn = data.turn_track.iloc[0]['group']
                uploaded_files = None
    st.header("Exporting")
    with st.expander("Click to Open - Export"):
        col_export_all, col_export_team = st.columns(2)
        export_date = st.date_input("Date Tag")
        with col_export_all:
            export_name = st.text_input("Export Name")
            export_file = f"{export_name}_{export_date}.csv"
            st.write(f"File Export Name: {export_file}.")
            st.download_button(
                "Press to Download Complete Turn Track",
                fx.convert_df(data.turn_track),
                export_file,
                "text/csv"
            )
    with col_export_team:
        export_team = st.selectbox("Team to Export",options=fx.team_list(data.turn_track))
        st.write(data.turn_track[data.turn_track["team"]==export_team])
        export_file_team = f"{export_team}_{export_date}.csv"
        st.write(f"File Export Name: {export_file_team}.")
        st.download_button(
            "Press to Download Specific Team",
            fx.convert_df(data.turn_track[data.turn_track["team"]==export_team]),
            export_file_team,
            "text/csv"
    )
with tabModifications:
    selected_modification = st.selectbox(
        "What do you want to Modify",
        options=["Select Function","Add Person","Remove Person/Team","Change Initiatives"]
    )
    st.markdown('---')
    if (selected_modification == "Select Function"):
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
    elif (selected_modification == "Remove Person/Team"):
        selected_character = st.selectbox("Character to Remove",options=fx.character_list(data.turn_track))
        if st.button("Remove Character"):
            data.turn_track = data.turn_track[data.turn_track['name'] != selected_character]
        selected_team = st.selectbox("Team to Remove",options=fx.team_list(data.turn_track))
        if st.button("Remove All Characters on a Team"):
            data.turn_track = data.turn_track[data.turn_track['team'] != selected_team]
        if st.button("Clear Whole Turn Track"):
            data.turn_track = data.turn_track[data.turn_track['name'] == None]
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
                data.turn_track.loc[(data.turn_track['name'] == selected_character,'initiative')]=new_initiative

########## SideBar ##########
selected_group_function = st.sidebar.selectbox(
    "Select Group Functions",
    options=["Select Function","Assign Groups","Move Group","Move Person to Other Group","Merge Groups","Split Group","Change Group Name"]
)
st.sidebar.markdown('---')
if (selected_group_function == "Select Function"):
        pass
if (selected_group_function == "Assign Groups"):
    if st.sidebar.button("Assign based on current initiatve"):
        data.turn_track = fx.initiative_based_group_assignment(data.turn_track)
    if st.sidebar.button("Remove All Group Assignments"):
        data.turn_track = fx.remove_group_assignments(data.turn_track)
    if st.sidebar.button("Give Everyone their Own Group"):
        data.turn_track = fx.individual_groups(data.turn_track)
elif (selected_group_function == "Move Group"):
    group_to_move = st.sidebar.selectbox(
        "Select Group to Move",
        options=fx.groups_list(data.turn_track)
    )
    before_or_after = st.sidebar.select_slider("Before or After",["Before","After"])
    group_to_place = st.sidebar.selectbox(
        f"Choose which group {group_to_move} will move {before_or_after}",
        options=fx.groups_list(data.turn_track)[fx.groups_list(data.turn_track)!=group_to_move]
    )
    if st.sidebar.button("Move"):
        data.turn_track = fx.move_group(data.turn_track,group_to_move,before_or_after,group_to_place)
elif (selected_group_function == "Move Person to Other Group"):
    person_to_move = st.sidebar.selectbox(
        "Select Person to Move",
        options=fx.character_list(data.turn_track)
    )
    use_existing_group = st.sidebar.checkbox("Move to Existing Group?",value=True)
    if use_existing_group:
        destination_group = st.sidebar.selectbox(
            "Group to Add Character to",
            options=fx.groups_list(data.turn_track)
        )
        if st.sidebar.button("Move Character"):
            data.turn_track = fx.move_character(data.turn_track, person_to_move, destination_group)
    else:
        destination_group = st.sidebar.text_input("Group to Add Character to",value="New Group")
        if st.sidebar.button("Move Character to New Group"):
            data.turn_track = fx.move_character_to_new_group(data.turn_track,person_to_move,destination_group)
elif (selected_group_function == "Merge Groups"):
    merge_group_1 = st.sidebar.selectbox(
        "Select Group 1 to Merge",
        options=fx.groups_list(data.turn_track)
    )
    merge_group_2 = st.sidebar.selectbox(
        "Select Group 2 to Merge",
        options=fx.groups_list(data.turn_track)[fx.groups_list(data.turn_track)!=merge_group_1]
    )
    merged_name = st.sidebar.text_input("New Name",value=f"{merge_group_1} and {merge_group_2}")
    if st.sidebar.button("Merge"):
        data.turn_track = fx.merge_groups(data.turn_track,merge_group_1,merge_group_2,merged_name)
        data.turn_track = fx.move_group(data.turn_track,merge_group_1,"After",merge_group_2)
        data.turn_track = data.turn_track.replace(merge_group_2,merged_name,inplace=True)
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
elif (selected_group_function == "Change Group Name"):
    # select group, new name fields and a button which uses pd's replace
    group_to_rename = st.sidebar.selectbox(
        "Select Group to Rename",
        options=fx.groups_list(data.turn_track)
    )
    new_name = st.sidebar.text_input("New Name")
    if st.sidebar.button("Rename Group"):
        data.turn_track.replace(group_to_rename,new_name,inplace=True)

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