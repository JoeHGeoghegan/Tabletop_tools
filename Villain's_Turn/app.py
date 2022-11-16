# Imports
import streamlit as st
from streamlit import session_state as ss
import pandas as pd
from dataclasses import dataclass
from streamlit_autorefresh import st_autorefresh

###############################
########## Functions ##########
###############################
# Function imports
import app_functions as fx
###############################
######## Steamlit Data ########
###############################
st.set_page_config(page_title="Villain's Turn", page_icon="🦹",layout="wide")
@dataclass
class datablock:
    def __init__(self):
        track_headers = ["name","health","armor_class","initiative","initiative_bonus","team","group","attributes"]
        ss.turn_track = pd.DataFrame(columns=track_headers)
        ss.current_turn = None
        audit_headers = ["turn","action_number","source","action","result","target","source_additional_info","target_additional_info","environment","damage","healing","additional_effects"]
        ss.audit = pd.DataFrame(columns=audit_headers)
        ss.audit_actions,ss.audit_outcome, ss.audit_tags, ss.audit_meta = fx.read_audit("data\default_audit_actions.csv")
        ss.meta_lookup = fx.meta_to_dict(ss.audit_meta)
        ss.turn_number = 0
        ss.action_number = 0
        ss.results_data = []
        ss.audit_combat = True
        ss.audit_changes = True
        ss.count = 0
    def set_audit(self, path):
        ss.audit_actions,ss.audit_outcome, ss.audit_tags, ss.audit_meta = fx.read_audit(path)

@st.cache(allow_output_mutation=True)
def setup():
    return datablock()
data = setup()
################################
######## Streamlit Code ########
################################
ss.count = st_autorefresh(interval=1000, key="runtime_counter")
col_image, col_refresh = st.columns(2)
with col_image:
    st.image(".\Images\Villains_turn_logo.png")
with col_refresh:
    # st.write(f'Runtime: {int(ss.count/60)} minutes {ss.count%60} seconds')
    st.write(f'Turn #: {ss.turn_number}')
    st.write(f'Action #: {ss.action_number}')
