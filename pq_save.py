import shelve

def listSave():
    db = shelve.open("saves/pq_saves")
    dkeys = list(db.keys())
    dkeys.sort()
    for x in dkeys:
        print ( x, db[x].player_name , db[x].maxdungeonlevel)
    db.close()
    return

def writeSave(oldName, newName):
    db = shelve.open("saves/pq_saves")
    dkeys = list(db.keys())
    for c in dkeys:
        if (db[c].player_name==oldName):
            print('found name: '+oldName)
            rpg=db[oldName]
            rpg.player_name=newName
            db[newName]=rpg
            del db[oldName]
            print('new value: '+newName)
    db.close()
    return

def main():
    listSave()
    writeSave('peileppe','Sauron')
    return

if __name__ == "__main__":
    main()
