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

def groups_gathered_check(groups:pd.DataFrame):
    order_list = groups_list(groups)
    team_changes = groups["group"].shift() != groups["group"]
    return len(team_changes[team_changes==True])==len(order_list)

def df_match_slice(df:pd.DataFrame,column,match):
    return df[df[column]==match]

def df_set_match_slice(df:pd.DataFrame,column,match,new_data):
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

def add_audit(audit_trail:pd.DataFrame,turn,source,action,action_number,damage_healing,target,source_add_info,target_add_info,environment):
    audit_trail.loc[len(audit_trail.index)] = [
        turn,
        source,
        action,
        action_number,
        damage_healing,
        target,
        source_add_info,
        target_add_info,
        environment
    ]

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