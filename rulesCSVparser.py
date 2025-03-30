# Rules.CSV Parser
# Designed to convert the rules.csv file in Starsector into (vaguely) human readable text
# By Scrinarus
# V1.1 - new update - descriptions.csv reading added! and cleaned up initial code for more flexibility

import pandas as pd
import os

seperator_line = '-' * 30
header = """===========================================
Scrinarus's Human Parsed CSV's - v1.2
An attempt to make all our rules.csv quotes look a little less terrible.
Proofread somewhat, and descriptions.csv functionality added.
==========================================="""
rules_output = "rules.txt"
desc_output = "desc.txt"

#allows toggling descriptions and rules parsing - mostly for debug, no real reason to not run both
rules_run = False
desc_run = True

# Obtain path of starsector folder
starsector_path = os.path.abspath(os.path.dirname(os.path.dirname( __file__ )))

# if rules parsing is enabled
if (rules_output):
    #list setup
    text_list_rules = []
    num_list_rules = []
    labels_list_rules = []
    option_dict_rules = {}

    # pull rules into Pandas dataframe
    data_rules = pd.read_csv(os.path.join(starsector_path,'starsector-core','data','campaign','rules.csv'), encoding='ansi')
    # Loop through the dataframe for rules.csv
    for row in range(data_rules.shape[0]):
        # Extract the dialog labels with corresponding row numbers
        if type(data_rules.iloc[row, 0]) is str and data_rules.iloc[row, 0][0:2] == '# ':
            appending_tuple = row+2, data_rules.iloc[row, 0][2:]
            labels_list_rules.append(appending_tuple)

        # Extract any text with corresponding line number; skip over any lines with no text (text=nan which is float)
        if type(data_rules.iloc[row, 4]) is str:
            #check if there is a triggering option for text, if not just append it raw
            if (type(data_rules.iloc[row, 2]) is str):
                #check if that triggering option is an actual "option" 
                #(sometimes they can be other things, instead of dialogue)
                if(data_rules.iloc[row, 2][0:7]=='$option'):
                    #check if we have the text that causes this option tag to trigger saved to our options dict. If not, just append it raw as sourceless
                    #(this obviously isn't ideal, but at the end of the day we are going to miss some cause-effect chains due to the nature of rules.csv)
                    if(data_rules.iloc[row, 2].split()[2] in option_dict_rules):
                        #if we do have a source, check if it's part of a multiple option output, this pretty much just standardizes formating.
                        if (option_dict_rules[data_rules.iloc[row, 2].split()[2]][0:9] == "Option(s)"):
                            if (len(data_rules.iloc[row, 2].split()) > 3):
                                text_list_rules.append(f'[Option Selected: {data_rules.iloc[row, 2].split()[2:]}]\n{data_rules.iloc[row, 4]}')
                            else:
                                text_list_rules.append(f'{option_dict_rules[data_rules.iloc[row, 2].split()[2]]}\n{data_rules.iloc[row, 4]}')
                        else:
                            text_list_rules.append(f'[Option Selected: {option_dict_rules[data_rules.iloc[row, 2].split()[2]]}]\n{data_rules.iloc[row, 4]}')
                    else:
                        text_list_rules.append(data_rules.iloc[row, 4])
                else:
                    text_list_rules.append(data_rules.iloc[row, 4])
            else:
                text_list_rules.append(data_rules.iloc[row, 4])
            #Tracking csv line numbers (offset by 2 due to python list math vs csv list math)
            num_list_rules.append(row+2)
        
        #Pulling the column F dialogue options into dictionary
        if (type(data_rules.iloc[row,5]) is str):
            if(":" in data_rules.iloc[row,5]):
                #Display the listed options after any given dialogue
                text_list_rules.append(f'[Options Given: {data_rules.iloc[row,5]}]')
                split_options = data_rules.iloc[row,5].split("\n")
                for option in split_options:
                    if (":" in option):
                        #for reasons beyond my understanding, some options are formated #:{tag}:{text}. This handles that edge case.
                        split_entry = option.split(":",2)
                        if (split_entry[0].isdigit()):
                            option_dict_rules[split_entry[1]] = split_entry[2].strip()
                        else:
                            option_dict_rules[split_entry[0]] = split_entry[1].strip()
                #track line number still
                num_list_rules.append(row+2)

        #Handling if one particular column F dialogue triggers another flag in column D(e.g. handling branching text)
        if(type(data_rules.iloc[row, 3]) is str and type(data_rules.iloc[row, 2]) is str): 
            if(data_rules.iloc[row, 3][0:7]=='$option' and 'DialogOptionSelected' in data_rules.iloc[row,3].split() and data_rules.iloc[row, 2][0:7]=='$option'):
                #if this a new branch/flag system, add it to the options_dict. 
                #If this isn't new, instead append it to the list of tags that trigger this
                if(data_rules.iloc[row, 3].split()[2] not in option_dict_rules):
                    option_dict_rules[data_rules.iloc[row, 3].split()[2]] = f"Option(s) Selected: {data_rules.iloc[row, 2].split()[2:]}"
                else:
                    option_dict_rules[data_rules.iloc[row, 3].split()[2]]+=f";{data_rules.iloc[row, 2].split()[2:]}"

    # Reformat the whitespace in between each segment of dialog and add line numbers - still rules.csv
    for i, line in enumerate(text_list_rules):
        new_line = line.replace('\r\n\r\n', '\n')
        new_line = f'[Line {num_list_rules[i]}] {new_line}'
        text_list_rules[i] = new_line

    # Check to see how many lines of dialog fall under each label - still rules.csv
    measure_labels = []
    for label in range(len(labels_list_rules) - 1):
        lines_in_label = 0
        for line in num_list_rules:
            if labels_list_rules[label][0] < line < labels_list_rules[label+1][0]:
                lines_in_label += 1
            if line > labels_list_rules[label+1][0]:
                break
        appending_tuple = label, lines_in_label
        measure_labels.append(appending_tuple)

    # Remove any labels that do not have any dialog directly associated with them - still rules.csv
    max_label = len(labels_list_rules)-1
    current_label = 0
    while current_label < max_label:
        if measure_labels[current_label][1] == 0:
            labels_list_rules.pop(current_label)
            measure_labels.pop(current_label)
            max_label -= 1
        else:
            current_label += 1
    
    # Start writing labels and dialog to file in proper order
    label_counter, line_counter = 0, 0
    label_counter_MAX, line_counter_MAX = len(labels_list_rules), len(num_list_rules)
    with open(rules_output, 'w') as outfile:
        # Determine if we need to write a label marker or a dialog line
        outfile.write(header)
        while line_counter < line_counter_MAX:
            if label_counter == label_counter_MAX:
                break
            if labels_list_rules[label_counter][0] < num_list_rules[line_counter]:
                outfile.write('\n'+seperator_line+'\n')
                outfile.write(labels_list_rules[label_counter][1]+'\n')
                outfile.write(seperator_line + '\n')
                if label_counter < label_counter_MAX:
                    label_counter += 1
            else:
                outfile.write(f'{text_list_rules[line_counter]}\n\n')
                line_counter += 1
        # Only loop over dialog after the last label has been written
        while line_counter < line_counter_MAX:
            outfile.write(f'{text_list_rules[line_counter]}\n\n')
            line_counter += 1

# descriptions.csv time! This one will be much simpler
if (desc_output):
    #pull descriptions into dataframe
    data_desc = pd.read_csv(os.path.join(starsector_path,'starsector-core','data','strings','descriptions.csv'), encoding='ansi')
    #open output file - we'll do this one live
    with open(desc_output, 'w') as outfile:
        outfile.write(header)
        for row in range(data_desc.shape[0]):
            outfile.write('\n'+seperator_line+'\n')
            outfile.write('[Line {}] '.format(row))
            outfile.write(str(data_desc.iloc[row, 0]) +' '+ str(data_desc.iloc[row, 1]) +'\n')
            #clean up extra whitespace present in the descriptions
            cleaned_desc = str(data_desc.iloc[row, 2]).replace('\r\n\r\n', '\n')
            outfile.write(cleaned_desc)
            
            #some descriptions have additional parts, such ship systems. This just catches them
            i=1
            while(True):
                if (str(data_desc.iloc[row, i+2]) != 'nan'):
                    cleaned_desc_additional = str(data_desc.iloc[row, i+2])
                    outfile.write('\nAdditional {}:\n'.format(i)+cleaned_desc_additional)
                    i+=1
                else:
                    break

            outfile.write('\n'+seperator_line+'\n')


