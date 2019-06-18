"""
This is the main module for the Percival's Quest RPG.
To start the game, at the command prompt type:

prompt$ python percivalsquest.py
"""

#
#  percivalsquest.py
#  part of Percival's Quest RPG (duh)

logo = """
   ()    
   )(     
o======o           
   ||              
   ||    ___              _            _ _        ____                 _    
   ||   / _ \___ _ __ ___(_)_   ____ _| ( )__    /___ \_   _  ___  ___| |_ 
   ||  / /_)/ _ \ '__/ __| \ \ / / _` | |/ __|  //  / / | | |/ _ \/ __| __| 
   || / ___/  __/ | | (__| |\ V / (_| | |\__ \ / \_/ /| |_| |  __/\__ \ |_ 
   || \/    \___|_|  \___|_| \_/ \__,_|_||___/ \___,_\ \__,_|\___||___/\__| 
   ||                                                                     
   ||                            copyright 2013
   || 
   \/ 

"""

import pq_rpg as pqr
from pq_utilities import color, choose_from_list, confirm_quit, save, load, \
    get_user_input, send_to_console
import shelve, os, textwrap
from colorama import init

init()

def town(rpg):
    """Maintain interactions with the town of North Granby."""
    while True:
        if rpg.character.dead:
            send_to_console(color.BOLD+"You are dead!"+color.END)
            deadchar(rpg)
            break
        send_to_console("Where would you like to go?\n"+color.BOLD+"Options: Home, " \
            "Cityhall, Bazaar, Temple, or Dungeon [Level#] (max "+ \
            str(rpg.maxdungeonlevel)+")"+color.END)
        destinations = ["Dungeon", "Home", "Cityhall", "Quest", \
            "Bazaar", "Temple"] + ["Dungeon "+str(i) for i in \
            range(1, rpg.maxdungeonlevel+1)]
        goto = choose_from_list("Town> ", destinations, rand=False,
            character=rpg.character, allowed=["sheet","help","equip"])
        if goto == "Home":
            send_to_console("You returned home," \
                +color.BOLD+" game is saved "+color.END+\
                "- you had a good nigth sleep.")
            rpg.character.sleep()
            save(rpg)
            continue
        elif goto in ["Cityhall", "Quest"]:
            send_to_console("You head to the Cityhall.")
            rpg.questhall()
            continue
        elif goto == "Bazaar":
            send_to_console("You head into the shop.")
            rpg.visit_shop()
            continue
        elif goto == "Temple":
            send_to_console("You head into the Temple.")
            rpg.visit_shrine()
            continue
        else:
            goto = goto.split()
            rpg.destination("start")
            if goto[0] == "Dungeon" and len(goto) == 1:
                rpg.dungeonlevel = 1
            else:
                rpg.dungeonlevel = int(goto[1])
            send_to_console("You head into the Dungeon, level "+str(rpg.dungeonlevel)+".")
            dungeon(rpg)
            continue

def dungeon(rpg):
    """Maintain interaction with the dungeon"""
    dothis = ""
    while dothis != "Leave":
        if rpg.character.dead:
            return
        actions = ["Research","Leave"] if rpg.whereareyou == "start" \
            else ["Research","Backtrack"]
        send_to_console("You're in the dank dark dungeon. What do you want to do?\n"+\
            "Options: "+color.BOLD+", ".join(actions)+color.END)
        dothis = choose_from_list("Dungeon> ", actions, rand=False,
            character=rpg.character, allowed=["sheet","help","equip"])
        if dothis == "Leave":
            if rpg.whereareyou != "start":
                send_to_console("You can't leave from here; you have to backtrack " \
                    "to the start of the level.")
                dothis = ""
                continue
            else:
                rpg.destination("town")
                send_to_console("You return back"+color.BOLD+" to town."+color.END)
                continue
        elif dothis == "Backtrack":
            if rpg.whereareyou == "start":
                send_to_console("You're already at the beginning of the level.")
                continue
            if rpg.check_backtrack():
                send_to_console("You successfully find your way back " \
                    "to the beginning of the level.")
                rpg.destination("start")
                continue
            else:
                send_to_console("On your way back, you get lost! You find yourself " \
                    "in another room of the dungeon...")
                rpg.destination("dungeon")
                rpg.explore()
                continue
        elif dothis == "Research":
            rpg.destination("dungeon")
            rpg.explore()
            if rpg.character.dead:
                deadchar(rpg)
            else:
                continue

