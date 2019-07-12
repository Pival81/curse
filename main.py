import json
import os
from curse import Curse, Mod


if __name__ == "__main__":
    with open('settings.json') as f:
        config = json.load(f)
        if config["multimc_path"] == "":
            print("Your MultiMC path is not set, set it now:")
            config["multimc_path"] = input(">>")
            config["releasetype"] = "release"

    with open("settings.json", "w") as f:
        json.dump(config, f, indent=4)

    packs = dir_list = next(os.walk(config["multimc_path"] + "/instances"))[1]

    for i, x in enumerate(packs, 1):
        print(i, x)

    try:
        selected_pack = packs[int(input(">>")) - 1]
    except:
        exit()
    selected_pack_url = config["multimc_path"] + "/instances/" + selected_pack
    selected_pack_version = json.load(open(selected_pack_url + "/mmc-pack.json"))["components"][1]["version"]
    
    curse = Curse(selected_pack_url)

    while(True):
        print("1) Search mod")
        print("2) Update modpack")
        print("3) Remove mod")
        try:
            choice = int(input(">>"))
        except:
            exit()
        if choice == 1:
            print("Search mod:")
            modlist = curse.getModList(input(">>"), str(selected_pack_version), "25", "0")
            if not modlist:
                continue 
            for i, mod in enumerate(modlist):
                print("#" + str(i + 1))
                print("Name: " + mod.name)
                print("Summary: " + mod.summary)
                print("Categories: " + ", ".join(mod.categories))
                print("--------------------------------------")
            try:
                selected_mod = modlist[int(input(">>")) - 1]
            except:
                exit()
            selected_mod.getFiles()
            selected_mod.install(str(selected_pack_version), selected_pack_url, releasetype=config["releasetype"])
        elif choice == 2:
            curse.updateModpack(str(selected_pack_version), selected_pack_url, releasetype=config["releasetype"])
        elif choice == 3:
            modlist = []
            for idx, entry in enumerate(curse.modlist_manager.modlist):
                modlist.append(entry["id"])
                print("#{} {}".format(idx + 1, entry["filename"]))
            try:
                selected_mod = int(input(">>")) - 1
            except:
                exit()
            curse.modlist_manager.removeMod(modlist[selected_mod])

        curse.modlist_manager.close()
    