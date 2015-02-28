"""
Puzzle encounter class declaration
for Percival's Quest RPG
"""
#
#  pq_puzzle.py
#  part of Percival's Quest RPG

from pq_namegen import riddlegen, numgen
from pq_utilities import atk_roll, choose_from_list, get_user_input, color, send_to_console
from pq_equipment import pq_treasuregen, pq_item_type
import random, time, json, textwrap

pq_stats = {'Attack':0, 'Defense':1, 'Reflexes':2, 'Fortitude':3, 
    'Mind':4, 'Skill':5}

class PQ_Puzzle(object):
    """Puzzle encounter object"""
    def __init__(self, lvl, character):
        """Initialize puzzle encounter based on dungeon level."""
        riddle = riddlegen()
        self.char = character
        self.answer = riddle[0]
        self.riddle = riddle[1]
        self.riddleguess = 3
        riches = []
        while not riches:
            treasure = pq_treasuregen(lvl + 2)
            for t in treasure.keys():
                if t == 'gp':
                    continue
                if treasure[t]:
                    riches.append(treasure[t])
        self.riches = random.choice(riches)
        self.numcode = numgen()
        self.numguess = 10
        self.gold = sum([random.randint(1, 100) for i in range(lvl)])
        self.damage = 0
        self.trial_num = lvl
        self.knowledge = lvl / 2
        self.thing = random.choice(['mysterious dark spirit', 'regal sphinx', \
            'magic mirror', 'blind oracle'])
        self.choice = ""
        self.finished = False
        
    def puzzleinit(self):
        """Begin a puzzle encounter."""
        msg1 = "Exploring the depths of the Dungeon, you encounter a " + \
            self.thing + " in a lonely room."
        if self.thing == 'magic mirror':
            msg1 += " A sinister face materializes in its murky surface, " \
                "looking directly at you."
        else:
            msg1 += " The " + self.thing + " addresses you."
        msg2 = color.BOLD + " 'Welcome to the Dungeon, adventurer. Portents " \
            "have foreshadowed your coming. I am here to aid you on your " \
            "journey, should you prove worthy. I offer you choices three: " \
            "you may play a game, for Gold; solve a riddle, for Riches;" \
            " or undergo a Trial of Being, for Knowledge. Choose your prize," \
            " and choose well.'"+color.END
        msg3 = "(Your choices are Gold, Riches, Knowledge, or Skip.)"
        send_to_console(textwrap.fill(msg1 + msg2)+'\n'+msg3)
        choice = choose_from_list("Choice> ", ["gold", "riches", "knowledge", \
            "skip"], character=self.char, allowed=['sheet', 'help', 'equip'])
        self.choice = choice
        if self.choice == "gold":
            msg = "The " + self.thing + " nods approvingly. " + color.BOLD + \
                "'You have chosen the game; here are the rules. I have " \
                "selected a set of four digits, in some order. You have 10 " \
                "chances to guess the digits, in the correct order. If you " \
                "are polite, I may be persuaded to give you a hint... Now, " \
                "begin; you have 10 chances remaining.'" + color.END
            msg2 = "(Guess should be ####)"
            send_to_console(textwrap.fill(msg)+'\n'+msg2)
            self.check_numguess()
            return
        elif self.choice == "riches":
            msg = "The " + self.thing + " nods slowly. " + color.BOLD + \
                "'You have chosen the riddle; here are the rules. I will " \
                "tell you the riddle, which has an answer one word long. " \
                "You have three chances to guess the answer. If it goes " \
                "poorly, I may decide to give you a hint. Here is the riddle: "
            msg2 = "Now, begin your guess. You have three chances remaining.'"\
                + color.END
            send_to_console(textwrap.fill(msg), '\n', textwrap.fill(self.riddle), \
                '\n', msg2)
            self.check_riddleguess()
            return
        elif self.choice == "knowledge":
            msg = "The " + self.thing+"'s face spreads in a predatory smile. "\
                + color.BOLD + "'As you wish. The Trial consists of three " \
                "tests; if you succeed at all three, you will be rewarded." \
                " The first test will begin... now.'" + color.END
            send_to_console(textwrap.fill(msg))
            self.trialofbeing()
            return
        elif self.choice == "skip":
            self.failure()
    
    def failure(self):
        """Handler for failure to complete puzzle."""
        msg = "The " + self.thing + " stares at you impassively. " + \
            color.BOLD + "'You have been found wanting. How disappointing.'" \
            + color.END + " Then it vanishes, leaving no trace that this " \
            "room of the dungeon was ever occupied."
        send_to_console(textwrap.fill(msg))
        if self.choice == "knowledge" and self.damage > 0:
            self.char.ouch(self.damage)
            msg = "The Trial was extremely taxing; you take " + \
                str(self.damage) + " damage"
            if self.char.hitpoints[0] <= 0:
                msg += "..."
                self.char.dead = True
                send_to_console('Sorry, ' + self.char.player + ', you have died. ' \
                    'You can load from your last save, quit, or make a new ' \
                    'character.', '\n')
            else:
                msg += ", and have " + str(self.char.hitpoints[0]) + \
                    " hit points remaining."
            send_to_console(msg, '\n')
        self.finished = True
        return
    
    def success(self):
        """Handler for successful puzzle completion."""
        msg = "The " + self.thing + " seems pleased. " + color.BOLD + \
            "'You have proven worthy, and now may receive your reward.'" + \
            color.END + " Then it vanishes, leaving no trace that this room " \
            "of the dungeon was ever occupied."
        send_to_console(textwrap.fill(msg))
        msg = "You gain "
        if self.choice == "gold":
            msg += str(self.gold) + " gp!"
            send_to_console(msg, '\n')
            self.char.defeat_enemy(0, {'gp':self.gold})
        if self.choice == "riches":
            typ = pq_item_type(self.riches)
            msg += "a "
            if typ[0] == "ring":
                msg += "Ring of "
            msg += self.riches + "!"
            send_to_console(msg, '\n')
            self.char.defeat_enemy(0, {typ[0]:self.riches})
        if self.choice == "knowledge":
            msg += str(self.knowledge) + " experience!"
            send_to_console(msg, '\n')
            self.char.defeat_enemy(self.knowledge, {})
            if self.char.level[0] >= 10 * self.char.level[1]:
                self.char.levelup()
        self.finished = True
        return
    
    def trialofbeing(self):
        """Run character through the Trial of Being."""
        sta = random.sample(['Attack', 'Defense', 'Reflexes', 'Fortitude', \
            'Mind', 'Skill'], 3)
        with open('data/pq_trialmsg.json') as f:
            trials = json.load(f)
        for i, s in enumerate(sta):
            time.sleep(0.5)
            send_to_console(textwrap.fill("The " + ("first", "second", "third")[i] + \
                " challenge begins. " + trials['tests'][s]), '\n')
            result = atk_roll([0, self.char.stats[pq_stats[s]]], \
                [0, self.trial_num], 0, 0)
            if result < 0:
                send_to_console(trials['lose'][s], '\n')
                self.damage = result
                self.failure()
                return
            else:
                send_to_console(trials['win'][s], '\n')
                self.knowledge += self.trial_num
        self.success()
        
    def check_riddleguess(self):
        """Handle guesses of the riddle answer."""
        while self.riddleguess > 0:
            guess = get_user_input("Guess> ", character=self.char, \
                options = ["sheet", "equip", "help"])
            self.riddleguess -= 1
            #check for a valid guess
            badguess = 0
            import string
            if len(guess.split()) > 1:
                badguess = 1
            for i in guess:
                if i not in string.letters:
                    badguess = 2
                    break
            if badguess:
                badguess_message = ["your guess should be one word only.'", \
                    "what you said isn't even a word.'"][badguess - 1]
                send_to_console("The " + self.thing + " frowns. 'I do not know why you " \
                    "would waste a guess on that... " + badguess_message, '\n')
                continue
            #are they right?
            if guess.upper() == self.answer:
                self.success()
                return
            #are they done?
            if self.riddleguess <= 0:
                break
            answer_length = len(self.answer)
            pl = "s" if self.riddleguess != 1 else ""
            msg = "You have guessed incorrectly, leaving you with " + \
                str(self.riddleguess) + " chance" + pl + " remaining. "
            msg += "Here is a hint to help you: the answer to the riddle " \
                "is a single word with " + str(answer_length) + " letters."
            send_to_console(msg, '\n')
        self.failure()
        return
        
    def check_numguess(self):
        """A numeric Mastermind game! Give feedback on the guesses."""
        while self.numguess > 0:
            guess = get_user_input("Guess> ", character=self.char, \
                options = ["sheet", "equip", "help"])
            self.numguess -= 1
            #check for a valid guess
            badguess = False
            if len(guess) != 4:
                badguess = True
            for i in guess:
                try:
                    j = int(i)
                except ValueError:
                    badguess = True
            if badguess:
                send_to_console("The " + self.thing + " frowns. 'I do not know why " \
                    "you would waste a guess on that.'", '\n')
                continue
            copy_answer = [i for i in self.numcode]
            copy_guess = [i for i in guess]
            correct = []
            #first pass: check for correct positions
            progress = 0
            for i in range(4):
                if copy_guess[i] == copy_answer[i]:
                    correct.append('rectus')
                    copy_answer[i] = '*'
                    copy_guess[i] = '*'
                    progress += 2
            #did they get it right?
            if ''.join(copy_answer) == '****' or progress == 8:
                self.success()
                return
            #if not, are they done?
            if self.numguess <= 0:
                break
            #if not, let's check for correct digits, incorrect positions
            for i in range(4):
                if copy_guess[i] != '*' and copy_guess[i] in copy_answer:
                    correct.append('proxime')
                    progress += 1
            #fill out the rest with evil BWHAHA
            ncorrect = len(correct)
            for i in range(4 - ncorrect):
                correct.append('malum')
            #concatenate results
            hint = []
            nums = ['', 'singuli', 'bini', 'terni', 'quaterni']
            for i in ['rectus', 'proxime', 'malum']:
                num = correct.count(i)
                if num > 0:
                    hint.append(nums[num] + ' ' + i)
            hint = ', '.join(hint) + '.'
            progress = (progress + 1) / 2
            progmsg = ("The " + self.thing + " sighs. " + color.BOLD + \
                "'You are nearly as far from correct as it is possible to be."\
                " Perhaps this hint will help:",
                "The " + self.thing + " nods slowly. " + color.BOLD + \
                "'You have some small skill at this sort of thing, " \
                "it would seem. A hint to aid your progress:",
                "The " + self.thing + " quirks an eyebrow. " + color.BOLD + \
                "'Perhaps you do not even need this hint, but I will " \
                "provide it anyway:",
                "The " + self.thing + " smiles, showing a little too many " \
                "teeth. " + color.BOLD + "'I am impressed -- you are nearly " \
                "there. Another hint:")
            if self.numguess > 1:
                nummsg = "You have " + str(self.numguess) + " guesses " \
                    "remaining. Use them wisely.'" + color.END
            else:
                nummsg = "You have one guess remaining. Use it wisely.'" \
                    + color.END
            send_to_console(textwrap.fill(" ".join([progmsg[progress], hint, \
                nummsg])), '\n')
        self.failure()
        return
        
