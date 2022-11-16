# Imports
import pandas as pd
import numpy as np
import random
import ast

def read_import(path,import_groups=True):
    party = pd.read_csv(path)
    if import_groups and ('group' in list(party)):
        return party
    else:
        party = individual_groups(party)
        return party

def read_audit(path):
    audit_read = pd.read_csv(path)

    audit_tags = audit_read[audit_read['Audit Header'].str.contains('tags_')].reset_index(drop=True)
    audit_out = audit_read[audit_read['Audit Header'].str.contains('out_')].reset_index(drop=True)
    audit_meta = audit_read[audit_read['Audit Header'].str.contains('meta_')].reset_index(drop=True)
    
    audit_actions = audit_read.drop(index=audit_read[audit_read['Audit Header'].str.contains('tags_')].index)
    audit_actions = audit_actions.drop(index=audit_read[audit_read['Audit Header'].str.contains('out_')].index)
    audit_actions = audit_actions.drop(index=audit_read[audit_read['Audit Header'].str.contains('meta_')].index)

    audit_actions.reset_index(drop=True,inplace=True)

    audit_tags['Audit Header'] = audit_tags['Audit Header'].str[5:]
    audit_out['Audit Header'] = audit_out['Audit Header'].str[4:]
    audit_meta['Audit Header'] = audit_meta['Audit Header'].str[5:]

    return process_audit(audit_actions), process_audit(audit_out), process_audit(audit_tags), process_audit(audit_meta)

def process_audit(df:pd.DataFrame):
    df = df.set_index("Audit Header").transpose().reset_index(drop=True)
    audit_out = {}
    for col in df.columns : audit_out[col] = df[col].dropna().to_list()
    return audit_out

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def sort_by_initiatives(groups:pd.DataFrame):
    df = groups.copy()
    df['total_initiative'] = df['initiative']+df['initiative_bonus']
    df.sort_values(by='total_initiative',ascending=False,inplace=True)
    return df.drop(columns="total_initiative")

def initiative_based_group_assignment(groups:pd.DataFrame):
    df = sort_by_initiatives(groups)
    df_count = {}
    team_order = df['team']
    group_placement = []
    lastTeam = None
    for team in team_order:
        if team != lastTeam :
            if team in df_count.keys() :
                df_count[team]+=1
            else :
                df_count[team]=1
            lastTeam = team
        group_placement.append(f"{team} {df_count[team]}")
    df['group']=group_placement
    return df

def roll(sided=20):
    return random.randint(1,sided)

def auto_initiative(groups:pd.DataFrame):
    df = groups.copy()
    df['initiative'] = df['initiative'].apply(lambda x: roll(20))
    return df

def groups_list(turn_track:pd.DataFrame):
    return(turn_track['group'].unique())

def character_list(turn_track:pd.DataFrame):
    return(turn_track['name'].unique())

def team_list(turn_track:pd.DataFrame):
    return(turn_track['team'].unique())

def person_is_alone(groups:pd.DataFrame,person):
    group_name = groups[groups['name'] == person]['group'].values[0]
    return len(groups[groups['group']==group_name]) == 1

def multi_person_groups_list(groups):
    multi_person_groups_mask = [len(groups[groups['group']==x]) != 1 for x in groups['group'].unique()]
    multi_person_groups = groups['group'].unique()[multi_person_groups_mask]
    return multi_person_groups

def groups_gathered_check(groups:pd.DataFrame):
    order_list = groups_list(groups)
    team_changes = groups["group"].shift() != groups["group"]
    return len(team_changes[team_changes==True])==len(order_list)

def df_match_slice(df:pd.DataFrame,column,match):
    return df[df[column]==match]

def df_set_slice(df:pd.DataFrame,column,match,new_data):
    df_slice = df[df[column] == match].copy()
    df_slice[column] = new_data
    df_copy = df.copy()
    df_copy.update(df_slice)
    return df_copy

def remove_group_assignments(groups:pd.DataFrame):
    df = groups.copy()
    df['group']=np.nan
    return df

def individual_groups(groups:pd.DataFrame):
    df = groups.copy()
    df['group']=df['name']
    return df

