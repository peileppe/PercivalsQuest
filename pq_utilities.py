"""
Some utility functions
for Percival's Quest RPG
"""
#
#  pq_utilities.py
#  part of Percival's Quest RPG

import json, textwrap, random, shelve, os
from time import sleep

readl = True
try:
    import readline
except ImportError:
    readl = False

try:
    input = raw_input
except NameError:
    pass

def dict_return(pq): # required for python3
    k=list(pq)
    random.shuffle(k)
    return k[0]

def collapse_stringlist(thelist, sortit = False, addcounts = False):
    """Remove duplicate elements from a list, 
    possibly sorting it in the process."""
    collapsed = []
    [collapsed.append(i) for i in thelist if not collapsed.count(i)]
    if sortit:
        collapsed = sorted(collapsed)
    if not addcounts:
        return collapsed
    for j, i in enumerate(collapsed):
        if type(i) is list:
            i = i[0]
        count = thelist.count(i)
        tag = ' x'+str(count) if count > 1 else ''
        collapsed[j] += tag
    return collapsed

def atk_roll(attack, defense, attack_adjust = 0, defense_adjust = 0):
    """Handle any opposed roll ('attack' roll)."""
    print(attack, defense, attack_adjust, defense_adjust)
    if attack[1] <= attack[0]:
        attack_result = attack[0] + attack_adjust
    else:
        attack_result = random.choice([random.randint(int(attack[0]), int(attack[1])) for i in range(0,6)]) + attack_adjust    
    if defense[1] <= defense[0]:
        defense_result = defense[0] + defense_adjust 
    else:
        defense_result = random.choice([random.randint(int(defense[0]), int(defense[1])) for i in range(0,6)]) + defense_adjust
    return attack_result - defense_result

def confirm_quit():
    """Do you really want to quit? """
    send_to_console("Remember that your last save was the last time you rested.")
    choice = input("Are you sure you want to quit (y/n)? ")
    if choice.lower() in ["y", "yes", "quit"]:
        quit()

def choose_from_list(prompt, options, rand = False, character = None, allowed = ["Help"]):
    """Accept user input from a list of options."""
    # -- remove -- 
    #print(type(options))
    #print(options)
    #print(list(options))
    #print(dict(list(options)))
    choice = get_user_input(prompt, character, options = (list(options)) + list(allowed))
    while choice.lower() not in [i.lower() for i in options]:
        if rand and choice.lower() == "random":
            return random.choice(options)
        send_to_console("Sorry, I didn't understand your choice. Try again?")
        choice = get_user_input(prompt, character, options = (list(options) + list(allowed)))
    for i in options:
        if i.lower() == choice.lower():
            return i

class PQ_Completer(object):
    """Custom completer for our fabulous program"""
    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                                    if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None

def get_user_input(prompt, character = None, options = ["Quit"]):
    """Get some info from the user."""
    if readl:
        options = options + ["Quit"] if "Quit" not in options else options
        options = sorted([i.lower() for i in options] + \
            [i.lower().capitalize() for i in options] + \
            [i.upper() for i in options])
        completer = PQ_Completer(options)
        readline.set_completer(None)   
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')
    else:
        options = [i.lower() for i in options]

    user_input = input(color.BOLD + prompt + color.END)
    if "sheet" in options and character and user_input.lower() == "sheet":
        character.tellchar()
        return get_user_input(prompt, character = character, options = options)
    if "help" in options and user_input.lower() == "help":
        pq_help()
        return get_user_input(prompt, character = character, options = options)
    if "equip" in options and character and user_input.lower() == "equip":
        character.equip()
        return get_user_input(prompt, character = character, options = options)
    if user_input.lower() == "quit":
        confirm_quit()
        return get_user_input(prompt, character = character, options = options)
    return user_input

def send_to_console(*output):
    #sleep(0.5)
    print (''.join(output))

def pq_help():
    """Open the help prompt and, y'know, help."""
    with open('data/pq_help_strings.json') as f:
        help_topics = json.load(f)
    send_to_console(textwrap.fill("Help topics: " + ", ".join(sorted(help_topics.keys())) + \
        "; Exit to return to game."))
    topic = choose_from_list("Help> ", list(help_topics.keys()) + ["Exit"],  allowed = []) # hack python 3 dict
    while topic != "Exit":
        send_to_console(color.BOLD + "TOPIC: " + topic.upper() + color.END)
        if topic not in ["Armor", "Weapons", "Races", "Classes", "Feats"]:
            send_to_console(textwrap.fill(help_topics[topic]))
        else:
            send_to_console(help_topics[topic])
        topic = choose_from_list("Help> ", help_topics.keys() + ["Exit"], \
            allowed = [])

class color:
    """Color ANSI codes"""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
savefile = os.path.expanduser("./saves/pq_saves")

def save(rpg):
    savedb = shelve.open(savefile)
    savedb[rpg.player_name] = rpg
    savedb.close()
    
def load(rpg):
    savedb = shelve.open(savefile)
    print('Saved Games:',savedb.keys())
    if rpg.player_name not in savedb:
        savedb.close()
        return None
    else:
        rpgout = savedb[rpg.player_name]
        savedb.close()
        return rpgout
