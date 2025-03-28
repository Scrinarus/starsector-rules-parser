# Rules.CSV Parser
# Designed to convert the rules.csv file in Starsector into (vaguely) human readable text
# By Scrinarus
# V1.0 - release update - happy 0.98 everyone!

import pandas as pd
text_list = []
rules_line_num_list = []
labels_list = []
option_dict = {}
seperator_line = '-' * 30

# Import the .csv into a Pandas DataFrame
data = pd.read_csv('rules.csv', encoding='ansi')

# Loop through the DataFrame
for row in range(data.shape[0]):
    # Extract the dialog labels with corresponding row numbers
    if type(data.iloc[row, 0]) is str and data.iloc[row, 0][0:2] == '# ':
        appending_tuple = row+2, data.iloc[row, 0][2:]
        labels_list.append(appending_tuple)

    # Extract any text with corresponding line number; skip over any lines with no text (text=nan which is float)
    if type(data.iloc[row, 4]) is str:
        #check if there is a triggering option for text, if not just append it raw
        if (type(data.iloc[row, 2]) is str):
            #check if that triggering option is an actual "option" 
            #(sometimes they can be other things, instead of dialogue)
            if(data.iloc[row, 2][0:7]=='$option'):
                #check if we have the text that causes this option tag to trigger saved to our options dict. If not, just append it raw as sourceless
                #(this obviously isn't ideal, but at the end of the day we are going to miss some cause-effect chains due to the nature of rules.csv)
                if(data.iloc[row, 2].split()[2] in option_dict):
                    #if we do have a source, check if it's part of a multiple option output, this pretty much just standardizes formating.
                    if (option_dict[data.iloc[row, 2].split()[2]][0:9] == "Option(s)"):
                        if (len(data.iloc[row, 2].split()) > 3):
                            text_list.append(f'[Option Selected: {data.iloc[row, 2].split()[2:]}]\n{data.iloc[row, 4]}')
                        else:
                            text_list.append(f'{option_dict[data.iloc[row, 2].split()[2]]}\n{data.iloc[row, 4]}')
                    else:
                        text_list.append(f'[Option Selected: {option_dict[data.iloc[row, 2].split()[2]]}]\n{data.iloc[row, 4]}')
                else:
                    text_list.append(data.iloc[row, 4])
            else:
                text_list.append(data.iloc[row, 4])
        else:
            text_list.append(data.iloc[row, 4])
        #Tracking csv line numbers (offset by 2 due to python list math vs csv list math)
        rules_line_num_list.append(row+2)
    
    #Pulling the column F dialogue options into dictionary
    if (type(data.iloc[row,5]) is str):
        if(":" in data.iloc[row,5]):
            #Display the listed options after any given dialogue
            text_list.append(f'[Options Given: {data.iloc[row,5]}]')
            split_options = data.iloc[row,5].split("\n")
            for option in split_options:
                if (":" in option):
                    #for reasons beyond my understanding, some options are formated #:{tag}:{text}. This handles that edge case.
                    split_entry = option.split(":",2)
                    if (split_entry[0].isdigit()):
                        option_dict[split_entry[1]] = split_entry[2].strip()
                    else:
                        option_dict[split_entry[0]] = split_entry[1].strip()
            #track line number still
            rules_line_num_list.append(row+2)

    #Handling if one particular column F dialogue triggers another flag in column D(e.g. handling branching text)
    if(type(data.iloc[row, 3]) is str and type(data.iloc[row, 2]) is str): 
        if(data.iloc[row, 3][0:7]=='$option' and 'DialogOptionSelected' in data.iloc[row,3].split() and data.iloc[row, 2][0:7]=='$option'):
            #if this a new branch/flag system, add it to the options_dict. 
            #If this isn't new, instead append it to the list of tags that trigger this
            if(data.iloc[row, 3].split()[2] not in option_dict):
                option_dict[data.iloc[row, 3].split()[2]] = f"Option(s) Selected: {data.iloc[row, 2].split()[2:]}"
            else:
                option_dict[data.iloc[row, 3].split()[2]]+=f";{data.iloc[row, 2].split()[2:]}"

# Reformat the whitespace in between each segment of dialog and add line numbers
for i, line in enumerate(text_list):
    new_line = line.replace('\r\n\r\n', '\n')
    new_line = f'[Line {rules_line_num_list[i]}] {new_line}'
    text_list[i] = new_line

# Check to see how many lines of dialog fall under each label
measure_labels = []
for label in range(len(labels_list) - 1):
    lines_in_label = 0
    for line in rules_line_num_list:
        if labels_list[label][0] < line < labels_list[label+1][0]:
            lines_in_label += 1
        if line > labels_list[label+1][0]:
            break
    appending_tuple = label, lines_in_label
    measure_labels.append(appending_tuple)

# Remove any labels that do not have any dialog directly associated with them
max_label = len(labels_list)-1
current_label = 0
while current_label < max_label:
    if measure_labels[current_label][1] == 0:
        labels_list.pop(current_label)
        measure_labels.pop(current_label)
        max_label -= 1
    else:
        current_label += 1
# Old debug option to view every game action in it's own file, not strictly necessary nowadays
# with open('options.txt', 'w') as file:
    #for key in option_dict:
        #file.write(f'{key} : {option_dict[key]}\n')

# Start writing labels and dialog to file in proper order
label_counter, line_counter = 0, 0
label_counter_MAX, line_counter_MAX = len(labels_list), len(rules_line_num_list)
with open('dialogue.txt', 'w') as outfile:
    # Determine if we need to write a label marker or a dialog line
    while line_counter < line_counter_MAX:
        if label_counter == label_counter_MAX:
            break
        if labels_list[label_counter][0] < rules_line_num_list[line_counter]:
            outfile.write('\n'+seperator_line+'\n')
            outfile.write(labels_list[label_counter][1]+'\n')
            outfile.write(seperator_line + '\n')
            if label_counter < label_counter_MAX:
                label_counter += 1
        else:
            outfile.write(f'{text_list[line_counter]}\n\n')
            line_counter += 1
    # Only loop over dialog after the last label has been written
    while line_counter < line_counter_MAX:
        outfile.write(f'{text_list[line_counter]}\n\n')
        line_counter += 1