def deadchar(rpg):
    """Deal with character death"""
    send_to_console("What would you like to do? Options: "\
        "Generate (a new character), Load, Quit")
    dothis = choose_from_list("Dead> ", ["Generate", "Load", "Quit"],
        character=rpg.character, rand=False, allowed=["sheet", "help"])
    if dothis == "Quit":
        confirm_quit()
        deadchar(rpg)
        return
    if dothis == "Load":
        rpg = load(rpg)
        if not rpg:
            send_to_console("I'm sorry, that didn't work... maybe you deleted " \
                "the save file? Anyway...")
            deadchar(rpg)
            return
        else:
            send_to_console("Game successfully loaded!")
            send_to_console("You begin in the town square.")
            rpg.character.tellchar()
            rpg.destination("town")
            town(rpg)
            return
    if dothis == "Generate":
        rpg = generate(rpg)
        send_to_console("You begin in the town square.")
        town(rpg)
        return
        
def generate(rpg):
    """Wrapper for making a new character"""
    send_to_console("Time to make a new character! It'll be saved under this player name.")
    rpg.character.chargen(rpg.player_name)
    save(rpg)
    msg = "In the town of North Granby, the town militia has recently " \
        "discovered that the plague of monsters harrassing the townspeople " \
        "originates from a nearby dungeon crammed with nasties. As the " \
        "resident adventurer, the Mayor of North Granby (a retired " \
        "adventurer by the name of Sir Percival) has recruited you to clear " \
        "out the dungeon."
    send_to_console(textwrap.fill(msg))
    return rpg

def main():
    """Initialize and start the game session"""
    send_to_console(logo)
    send_to_console(textwrap.fill("Welcome to Percival's Quest! This is a solo random " \
        "dungeoncrawl rpg written in python by the ever-resourceful (and " \
        "extremely humble) sirpercival."))
    player_name = get_user_input("Please enter your player name> ")
    msg = "Welcome, "+player_name+"!"
    rpg_instance = pqr.PQ_RPG(player_name)
    newgame = False
    temp_rpg = load(rpg_instance)
    if temp_rpg:
        msg += " You currently have a game saved. Would you like to load it?"
        send_to_console(msg)
        loadit = get_user_input("Load (y/n)> ", options = ['Yes','No','Y','N','Load'])
        if loadit.lower() in ["y", "yes", "load"]:
            rpg_instance = temp_rpg
            del temp_rpg
            send_to_console("Game successfully loaded.")
            rpg_instance.character.tellchar()
        else:
            newgame = True
    else:
        send_to_console(msg + " You don't have a character saved...")
        newgame = True
    if newgame:
        rpg_instance = generate(rpg_instance)
    msg = "You begin in the town square. \n"
    msg += "(Please note that at almost any prompt, you can choose Sheet " \
        "to look at your charsheet, Equip to change your equipment, Help " \
        "to enter the help library, or Quit to quit.)"
    send_to_console(textwrap.fill(msg))
    msg = "To the East is your humble abode and warm bed; " \
        "to the North, the General Store where various and sundry goods " \
        "may be purchased; to the West, the Cityhall where the mayor " \
        "makes his office; to the Northwest, the local Temple to the " \
        "Unknowable Gods; and to the South lie the gates of the city, " \
        "leading out to the Dungeon."
    send_to_console(textwrap.fill(msg))
    town(rpg_instance)
    
if __name__ == '__main__':
    main()
