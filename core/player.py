from typing import List


class CTWAchievement:
    id: str
    name: str
    desc: str
    points: int
    game_percent: float
    global_percent: float

    def __init__(self, id_: str, data: dict):
        self.id = id_
        self.name = data["name"]
        self.desc = data["description"]
        self.points = data["points"]
        self.game_percent = data["gamePercentUnlocked"]
        self.global_percent = data["globalPercentUnlocked"]


class Player:
    achievements: List[CTWAchievement]

    def __init__(self, data: dict):
        player = data.get("player", {})

        self.name: str = player.get("displayname", "")
        self.uuid: str = player.get("uuid", "")
        self.bust = f"https://visage.surgeplay.com/bust/512/{self.uuid}"

        achievements = player.get("achievements", {})
        self.kills: int = achievements.get("arcade_ctw_slayer", 0)
        self.caps: int = achievements.get("arcade_ctw_oh_sheep", 0)

        achievement_ids = player["achievementsOneTime"]
        self._completed_achs = []
        for ach in achievement_ids:
            if "arcade_ctw" in ach:
                self._completed_achs.append(
                    ach.split("arcade_")[1].upper()
                )
