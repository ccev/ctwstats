import json

class Stats():
    def __init__(self):
        with open("stats.json", "r") as f:
            self.stats = json.load(f)

    def save_file(self):
        with open("stats.json", "w") as f:
            f.write(json.dumps(self.stats, indent=4))

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