tabOverview, tabModifications, tabSettings, tabImportExport = st.tabs(["Overview", "Modifications", "Settings", "Import/Export"])
with tabOverview:
    # Checks to ensure data is able to be displayed
    if len(ss.turn_track) == 0:
        st.write("Welcome! Add Characters in the Modifications tab or Import an exisiting Villain's Turn csv to get started!")
    elif not fx.groups_gathered_check(ss.turn_track) :
        st.write("Groups are not gathered, move groups to desired order or reset initiative")
    else :
        # Turn tracking start up
        if ss.current_turn==None or not (ss.current_turn in fx.groups_list(ss.turn_track)):
            ss.current_turn = ss.turn_track.iloc[0]['group']
        current_group = ss.turn_track.loc[ss.turn_track['group']==ss.current_turn]

        # Turn Track displays
        col_current_turn, col_on_deck, col_turn_controls = st.columns(3)
        with col_current_turn:
            st.write(f"{ss.current_turn}'s turn")
            st.write(current_group['name'])
        with col_on_deck:
            next_turn = fx.next_turn(ss.turn_track,ss.current_turn)
            st.write(f"{next_turn} is on deck")
            st.write(ss.turn_track.loc[ss.turn_track['group']==next_turn,'name'])
        with col_turn_controls:
            if st.button("Next Turn"):
                ss.current_turn = next_turn
                ss.turn_number += 1
            if st.button("Previous Turn"):
                ss.current_turn = fx.previous_turn(ss.turn_track,ss.current_turn)
                ss.turn_number -= 1
            turn_jump = st.selectbox("Jump to Turn",options=fx.groups_list(ss.turn_track))
            if st.button("Jump to Turn"):
                ss.current_turn = turn_jump
                ss.turn_number = 0
        
        # Combat Interface
        # Would be nice to do this with a form but forms stop the internal widgets from being modified
        if st.checkbox("Show Combat Entry - Toggle to clear values"):
            st.markdown("---")
            col_actors, col_action, col_target,col_execute = st.columns(4)
            # Active Character
            with col_actors:
                attribute_select_active_characters = []
                if st.checkbox("Are there active characters?",value=True):
                    # Single/Multi Character Handling
                    if len(ss.turn_track.loc[ss.turn_track['group']==ss.current_turn,'name']) > 1 :
                        active_characters = st.multiselect("Active Character(s)", options=ss.turn_track.loc[ss.turn_track['group']==ss.current_turn,'name'])
                    elif len(ss.turn_track.loc[ss.turn_track['group']==ss.current_turn,'name']) == 1  :
                        active_characters = [ss.turn_track.loc[ss.turn_track['group']==ss.current_turn,'name'].values[0]]
                    else : # Error catch, "should" never happen
                        st.write("It is no one's turn!")
                    # Attribute specifications
                    if st.checkbox("Specify Attributes?",key="active_characters_specify"):
                        attribute_select_active_characters = st.multiselect("Select Attributes",
                            options = fx.attributes_list(current_group[current_group['name'].isin(active_characters)])
                        )
                else :
                    active_characters = st.text_area(f'What is causing the action?')
            # Action
            with col_action:
                if st.checkbox("Standard Action",value=True):
                    action_subject = st.selectbox("Action Type", options=ss.audit_actions.keys())
                    action = st.multiselect(f"{action_subject} Submenu", options=ss.audit_actions[action_subject])
                else :
                    action = st.text_area('What occured?')
            # Target Character
            with col_target:
                attribute_select_target_characters = []
                if st.checkbox("Are there target characters?",value=True):
                    # Multi Character Handling Only
                    target_characters = st.multiselect("Target Character(s)", options=ss.turn_track['name'])
                    # Attribute specifications
                    if st.checkbox("Specify Attributes?",key="target_characters_specify"):
                        attribute_select_target_characters = st.multiselect("Select Attributes",
                            options = fx.attributes_list(ss.turn_track[ss.turn_track['name'].isin(target_characters)])
                        )
                else :
                    target_characters = st.text_area(f'What occured with the {action}')
            with col_execute:
                attribute_environment = st.selectbox("Environment Information", options=ss.audit_tags['Environment'])
                outcome = st.selectbox("Outcome",options=ss.audit_outcome['Outcome'])
                results = st.multiselect("Result",options=ss.audit_outcome['Results'])
                # Writes list of confirmed actions
                st.write(f'Confirmed Actions: {ss.results_data}')
                if st.button("Submit Action"):
                    # creates an additional log, submits action and adds to audit
                    additional_log = ""
                    ss.turn_track, ss.current_turn, additional_log, damage, healing = fx.submit_action(ss.turn_track,ss.current_turn,ss.results_data,additional_log)
                    if ss.audit_combat : fx.add_audit(ss.audit,
                        ss.turn_number,ss.action_number, # turn, action_number
                        active_characters, # source
                        action, # action
                        results, # result
                        target_characters, # target
                        attribute_select_active_characters, # source_additional_info
                        attribute_select_target_characters, # target_additional_info
                        attribute_environment, # environment
                        damage, # damage
                        healing, # healing
                        additional_log # additional_effects
                        )
                    ss.results_data = []
                    ss.action_number += 1
            st.markdown("---")
            # Dynamic Meta Data handling
            if results != None :
                for result in results :
                    st.markdown(f"### {result}")
                    col_result_data, col_result_target = st.columns(2)
                    if fx.has_meta(result,ss.meta_lookup):
                        meta = ss.meta_lookup[result]
                        with col_result_data:
                            # Fills mod_data with correct input depending on need
                            mod_data = st.empty()
                            if meta["modification"] in ['-','+']:
                                mod_data = []
                                mod_characters = st.multiselect(f"Characters {result}",options=active_characters,key=f'data_characters_{result}')
                                for character in mod_characters:
                                    mod_data.append([character,st.number_input(f'{character} {result}',value=0,key=f'data_number_{character}_{result}')])
                            elif meta["modification"] == 'attribute':
                                mod_data = st.multiselect(f'Attribute {meta["wording"]}',options=attribute_select_active_characters,key=f'data_attribute_{result}')
                            elif meta["modification"] == 'condition':
                                mod_data = st.multiselect(f'Condition {meta["wording"]}',options=ss.audit_tags['Condition'],key=f'data_condition_{result}')
                            elif meta["modification"] == 'info':
                                mod_data = st.text_area(meta["wording"],key=f'data_info_{result}')
                            elif meta["modification"] == 'disrupt':
                                mod_data = st.selectbox("Who is Disrupting (can only be one)",options=active_characters,key=f'data_disrupt_{result}')
                        with col_result_target:
                            # Fills target_data with correct input depending on need
                            target_data = st.empty()
                            if meta["target"] == 'self' : target_data = active_characters
                            elif meta["target"] == 'target':
                                if type(active_characters)==str : targets = target_characters
                                elif type(target_characters)==str : targets = active_characters
                                else : targets = active_characters + target_characters
                                target_data = st.multiselect("Specific Target(s)",options=targets,key=f'target_specifics_{result}')
                            elif (meta["target"] == 'target_group') and (meta["modification"] == 'disrupt'):
                                # Disrupt handling
                                action_group_to_split = st.selectbox("Select Group to Disrupt",
                                                            options=fx.multi_person_groups_list(ss.turn_track),
                                                            key=f'target_group_{result}')
                                if(action_group_to_split!=None):
                                    action_group_to_split_1st = st.text_input("First Half Name",value=f"{action_group_to_split} 1",key=f'target_name1_{result}')
                                    action_group_to_split_2nd = st.text_input("Second Half Name",value=f"{action_group_to_split} 2",key=f'target_name2_{result}')
                                    action_group_to_split_df = fx.df_match_slice(ss.turn_track,"group",action_group_to_split)
                                    action_split_decicions = []
                                    st.write("Where is:")
                                    for member in action_group_to_split_df['name']:
                                        action_split_decicions.append(st.select_slider(member,
                                            options=[action_group_to_split_1st,action_group_to_split_2nd],key=f'target_{member}_{result}'
                                        ))
                                target_data = [action_group_to_split,action_group_to_split_1st,action_split_decicions,action_group_to_split_2nd]
                            elif (meta["target"] == 'target_group'):
                                # Target group handling
                                target_data = st.selectbox("Select Group",options=fx.groups_list(ss.turn_track),key=f'target_group_{result}')
                            if st.button(f"Confirm Result - {result}"):
                                ss.results_data.append([
                                    meta["modification"],
                                    mod_data,
                                    target_data
                                ])
                        st.markdown("---")
