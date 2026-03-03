from enum import Enum


class MajorEnum(str, Enum):
    economics = "Экономика"
    engineering = "Инженерия"
    law = "Право"
    psychology = "Психология"
    informatics = "Информатика"
    medicine = "Медицина"
    languages = "Языки"
    media = "Реклама"
    sport = "Спорт"


# institutes, сгруппированные по major
institutes_enum: dict[MajorEnum, list[str]] = {
    MajorEnum.economics: [
        "Институт финансов и менеджмента",
    ],
    MajorEnum.engineering: [
        "Физико-математический институт",
        "Институт нефти и газа",
    ],
    MajorEnum.law: [
        "Институт юстиции",
        "Институт правоохранительной деятельности",
        "Институт прокуратуры",
    ],
    MajorEnum.psychology: [
        "Институт психологии и педагогических наук",
    ],
    MajorEnum.informatics: [
        "Институт информационных технологий",
    ],
    MajorEnum.medicine: [
        "Медико-биологический институт",
    ],
    MajorEnum.languages: [
        "Институт лингвистики и международных отношений",
    ],
    MajorEnum.media: [
        "Институт рекламы и связи",
        "Институт маркетинга",
    ],
    MajorEnum.sport: [
        "Институт физической культуры и спорта",
    ],
}