from enum import Enum


class MajorNameEnum(str, Enum):
    economics = "Экономика"
    engineering = "Инженерия"
    law = "Право"
    languages = "Языки"
    informatics = "Информатика"
    psychology = "Психология"
    medicine = "Медицина"


class MajorDescriptionEnum(str, Enum):
    economics = "Факультет экономики и финансового менеджмента"
    engineering = "Факультет инженерии"
    law = "Факультет права"
    languages = "Факультет лингвистики и международных отношений"
    psychology = "Факультет психологии и педагогических наук"
    informatics = "Факультет информационных технологий"
    medicine = "Факультет медицины и биологии"