def move_group(groups:pd.DataFrame,group_to_move,before_or_after,group_to_place):
    df = groups.copy()
    df.reset_index(drop=True,inplace=True)
    slice_group_to_move = df[df['group']==group_to_move].copy()
    df.drop(slice_group_to_move.index,inplace=True)
    df.reset_index(drop=True,inplace=True)
    slice_group_to_move.reset_index(drop=True,inplace=True)
    if before_or_after == "Before" :
        index_split_point = (df[df['group']==group_to_place].index[0]) #first index
    else :
        index_split_point = df[df['group']==group_to_place].index[-1]+1 #last index
    return pd.concat([df.iloc[:index_split_point],slice_group_to_move,df.iloc[index_split_point:]]).reset_index(drop=True)

def move_character(groups:pd.DataFrame,person_to_move,destination_group):
    df = groups.copy()
    df.reset_index(drop=True,inplace=True)
    slice_character_to_move = df[df['name']==person_to_move].copy()
    slice_character_to_move['group']=destination_group
    df.drop(slice_character_to_move.index,inplace=True)
    index_split_point = df[df['group']==destination_group].index[-1] #last index
    return pd.concat([df.iloc[:index_split_point],slice_character_to_move,df.iloc[index_split_point:]]).reset_index(drop=True)

def move_character_to_new_group(groups:pd.DataFrame,person_to_move,new_group_name):
    df = groups.copy()
    old_group=df.loc[(df["name"]==person_to_move,"group")].values[0]
    df.loc[(df["name"]==person_to_move,"group")]=new_group_name
    if df[df['group']==old_group].empty :
        return df # If character was the only member of a group, no need to rearrange
    return move_group(df,new_group_name,"After",old_group)

def merge_groups(groups:pd.DataFrame,merge_group_1,merge_group_2,merged_name):
    df = groups.copy()
    df = move_group(df,merge_group_1,"After",merge_group_2)
    df['group'].replace([merge_group_1,merge_group_2],[merged_name,merged_name],inplace=True)
    return df

def next_turn(groups:pd.DataFrame,current_turn):
    groups.reset_index(drop=True,inplace=True)
    current_turns_last_index=groups[groups['group']==current_turn].index[-1]
    if current_turns_last_index == len(groups)-1 : #loop around detection
        return groups.iloc[0]['group']
    else:
        return groups.iloc[current_turns_last_index+1]['group']

def previous_turn(groups:pd.DataFrame,current_turn):
    groups.reset_index(drop=True,inplace=True)
    current_turns_last_index=groups[groups['group']==current_turn].index[0]
    if current_turns_last_index == 0 : #loop around detection
        return groups.iloc[-1]['group']
    else:
        return groups.iloc[current_turns_last_index-1]['group']

def attributes_list(groups:pd.DataFrame):
    df = groups[['name','attributes']].copy()
    df.dropna(inplace=True)
    all_attributes = []
    for index,character in df.iterrows():
        character_attributes = ast.literal_eval(character['attributes'])
        for key, values in character_attributes.items() :
            if type(values) == list :
                for item in values:
                    all_attributes.append(f"{character['name']} - {key} - {item}")
            else :
                all_attributes.append(f"{character['name']} - {key} - {values}")
    return all_attributes

def add_audit(audit_trail:pd.DataFrame,turn,action_number,source,action,result,target,source_additional_info,target_additional_info,environment,damage,healing,additional_effects):
    audit_trail.loc[len(audit_trail.index)] = [
        turn, action_number,
        source,
        action,
        result,
        target,
        source_additional_info,
        target_additional_info,
        environment,
        damage,
        healing,
        additional_effects
    ]

def add_audit_note(audit_trail:pd.DataFrame,turn,action_number,note):
    add_audit(audit_trail,turn,action_number,"","","","","","","","","",note)
def add_audit_character_note(audit_trail:pd.DataFrame,turn,action_number,character,note):
    add_audit(audit_trail,turn,action_number,character,"","","","","","","","",note)

def parse_meta_str(meta):
    meta_list = meta.strip('][').split(',')
    output = {}
    output["target"] = meta_list[1]
    output["modification"] = meta_list[2]
    output["wording"] = meta_list[3]
    return meta_list[0],output

def meta_to_dict(audit_meta,key='Results'):
    output = {}
    for meta in audit_meta[key]:
        parse_name, parse_dict = parse_meta_str(meta)
        output[parse_name] = parse_dict
    return output

