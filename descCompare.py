# Rules.CSV Parser
# Designed to convert the rules.csv file in Starsector into (vaguely) human readable text
# By Scrinarus
# V1.2 - new update - created a new separate script to run comparisons between codex versions! Also set both flags in this parser to true by default.

#Authors note - currently the file and variable names are set with the understanding that we are comparing .97 and .98.
#However, all this logic should work perfectly fine for minor update versions into the future.
#Just gotta tweak the names of the files you want to open, the logic will do the rest.

#Authors note P2 - literally as I prep to push this to the repo, Alex drops RC6. Hilarious. Alright, we'll make sure this works.

#list of keywords for later
desc97Dict = {}
desc98Dict = {}
#open file
with open("desc97.txt", 'r') as desc97:
    #use my own line breaks
    list97 = desc97.read().split(('-' * 30))
    prune = []

    #kill anything too short (various useless characters, no description in the game is this short by default)
    for line in list97:
        if len(line) <25:
            prune.append(line)
    for line in prune:
        list97.remove(line)

    #strip extra whitespace
    list97 = list(map(str.strip, list97))
    for i in range(len(list97)):
        list97[i]=list97[i].split(' ',2)[-1]
    
    #strip line numbers for ability to compare by tag
    for i in range(len(list97)):
        line = list97[i].split(' ',1)
        desc97Dict[line[0]] = line[-1].split('\n',1)[-1]

#do the exact same as above for the second file
with open("desc98.txt", 'r') as desc98:
    #use my own line breaks
    list98 = desc98.read().split(('-' * 30))
    prune = []

    #kill anything too short (various useless characters, no description in the game is this short by default)
    for line in list98:
        if len(line) <25:
            prune.append(line)
    for line in prune:
        list98.remove(line)

    #strip extra whitespace
    list98 = list(map(str.strip, list98))
    for i in range(len(list98)):
        list98[i]=list98[i].split(' ',2)[-1]
    
    #strip line numbers for ability to compare by tag
    for i in range(len(list98)):
        line = list98[i].split(' ',1)
        desc98Dict[line[0]] = line[-1].split('\n',1)[-1]

#now to compare
with open('changelog.txt', 'w') as outfile:
    #if the tag has changed text, add it to the changelog
    for key in desc97Dict.keys():
        if key in desc98Dict:
            if desc97Dict[key] != desc98Dict[key]:
                outfile.write("-----\nChanged: {}\n[0.97] {}\n\n[0.98] {}\n".format(key,desc97Dict[key],desc98Dict[key]))
    
    #if the tag is new entirely, add it to the changelog
    for key in desc98Dict.keys():
        if key not in desc97Dict:
            outfile.write("-----\nNew: {}\n[0.98] {}\n".format(key,desc98Dict[key]))