with tabSettings:
    with st.expander("Turn Tracker Visuals"):
        # Modify settings to change what is shown
        resize_turn_tracker = 1
        show_turn_tracker = st.checkbox('Show Turn Tracker',value=True)
        if show_turn_tracker:
            show_health = st.checkbox('Show Health')
            show_ac = st.checkbox('Show Armor Class')
            show_init = st.checkbox('Show Initiative',value=True)
            show_team = st.checkbox('Show Teams',value=True)
            show_group = st.checkbox('Show Combat Groups',value=True)
            show_attributes = st.checkbox('Show Additional Attributes')
    with st.expander("Audit Settings"):
        # What to Audit
        ss.audit_combat = st.checkbox('Audit Combat',value=True)
        ss.audit_changes = st.checkbox('Audit Turn Track Changes',value=True)
        # Audit downloads/settings
        st.download_button(
            "Press to Download Default Action Configuration",
            fx.convert_df(pd.read_csv(".\data\default_audit_actions.csv")),
            "default_audit_actions.csv",
            "text/csv"
        )
        st.download_button(
            "Export Audit",
            fx.convert_df(ss.audit),
            f"audit_{str(pd.Timestamp.today().date())}.csv",
            "text/csv"
        )
        st.download_button(
            "Export Every Action Result as its own Row",
            fx.convert_df(fx.audit_every_action_df(ss.audit)),
            f"audit_every_action_{str(pd.Timestamp.today().date())}.csv",
            "text/csv"
        )
        new_configuration = st.file_uploader("Upload Custom Action Configuration", accept_multiple_files=False)
        if new_configuration != None :
            if st.button("Switch Configuration"): ss.set_audit(new_configuration)
        if st.button("Show Current Audit Trail"):
            st.write(ss.audit.set_index('turn'))
        # enable_audit = st.checkbox('Enable Audit',value=True)
