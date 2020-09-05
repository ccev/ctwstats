import json
import requests

class Stats():
    def __init__(self):
        with open("stats.json", "r") as f:
            self.stats = json.load(f)

    def save_file(self):
        with open("stats.json", "w") as f:
            f.write(json.dumps(self.stats, indent=4))

    def is_on_lb(self, uuid):
        if self.stats.get(uuid, {"leaderboard": False})["leaderboard"]:
            return True
        else:
            return False

    def add_generic(self, uuid, user_id, type_):
        if not uuid in self.stats.keys():
            self.stats[uuid] = {
                "leaderboard": False,
                "stats_by": [],
                "achievements_by": []
            }
        if not user_id in self.stats[uuid][type_]:
            self.stats[uuid][type_].append(user_id)
            self.save_file()

    def add_statsquery(self, uuid, user_id):
        self.add_generic(uuid, user_id, "stats_by")

    def add_achievementsquery(self, uuid, user_id):
        self.add_generic(uuid, user_id, "achievements_by")

    def generic_sort(self, type_):
        s = [(k, len(v[type_])) for k, v in sorted(self.stats.items(), reverse=True, key=lambda item: len(item[1][type_]))]
        r = ""

        for i, a in enumerate(s[:3]):
            i += 1
            name = requests.get(f"https://api.mojang.com/user/profiles/{a[0]}/names").json()[-1]["name"]
            r += f"{i}. **{name}** ({a[1]})\n"
        return r

    def sort_stats(self):
        return self.generic_sort("stats_by")

    def sort_achievements(self):
        return self.generic_sort("achievements_by")