def has_meta(result,meta_lookup:dict):
    return result in meta_lookup.keys()

def submit_action(turn_track,current_turn,results_data,additional_log):
    damage = []
    healing = []
    for result in results_data:
        if result[0] in ['+','-'] : adjust_health(turn_track,result[0],result[1],result[2])
        elif result[0] in ['attribute','condition','info'] :
            if additional_log != "" : additional_log += '\n'
            additional_log += add_additional_info(result)
        elif result[0] == 'disrupt' :
            if len(turn_track[turn_track['group']==current_turn]) == 1 : 
                current_turn = next_turn(turn_track,current_turn)
            turn_track = disrupt(turn_track,result[1],result[2])

        if result[0] == '-' : damage.append([result[1],result[2]])
        elif result[0] == '+' : healing.append([result[1],result[2]])
    return turn_track, current_turn, additional_log, damage, healing

def adjust_health(turn_track,is_damage,numbers,target):
    health_mod = 1
    if is_damage == "-" : health_mod = -1
    for number in numbers :
        value = number[1]
        turn_track.loc[turn_track['name'].isin(target),'health'] += (health_mod * value)

def add_additional_info(result):
    return f'{result[0]} -> {result[2]} : {result[1]}'

def disrupt(turn_track,disruptor,disrupted_info):
    print(disrupted_info)
    group_to_split = disrupted_info[0]
    group_name_1 = disrupted_info[1]
    split_decicions = disrupted_info[2]
    group_name_2 = disrupted_info[3]
    turn_track = df_set_slice(turn_track,"group",group_to_split,split_decicions)
    if not person_is_alone(turn_track,disruptor) :
        turn_track = move_character_to_new_group(turn_track, disruptor, disruptor)
    else :
        turn_track.loc[turn_track['name']==disruptor,'group']=disruptor
    turn_track = move_group(turn_track,disruptor,"After",group_name_1)
    turn_track = move_group(turn_track,group_name_2,"After",disruptor)
    return turn_track

def split_column_list(df,column_name,new_axis_names):
    df[new_axis_names] = pd.DataFrame(df[column_name].to_list(),index=df.index)
    df.drop(columns=column_name,inplace=True)

def col_str_every_action(df,column_name,drop_cols):
    df_split = df.copy()
    df_split.drop(df_split[df_split[column_name]==''].index,inplace=True)
    df_split.drop(columns=drop_cols,inplace=True)
    df_split['additional_effects'] = df_split['additional_effects'].str.split('\n')
    df_split = df_split.explode('additional_effects').reset_index(drop=True)
    df_split.drop(df_split[df_split[column_name]==''].index,inplace=True)
    return df_split

def split_column_list(df,column_name,new_axis_names):
    df_split = df.copy()
    df_split.drop(df[df[column_name].isin(["",[]])].index,inplace=True)
    df_split[new_axis_names] = pd.DataFrame(df_split[column_name].to_list(),columns=new_axis_names,index=df_split.index)
    df_split.drop(columns=column_name,inplace=True)
    return df_split

def col_list_every_action(df,column_name,drop_cols):
    df_split = df.explode(column_name)
    df_split.dropna(inplace=True)
    df_split.drop(columns=drop_cols,inplace=True)
    df_split = split_column_list(df_split,column_name,['sources','target'])
    df_split = df_split.explode('sources')
    df_split = split_column_list(df_split,'sources',['source',column_name])
    return df_split

def audit_every_action_df(audit:pd.DataFrame):
    action_df = audit.copy()[["turn","action_number","damage","healing","additional_effects"]]
    concat_list = []
    if not all(action_df['damage'].isin(["",[]])) : concat_list.append(col_list_every_action(action_df,'damage',['healing','additional_effects']))
    if not all(action_df['healing'].isin(["",[]])) : concat_list.append(col_list_every_action(action_df,'healing',['damage','additional_effects']))
    if not all(action_df['additional_effects'].isin(["",[]])) : concat_list.append(col_str_every_action(action_df,'additional_effects',['damage','healing']))
    
    if len(concat_list) : return pd.concat(concat_list,ignore_index=True).sort_values(by=["turn","action_number"])
    return pd.DataFrame(columns=['turn','action_number','source','damage','healing','additional_effects'])