with tabImportExport:
    st.header("Importing")
    with st.expander("Click to Open - Import"):
        if st.button("Load Example"):
            ss.turn_track = pd.concat([ss.turn_track,fx.read_import("Test_Files&Notebooks\Party2.csv")])
            resize_turn_tracker = 0
        st.download_button(
            "Download Example CSV",
            fx.convert_df(fx.read_import("Test_Files&Notebooks\Party2.csv")),
            "Example_Turn_Track.csv",
            "text/csv"
        )
        if st.button("Clear Whole Turn Track",key='import_clear'):
            ss.turn_track = ss.turn_track[ss.turn_track['name'] == None]
        uploaded_files = st.file_uploader("Select Villain's Turn CSV file(s)", accept_multiple_files=True)
        keep_imported_groups = st.checkbox("Keep Imported Groups? (If they exist)",value=True)
        if uploaded_files : # If a single file or more has been added
            if st.button("Add to Turn Track?"):
                for uploaded_file in uploaded_files:
                    ss.turn_track = pd.concat([ss.turn_track,fx.read_import(uploaded_file,import_groups=keep_imported_groups)])
                if ss.current_turn == None :
                    ss.current_turn = ss.turn_track.iloc[0]['group']
                uploaded_files = None
                resize_turn_tracker = 0
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
                fx.convert_df(ss.turn_track),
                export_file,
                "text/csv"
            )
    with col_export_team:
        export_team = st.selectbox("Team to Export",options=fx.team_list(ss.turn_track))
        st.write(ss.turn_track[ss.turn_track["team"]==export_team])
        export_file_team = f"{export_team}_{export_date}.csv"
        st.write(f"File Export Name: {export_file_team}.")
        st.download_button(
            "Press to Download Specific Team",
            fx.convert_df(ss.turn_track[ss.turn_track["team"]==export_team]),
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
            ss.turn_track=ss.turn_track.append(character,ignore_index=True)
            if ss.audit_changes : fx.add_audit(ss.audit,ss.turn_number,ss.action_number,
                newPerson_name,
                f"Entered the Turn Order\nHP:{newPerson_hp}, AC:{newPerson_ac}, init_bonus:{newPerson_b_init}, team:{newPerson_team}, group:{newPerson_group}")
    elif (selected_modification == "Remove Person/Team"):
        selected_character = st.selectbox("Character to Remove",options=fx.character_list(ss.turn_track))
        if st.button("Remove Character"):
            ss.turn_track = ss.turn_track[ss.turn_track['name'] != selected_character]
            if ss.audit_changes : fx.add_audit_character_note(ss.audit,ss.turn_number,ss.action_number,
                selected_character,"Left the Turn Order")
        selected_team = st.selectbox("Team to Remove",options=fx.team_list(ss.turn_track))
        if st.button("Remove All Characters on a Team"):
            ss.turn_track = ss.turn_track[ss.turn_track['team'] != selected_team]
            if ss.audit_changes : fx.add_audit_character_note(ss.audit,ss.turn_number,ss.action_number,
                f'The Team {selected_team}',"Left the Turn Order")
        if st.button("Clear Whole Turn Track"):
            ss.turn_track = ss.turn_track[ss.turn_track['name'] == None]
            if ss.audit_changes : fx.add_audit_note(ss.audit,ss.turn_number,ss.action_number,"Turn Track Cleared")
    elif (selected_modification == "Change Initiatives"):
        col_init_random, col_init_sort = st.columns(2)
        with col_init_random:
            if st.button("Auto Reroll all Initiatives?"):
                ss.turn_track = fx.auto_initiative(ss.turn_track)
                if ss.audit_changes : fx.add_audit_note(ss.audit,ss.turn_number,ss.action_number,"All Initiatives Randomized")
        with col_init_sort:
            if st.button("Sort Initiatives"):
                ss.turn_track = fx.sort_by_initiatives(ss.turn_track)
                ss.turn_track = fx.individual_groups(ss.turn_track)
                if ss.audit_changes : fx.add_audit_note(ss.audit,ss.turn_number,ss.action_number,"Sorted by Initiatives")
        # select person, initiative field, and a button
        with st.expander("Manually Set/Change Initiatives"):
            selected_character = st.selectbox("Character",options=fx.character_list(ss.turn_track))
            new_initiative = st.number_input("New Initiative",value = 1)
            if st.button("Set Initiative"):
                ss.turn_track.loc[(ss.turn_track['name'] == selected_character,'initiative')]=new_initiative
                if ss.audit_changes : fx.add_audit_character_note(ss.audit,ss.turn_number,ss.action_number,
                    selected_character,f"Initiative was set to {new_initiative}")
########## SideBar ##########
selected_group_function = st.sidebar.selectbox(
    "Select Group Functions",
    options=["Select Function","Assign Groups","Move Group","Move Person to Other Group","Merge Groups","Split Group","Change Group Name"]
)
st.sidebar.markdown('---')
if (selected_group_function == "Select Function"):
        pass
if (selected_group_function == "Assign Groups"):
    if st.sidebar.button("Assign based on current initiative"):
        ss.turn_track = fx.initiative_based_group_assignment(ss.turn_track)
        if ss.audit_changes : fx.add_audit_note(ss.audit,ss.turn_number,ss.action_number,"Groups created based on Team/Initiative")
    if st.sidebar.button("Assign based on new initiative"):
        ss.turn_track = fx.auto_initiative(ss.turn_track)
        ss.turn_track = fx.initiative_based_group_assignment(ss.turn_track)
        if ss.audit_changes : fx.add_audit_note(ss.audit,ss.turn_number,ss.action_number,"Groups created based on Team/New Initiative")
    if st.sidebar.button("Remove All Group Assignments"):
        ss.turn_track = fx.remove_group_assignments(ss.turn_track)
        if ss.audit_changes : fx.add_audit_note(ss.audit,ss.turn_number,ss.action_number,"Groups Removed")
    if st.sidebar.button("Give Everyone their Own Group"):
        ss.turn_track = fx.individual_groups(ss.turn_track)
        if ss.audit_changes : fx.add_audit_note(ss.audit,ss.turn_number,ss.action_number,"Every character is in their own group")
elif (selected_group_function == "Move Group"):
    group_to_move = st.sidebar.selectbox(
        "Select Group to Move",
        options=fx.groups_list(ss.turn_track)
    )
    before_or_after = st.sidebar.select_slider("Before or After",["Before","After"])
    group_to_place = st.sidebar.selectbox(
        f"Choose which group {group_to_move} will move {before_or_after}",
        options=fx.groups_list(ss.turn_track)[fx.groups_list(ss.turn_track)!=group_to_move]
    )
    if st.sidebar.button("Move"):
        if ss.current_turn != None : ss.current_turn = fx.next_turn(ss.turn_track,ss.current_turn)
        ss.turn_track = fx.move_group(ss.turn_track,group_to_move,before_or_after,group_to_place)
        if ss.audit_changes : fx.add_audit_character_note(ss.audit,ss.turn_number,ss.action_number,
        group_to_move,f'Moved to {before_or_after} {group_to_place}')
elif (selected_group_function == "Move Person to Other Group"):
    person_to_move = st.sidebar.selectbox(
        "Select Person to Move",
        options=fx.character_list(ss.turn_track)
    )
    if st.sidebar.checkbox("Move to Existing Group?",value=True):
        destination_group = st.sidebar.selectbox(
            "Group to Add Character to",
            options=fx.groups_list(ss.turn_track)
        )
        if st.sidebar.button("Move Character"):
            ss.turn_track = fx.move_character(ss.turn_track, person_to_move, destination_group)
            if ss.audit_changes : fx.add_audit_character_note(ss.audit,ss.turn_number,ss.action_number,
                person_to_move,f'Added to {destination_group}')
    else:
        destination_group = st.sidebar.text_input("Group to Add Character to",value="New Group")
        if st.sidebar.button("Move Character to New Group"):
            ss.turn_track = fx.move_character_to_new_group(ss.turn_track,person_to_move,destination_group)
            if ss.audit_changes : fx.add_audit_character_note(ss.audit,ss.turn_number,ss.action_number,
                person_to_move,f'Added to new group: {destination_group}')
elif (selected_group_function == "Merge Groups"):
    merge_group_1 = st.sidebar.selectbox(
        "Select Group 1 to Merge",
        options=fx.groups_list(ss.turn_track)
    )
    merge_group_2 = st.sidebar.selectbox(
        "Select Group 2 to Merge",
        options=fx.groups_list(ss.turn_track)[fx.groups_list(ss.turn_track)!=merge_group_1]
    )
    merged_name = st.sidebar.text_input("New Name",value=f"{merge_group_1} and {merge_group_2}")
    if st.sidebar.button("Merge"):
        if ss.current_turn != None : ss.current_turn = fx.next_turn(ss.turn_track,ss.current_turn)
        ss.turn_track = fx.merge_groups(ss.turn_track,merge_group_1,merge_group_2,merged_name)
        ss.turn_track.replace(merge_group_2,merged_name,inplace=True)
        if ss.audit_changes : fx.add_audit_character_note(ss.audit,ss.turn_number,ss.action_number,
                f'{merge_group_1}, {merge_group_2}',f'Merged. New Name: {merged_name}')
elif (selected_group_function == "Split Group"):
    group_to_split = st.sidebar.selectbox(
        "Select Group to Split",
        options=fx.multi_person_groups_list(ss.turn_track)
    )
    if(group_to_split!=None):
        group_to_split_1st = st.sidebar.text_input("First Half Name",value=f"{group_to_split} 1")
        group_to_split_2nd = st.sidebar.text_input("Second Half Name",value=f"{group_to_split} 2")
        group_to_split_df = fx.df_match_slice(ss.turn_track,"group",group_to_split)
        st.sidebar.write("Selected Group:")
        st.sidebar.write(group_to_split_df)
        split_decicions = []
        st.sidebar.write("Where is:")
        for member in group_to_split_df['name']:
            split_decicions.append(st.sidebar.select_slider(member,options=[group_to_split_1st,group_to_split_2nd]))
        if st.sidebar.button("Split") :
            ss.turn_track = fx.df_set_slice(ss.turn_track,"group",group_to_split,split_decicions)
            if ss.audit_changes : fx.add_audit_character_note(ss.audit,ss.turn_number,ss.action_number,
                group_to_split,f'Split. New Groups: {group_to_split_1st} and {group_to_split_2nd}')
elif (selected_group_function == "Change Group Name"):
    # select group, new name fields and a button which uses pd's replace
    group_to_rename = st.sidebar.selectbox("Select Group to Rename",options=fx.groups_list(ss.turn_track))
    new_name = st.sidebar.text_input("New Name")
    if st.sidebar.button("Rename Group"):
        ss.turn_track.replace(group_to_rename,new_name,inplace=True)
        if ss.audit_changes : fx.add_audit_character_note(ss.audit,ss.turn_number,ss.action_number,
            group_to_rename,f'Renamed. New Name: {new_name}')

if resize_turn_tracker and show_turn_tracker :
    st.header("Turn Track")
    st.write(ss.turn_track[ss.turn_track.columns[[
        True, # Always show name
        show_health,
        show_ac,
        show_init, #Initiative
        show_init, #Bonus Init
        show_team,
        show_group,
        show_attributes
    ]]].set_index('name'))
elif resize_turn_tracker == 0 :
    resize_turn_tracker = 1