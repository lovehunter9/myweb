import random
import re
import json
import requests
from collections import Counter, defaultdict
from typing import Optional

OLLAMA_URL = "http://localhost:11434"


def _ollama_available() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _ollama_generate(prompt: str, model: str = "qwen2:0.5b") -> Optional[str]:
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        if r.status_code == 200:
            return r.json().get("response", "").strip()
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════
#  Chinese Name Data
# ═══════════════════════════════════════════════════════════════════════

SURNAMES = [
    "李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
    "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧",
    "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕",
    "苏", "卢", "蒋", "蔡", "贾", "丁", "魏", "薛", "叶", "阎",
    "余", "潘", "杜", "戴", "夏", "钟", "汪", "田", "任", "姜",
    "范", "方", "石", "姚", "谭", "廖", "邹", "熊", "金", "陆",
    "郝", "孔", "白", "崔", "康", "毛", "邱", "秦", "江", "史",
    "顾", "侯", "邵", "龙", "万", "段", "雷", "钱", "汤", "尹",
    "易", "常", "武", "乔", "贺", "赖", "龚", "文",
]

COMPOUND_SURNAMES = [
    "欧阳", "司马", "上官", "诸葛", "东方", "皇甫", "令狐", "慕容",
    "南宫", "西门", "独孤", "公孙", "轩辕", "百里", "端木", "宇文",
]

NAME_CHARS = {
    "classical_male": [
        "渊", "瑾", "瑜", "昊", "辰", "宸", "睿", "哲", "翰", "墨",
        "衡", "琛", "煜", "烨", "霖", "澈", "骞", "彦", "珩", "璟",
        "铭", "瀚", "逸", "之", "然", "远", "明", "若", "景", "修",
        "文", "承", "子", "云", "风", "清", "言", "怀", "行", "安",
    ],
    "classical_female": [
        "婉", "清", "瑶", "琳", "雪", "月", "云", "霜", "露", "兰",
        "芷", "若", "素", "灵", "薇", "蕊", "颖", "琬", "玥", "瑾",
        "漪", "瑛", "婧", "妍", "嫣", "柔", "凝", "黛", "瑟", "筠",
        "蓉", "卿", "韵", "梦", "羽", "歆", "沁", "澜", "珺", "锦",
    ],
    "xianxia": [
        "玄", "天", "无", "紫", "青", "灵", "幽", "尘", "虚", "冥",
        "凌", "霄", "九", "苍", "墟", "渺", "恒", "沧", "太", "元",
        "道", "仙", "阳", "阴", "星", "辰", "华", "玉", "寒", "烟",
        "璇", "罗", "衍", "绝", "空", "离", "魂", "夜", "影", "殇",
    ],
    "wuxia": [
        "剑", "风", "云", "龙", "虎", "鹤", "鹰", "豪", "义", "侠",
        "忠", "勇", "飞", "天", "傲", "狂", "啸", "雄", "威", "霸",
        "刀", "枪", "武", "战", "英", "杰", "铁", "血", "烈", "猛",
        "千", "山", "长", "河", "秋", "寒", "冷", "孤", "独", "残",
    ],
    "modern": [
        "浩", "宇", "轩", "泽", "博", "涵", "思", "嘉", "欣", "怡",
        "佳", "晨", "旭", "阳", "俊", "杰", "伟", "强", "磊", "明",
        "雅", "婷", "静", "洁", "慧", "颖", "萌", "晴", "悦", "蕾",
        "辉", "峰", "翔", "飞", "鹏", "志", "文", "武", "才", "德",
    ],
    "scifi": [
        "星", "辰", "宇", "航", "量", "子", "维", "光", "速", "域",
        "拓", "创", "晶", "能", "核", "极", "界", "源", "元", "码",
        "智", "信", "达", "远", "新", "超", "异", "幻", "灵", "零",
        "数", "控", "频", "波", "磁", "引", "合", "联", "际", "穹",
    ],
}

PERSONALITY_TRAITS = {
    "positive": [
        "沉稳内敛", "果敢决断", "温文尔雅", "机智过人", "刚正不阿",
        "心思缜密", "豁达大度", "才华横溢", "忠义两全", "慈悲为怀",
        "聪慧绝伦", "谦逊有礼", "坚韧不拔", "淡泊名利", "洞察入微",
    ],
    "neutral": [
        "性格孤僻", "沉默寡言", "不苟言笑", "特立独行", "亦正亦邪",
        "喜怒无常", "深不可测", "冷漠疏离", "桀骜不驯", "城府极深",
        "离经叛道", "不拘小节", "随性洒脱", "玩世不恭", "我行我素",
    ],
    "negative": [
        "阴险狡诈", "贪婪成性", "心狠手辣", "嫉妒成狂", "暴虐无道",
        "虚伪做作", "冷血无情", "多疑善变", "自私自利", "目中无人",
    ],
}

BACKGROUNDS = [
    "出身名门望族，从小接受严格教育",
    "幼年丧亲，由师父一手带大",
    "本是皇族血脉，却流落民间长大",
    "出身贫寒，凭借天赋一路崛起",
    "世代书香门第，博览群书",
    "来自边陲小镇，心怀远大抱负",
    "曾为富家子弟，家道中落后奋发图强",
    "身世成谜，被预言为改变世界之人",
    "从小在寺庙/道观长大，精通佛法/道法",
    "出身将门世家，自小习武",
    "原为敌国质子，暗中积蓄力量",
    "农家子弟，偶得奇遇改变命运",
    "孤儿出身，被秘密组织收养训练",
    "曾是一代宗师的关门弟子",
    "前世记忆觉醒，重走人生路",
]

ABILITIES = {
    "xianxia": [
        "精通剑道，一剑可开天", "擅长炼丹，丹药出神入化",
        "阵法大师，布阵困敌于无形", "体修天才，肉身可碎星辰",
        "符篆宗师，画符驱邪斩妖", "拥有先天灵体，修炼速度惊人",
        "掌握空间法则，来去自如", "精通占卜推演，可知过去未来",
        "拥有上古血脉，可召唤神兽", "天生灵魂强大，擅长精神攻击",
    ],
    "wuxia": [
        "内力深厚，已臻化境", "轻功绝顶，踏雪无痕",
        "剑法超群，剑意通神", "掌法独步天下", "暗器手法出神入化",
        "医术精湛，活死人肉白骨", "琴棋书画皆可化为杀招",
        "精通易容术，变幻莫测", "点穴功夫一流", "身法奇快，鬼魅莫测",
    ],
    "modern": [
        "商业天才，善于运筹帷幄", "黑客高手，精通网络技术",
        "格斗专家，身手不凡", "心理学大师，洞悉人心",
        "医学奇才，妙手回春", "金融鬼才，呼风唤雨",
        "法律精英，能言善辩", "艺术天才，才情出众",
        "谈判专家，化解危机", "侦探天赋，明察秋毫",
    ],
    "scifi": [
        "基因强化者，身体素质超越常人", "精神力异能者，可操控物质",
        "量子计算专家，可与AI深度融合", "空间跳跃能力，瞬间移动",
        "生物改造专家，可重塑生命", "时间感知者，预见短暂未来",
        "纳米科技大师，微观操控", "暗物质感应者，掌控隐秘力量",
        "星际领航员，天生方向感极强", "意识上传先驱，灵魂可在网络中存在",
    ],
}

BUILD_OPTIONS = ["高大魁梧", "修长挺拔", "匀称健美", "纤细苗条", "娇小玲珑", "壮硕有力", "清瘦文弱"]
HEIGHT_OPTIONS = ["身高八尺有余", "身量中等", "身姿颀长", "高挑出众", "身段婀娜"]
FACE_OPTIONS = [
    "面如冠玉，剑眉星目", "五官分明，棱角如刀削", "容颜清丽，肤若凝脂",
    "面容冷峻，不怒自威", "眉目如画，唇红齿白", "面带疤痕，目光锐利",
    "轮廓柔和，笑容温暖", "五官精致，如同雕刻", "面容苍白，气质阴郁",
    "浓眉大眼，英气勃勃",
]
EYE_OPTIONS = [
    "双眸深邃如渊", "目含星辉", "眼神清澈如水", "双目炯炯有神",
    "瞳色异于常人", "目光如炬", "眼含笑意", "目光淡漠而深远",
]
HAIR_OPTIONS = [
    "黑发如墨，束以玉冠", "银发如瀑，随风飞扬", "长发及腰，以丝带束起",
    "短发利落，干净精神", "白发苍苍，却面容不老", "乌发如云，挽成高髻",
    "碎发微乱，添几分不羁", "发如红焰，耀眼夺目",
]
EXTRA_APPEARANCE = [
    "周身气质出尘，仿佛不食人间烟火。",
    "一身正气，令人不敢直视。",
    "举手投足间尽显贵气。",
    "浑身散发着危险的气息。",
    "看似温和无害，实则深藏不露。",
    "气质冷冽如寒冰，拒人于千里之外。",
    "自带一股书卷气息。",
    "身上总带着淡淡的药香/酒香。",
    "",
]


# ═══════════════════════════════════════════════════════════════════════
#  World / Background Setting Data
# ═══════════════════════════════════════════════════════════════════════

WORLD_TYPES = {
    "仙侠": {
        "desc": [
            "这是一个以修仙为主的世界，灵气充沛，万物皆可修炼。",
            "此界分为凡界、灵界与仙界三重天地，修行者追求长生不老。",
        ],
        "power_system": [
            "修炼体系分为：练气、筑基、金丹、元婴、化神、渡劫、大乘、飞升。",
            "以灵气为根基，分为剑修、丹修、阵修、符修、体修等流派。",
        ],
        "factions": [
            "三大正道宗门与五大魔门对峙千年，散修联盟居中调停。",
            "十大仙门掌控此界，各据一方灵脉，暗流涌动。",
        ],
    },
    "玄幻": {
        "desc": [
            "天地浩瀚，大陆无边，强者为尊的世界，实力决定一切。",
            "万族林立的广袤大陆，各族之间争斗不休，天才辈出。",
        ],
        "power_system": [
            "斗气修炼分为：斗者、斗师、大斗师、斗灵、斗王、斗皇、斗宗、斗尊、斗圣、斗帝。",
            "元力等级：凡境、灵境、地境、天境、圣境、帝境、神境，每境分九重。",
        ],
        "factions": [
            "五大帝国割据天下，各有镇国强者坐镇，帝国之外是凶险的蛮荒之地。",
            "四大家族与三大学院构成大陆格局，上方还有神秘的上界势力。",
        ],
    },
    "武侠": {
        "desc": [
            "江湖恩怨，快意恩仇。庙堂之高，江湖之远，侠之大者为国为民。",
            "大好河山，群雄逐鹿。武林纷争不断，各路豪杰各怀心思。",
        ],
        "power_system": [
            "内功心法为根基，外加拳脚兵器。武学境界：入门、小成、大成、登峰造极、返璞归真。",
            "内力分阴阳两极，武学讲究招式与内力并重，最高境界为无招胜有招。",
        ],
        "factions": [
            "少林武当为正道领袖，丐帮势力遍布天下，明教暗中崛起。各大门派盟会在即。",
            "北方武林以剑为尊，南方门派以掌法著称，中原武林世家暗中角力。",
        ],
    },
    "科幻": {
        "desc": [
            "星际纪元2847年，人类已殖民数百颗星球，建立了庞大的星际联邦。",
            "量子革命之后，人类突破光速壁障，开启了星际大航海时代。",
        ],
        "power_system": [
            "科技等级从I级（行星文明）到VII级（宇宙文明），人类目前处于III级文明门槛。",
            "基因强化、机械改造、意识上传三条进化路线并行发展，各有拥趸。",
        ],
        "factions": [
            "星际联邦、自由贸易联盟与外域独立军三方势力角力，AI自治区保持中立。",
            "地球联合政府、火星共和国与外环殖民地联盟构成三足鼎立之势。",
        ],
    },
    "都市": {
        "desc": [
            "繁华都市，高楼林立。商业帝国之间暗流涌动，权谋与爱情交织。",
            "现代社会表象之下，隐藏着不为人知的秘密世界。",
        ],
        "power_system": [
            "金钱与权力是最大的力量，商战中没有永远的敌人，也没有永远的朋友。",
            "古武传承隐匿于都市，特殊能力者秘密存在，维持着表面的平静。",
        ],
        "factions": [
            "四大家族把控经济命脉，新兴科技势力异军突起，地下世界自有规则。",
            "老牌财阀与新生代企业家的对决，各方势力在这座城市中博弈。",
        ],
    },
    "古代言情": {
        "desc": [
            "王朝更迭，宫廷深处暗藏杀机。后宫佳丽三千，唯有智者方能生存。",
            "盛世繁华之下，大家族之间联姻结盟，儿女情长与家国天下交织。",
        ],
        "power_system": [
            "皇权至上，家族势力盘根错节，后宫位分为：答应、常在、贵人、嫔、妃、贵妃、皇贵妃、皇后。",
            "世家大族以联姻巩固势力，文臣武将各自站队，暗中较量。",
        ],
        "factions": [
            "皇后一族与贵妃一族明争暗斗，太子党与诸皇子各怀鬼胎。",
            "世家大族分为保皇派与改革派，江湖势力暗中介入朝堂争斗。",
        ],
    },
}

GEOGRAPHY_TEMPLATES = [
    "大陆中央是广袤的{plain}，东临{sea}，西接{mountain}，南有{forest}，北是{desert}。",
    "世界由{num}座大陆组成，各大陆之间隔着危险的{sea}，传说{sea}深处沉睡着远古巨兽。",
]
PLAIN_NAMES = ["中州平原", "天元大平原", "沃土千里", "帝都腹地"]
SEA_NAMES = ["无尽之海", "东海", "幽冥海域", "星落海", "混沌之海"]
MOUNTAIN_NAMES = ["万仞山脉", "昆仑绝岭", "天柱山脉", "龙脊山脉"]
FOREST_NAMES = ["暗影密林", "万妖森林", "灵木古林", "迷雾丛林"]
DESERT_NAMES = ["大漠流沙", "焚天沙漠", "死亡戈壁", "黄沙万里"]


# ═══════════════════════════════════════════════════════════════════════
#  Novel Title Data
# ═══════════════════════════════════════════════════════════════════════

NOVEL_TITLE_PATTERNS = {
    "仙侠": [
        "{adj}{noun}录", "{noun}仙途", "一剑{verb}{noun}",
        "{noun}不朽", "万古{noun}帝", "{adj}{noun}传",
        "我在{place}修仙的日子", "{noun}道", "太{adj}{noun}经",
        "一念{noun}仙", "{noun}长生", "{adj}仙{noun}",
    ],
    "玄幻": [
        "{adj}{noun}决", "吞噬{noun}", "{noun}大帝",
        "万界{noun}尊", "{adj}{noun}天", "至尊{noun}王",
        "{noun}破天", "无敌{noun}体", "{noun}独尊",
        "逆天{noun}神", "永恒{noun}座", "{adj}之{noun}",
    ],
    "武侠": [
        "{noun}江湖", "{adj}剑{noun}", "天涯{noun}客",
        "{noun}风云录", "侠{noun}行", "{adj}刀{noun}",
        "笑傲{noun}", "{noun}英雄传", "武{noun}天下",
    ],
    "科幻": [
        "{noun}纪元", "星际{noun}舰", "{adj}宇宙",
        "量子{noun}", "{noun}觉醒", "银河{noun}录",
        "{adj}星域", "末日{noun}歌", "深空{noun}",
    ],
    "都市": [
        "都市之{noun}", "{adj}人生", "重生之{noun}",
        "{noun}风云", "超级{noun}系统", "{adj}{noun}年代",
        "我的{adj}{noun}", "{noun}传奇", "至尊{noun}",
    ],
    "古代言情": [
        "{adj}{noun}记", "凤{verb}{noun}", "{noun}锦绣",
        "嫡女{noun}", "{adj}王妃", "后宫{noun}传",
        "{noun}倾城", "皇{noun}令", "红楼{noun}梦",
    ],
}

TITLE_WORDS = {
    "adj": [
        "永恒", "不灭", "无上", "太古", "混沌", "逆天", "绝世",
        "苍穹", "鸿蒙", "九天", "万古", "亘古", "至高", "浮生",
        "长安", "烟雨", "锦绣", "盛世", "风华", "倾世",
    ],
    "noun": [
        "星辰", "苍穹", "乾坤", "天地", "龙凤", "风云", "剑魂",
        "神魔", "仙魔", "帝皇", "山河", "天命", "浮生", "红颜",
        "江山", "明月", "琉璃", "玲珑", "棋局", "沧海",
    ],
    "verb": [
        "破", "碎", "斩", "镇", "封", "焚", "临", "踏", "噬", "归",
    ],
    "place": [
        "仙门", "宗门", "深渊", "秘境", "古墓", "帝都",
        "蛮荒", "深山", "学院", "异世界",
    ],
}


# ═══════════════════════════════════════════════════════════════════════
#  Cover Style Data
# ═══════════════════════════════════════════════════════════════════════

COVER_STYLES = {
    "仙侠": {
        "colors": ["#1a0a3e", "#2d1b69", "#0d1b2a", "#1b2838"],
        "accents": ["#7b68ee", "#9370db", "#00ced1", "#48d1cc"],
        "elements": ["cloud", "sword", "mountain", "moon"],
    },
    "玄幻": {
        "colors": ["#0a0a2e", "#1a0000", "#0d0d0d", "#1a1a2e"],
        "accents": ["#ff4500", "#ffd700", "#ff6347", "#dc143c"],
        "elements": ["flame", "dragon", "star", "lightning"],
    },
    "武侠": {
        "colors": ["#1a1008", "#2d1810", "#0d1a0d", "#1a1510"],
        "accents": ["#cd853f", "#daa520", "#f4a460", "#d2691e"],
        "elements": ["bamboo", "sword", "mountain", "ink"],
    },
    "科幻": {
        "colors": ["#000814", "#001d3d", "#0a0a1a", "#050520"],
        "accents": ["#00f5ff", "#00bfff", "#1e90ff", "#4169e1"],
        "elements": ["circuit", "star", "ring", "grid"],
    },
    "都市": {
        "colors": ["#1a1a1a", "#2d2d2d", "#0d0d1a", "#1a1020"],
        "accents": ["#ff1493", "#ff69b4", "#00ff7f", "#ffd700"],
        "elements": ["city", "light", "glass", "line"],
    },
    "古代言情": {
        "colors": ["#1a0510", "#2d0a1a", "#1a0a0a", "#200a15"],
        "accents": ["#ff69b4", "#ff1493", "#db7093", "#c71585"],
        "elements": ["flower", "moon", "fan", "butterfly"],
    },
}


# ═══════════════════════════════════════════════════════════════════════
#  Generator Functions
# ═══════════════════════════════════════════════════════════════════════

def generate_character_name(genre: str = "classical", gender: str = "male",
                            count: int = 5, use_ai: bool = False) -> dict:
    style_key = _map_genre_to_name_style(genre, gender)
    chars = NAME_CHARS.get(style_key, NAME_CHARS["classical_male"])

    if use_ai and _ollama_available():
        prompt = (
            f"请为一部{genre}类型的小说生成{count}个{'男性' if gender == 'male' else '女性'}角色名字，"
            f"要求名字有意境、有内涵。只输出名字，每行一个，不要解释。"
        )
        result = _ollama_generate(prompt)
        if result:
            names = [n.strip() for n in result.strip().split('\n') if n.strip()][:count]
            if len(names) >= count:
                return {"names": names, "source": "ai"}

    names = []
    for _ in range(count):
        use_compound = random.random() < 0.15
        surname = random.choice(COMPOUND_SURNAMES) if use_compound else random.choice(SURNAMES)
        name_len = random.choice([1, 2])
        given = ''.join(random.sample(chars, name_len))
        full_name = surname + given
        if full_name not in names:
            names.append(full_name)

    return {"names": names, "source": "template"}


def generate_character_setting(genre: str = "仙侠", gender: str = "male",
                                use_ai: bool = False) -> dict:
    if use_ai and _ollama_available():
        prompt = (
            f"请为一部{genre}类型的小说创建一个{'男性' if gender == 'male' else '女性'}角色设定，"
            f"包含：名字、性格、身世背景、能力特长、外貌描述。请用结构化格式输出。"
        )
        result = _ollama_generate(prompt)
        if result:
            return {"setting": result, "source": "ai"}

    style_key = _map_genre_to_name_style(genre, gender)
    chars = NAME_CHARS.get(style_key, NAME_CHARS["classical_male"])
    surname = random.choice(SURNAMES + COMPOUND_SURNAMES)
    given = ''.join(random.sample(chars, random.choice([1, 2])))
    name = surname + given

    trait_type = random.choices(["positive", "neutral", "negative"], weights=[50, 35, 15])[0]
    traits = random.sample(PERSONALITY_TRAITS[trait_type], min(2, len(PERSONALITY_TRAITS[trait_type])))
    if trait_type != "positive":
        traits.append(random.choice(PERSONALITY_TRAITS["positive"]))

    background = random.choice(BACKGROUNDS)

    genre_key = _map_genre_to_ability_key(genre)
    ability_list = ABILITIES.get(genre_key, ABILITIES["xianxia"])
    abilities = random.sample(ability_list, min(2, len(ability_list)))

    build = random.choice(BUILD_OPTIONS)
    height = random.choice(HEIGHT_OPTIONS)
    face = random.choice(FACE_OPTIONS)
    eye = random.choice(EYE_OPTIONS)
    hair = random.choice(HAIR_OPTIONS)
    extra = random.choice(EXTRA_APPEARANCE)
    appearance = f"{build}，{height}，{face}，{eye}，{hair}。{extra}"

    return {
        "setting": {
            "name": name,
            "gender": "男" if gender == "male" else "女",
            "personality": "、".join(traits),
            "background": background,
            "abilities": "；".join(abilities),
            "appearance": appearance,
        },
        "source": "template",
    }


def generate_background_setting(genre: str = "仙侠", use_ai: bool = False) -> dict:
    if use_ai and _ollama_available():
        prompt = (
            f"请为一部{genre}类型的小说创建世界观设定，包含：世界描述、力量体系、"
            f"主要势力、地理环境。请详细描述，每部分2-3句话。"
        )
        result = _ollama_generate(prompt)
        if result:
            return {"setting": result, "source": "ai"}

    world = WORLD_TYPES.get(genre, WORLD_TYPES["仙侠"])
    desc = random.choice(world["desc"])
    power = random.choice(world["power_system"])
    factions = random.choice(world["factions"])

    geo_template = random.choice(GEOGRAPHY_TEMPLATES)
    geography = geo_template.format(
        plain=random.choice(PLAIN_NAMES),
        sea=random.choice(SEA_NAMES),
        mountain=random.choice(MOUNTAIN_NAMES),
        forest=random.choice(FOREST_NAMES),
        desert=random.choice(DESERT_NAMES),
        num=random.choice(["三", "五", "七", "九"]),
    )

    return {
        "setting": {
            "world_description": desc,
            "power_system": power,
            "factions": factions,
            "geography": geography,
        },
        "source": "template",
    }


def generate_novel_name(genre: str = "仙侠", count: int = 5,
                         use_ai: bool = False) -> dict:
    if use_ai and _ollama_available():
        prompt = (
            f"请为{genre}类型的小说生成{count}个书名，要求朗朗上口、有吸引力。"
            f"只输出书名，每行一个，不要编号和解释。"
        )
        result = _ollama_generate(prompt)
        if result:
            names = [n.strip().strip('《》') for n in result.strip().split('\n') if n.strip()][:count]
            if len(names) >= count:
                return {"names": names, "source": "ai"}

    patterns = NOVEL_TITLE_PATTERNS.get(genre, NOVEL_TITLE_PATTERNS["仙侠"])
    names = set()
    attempts = 0
    while len(names) < count and attempts < 100:
        pattern = random.choice(patterns)
        title = pattern.format(
            adj=random.choice(TITLE_WORDS["adj"]),
            noun=random.choice(TITLE_WORDS["noun"]),
            verb=random.choice(TITLE_WORDS["verb"]),
            place=random.choice(TITLE_WORDS["place"]),
        )
        names.add(title)
        attempts += 1
    return {"names": list(names)[:count], "source": "template"}


def generate_cover_data(title: str, author: str = "",
                         genre: str = "仙侠") -> dict:
    style = COVER_STYLES.get(genre, COVER_STYLES["仙侠"])
    bg_color = random.choice(style["colors"])
    accent = random.choice(style["accents"])
    element = random.choice(style["elements"])

    return {
        "cover": {
            "title": title,
            "author": author or "佚名",
            "genre": genre,
            "bg_color": bg_color,
            "accent_color": accent,
            "element": element,
            "font_style": random.choice(["serif", "fantasy", "elegant"]),
        },
        "source": "template",
    }


def check_ai_status() -> dict:
    available = _ollama_available()
    models = []
    if available:
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
            data = r.json()
            models = [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
    return {"available": available, "models": models}


# ═══════════════════════════════════════════════════════════════════════
#  Novel Analysis & Imitation
# ═══════════════════════════════════════════════════════════════════════

STOP_WORDS = set(
    "的了是在不有我他她它们这那个一与和也就都而但如果因为所以"
    "可以已经还要会被把让从到对又或很更最"
)


def analyze_novel(text: str) -> dict:
    """Analyze novel text and return style metrics."""
    char_count = len(text)

    sentences = re.split(r'[。！？…]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 1]
    sentence_count = len(sentences)
    avg_sentence_len = round(
        sum(len(s) for s in sentences) / max(sentence_count, 1), 1
    )

    paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 1]
    paragraph_count = len(paragraphs)

    dialogue_chars = sum(
        len(m) for m in re.findall(r'[""「」『』].*?[""「」『』]', text)
    )
    dialogue_ratio = round(dialogue_chars / max(char_count, 1), 3)

    try:
        import jieba
        words = [w for w in jieba.cut(text) if w.strip() and len(w) > 1]
    except ImportError:
        words = re.findall(r'[\u4e00-\u9fff]{2,}', text)

    word_count = len(words)
    unique_words = len(set(words))
    vocabulary_richness = round(unique_words / max(word_count, 1), 3)

    filtered = [w for w in words if w not in STOP_WORDS and len(w) >= 2]
    freq = Counter(filtered)
    top_words = freq.most_common(30)

    style_tags = []
    if dialogue_ratio > 0.30:
        style_tags.append("对话密集")
    elif dialogue_ratio > 0.15:
        style_tags.append("对话适中")
    else:
        style_tags.append("叙述为主")

    if avg_sentence_len > 35:
        style_tags.append("长句铺陈")
    elif avg_sentence_len < 15:
        style_tags.append("短句明快")
    else:
        style_tags.append("句式均衡")

    if vocabulary_richness > 0.55:
        style_tags.append("词汇丰富")
    elif vocabulary_richness < 0.3:
        style_tags.append("用词精练")

    desc_words = {"仿佛", "宛如", "好似", "如同", "犹如", "恰似", "像是"}
    desc_count = sum(1 for w in words if w in desc_words)
    if desc_count / max(sentence_count, 1) > 0.05:
        style_tags.append("善用修辞")

    action_puncs = text.count("！") + text.count("？")
    if action_puncs / max(sentence_count, 1) > 0.2:
        style_tags.append("情感强烈")

    return {
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_sentence_len": avg_sentence_len,
        "unique_words": unique_words,
        "vocabulary_richness": vocabulary_richness,
        "dialogue_ratio": dialogue_ratio,
        "top_words": top_words,
        "style_tags": style_tags,
    }


def _chinese_num(n: int) -> str:
    nums = "零一二三四五六七八九十"
    if n <= 10:
        return nums[n]
    if n < 20:
        return "十" + (nums[n - 10] if n > 10 else "")
    if n < 100:
        return nums[n // 10] + "十" + (nums[n % 10] if n % 10 else "")
    return str(n)


def imitate_novel(text: str, analysis: dict, target_length: int = 1000,
                  chapters: int = 1, scope: str = "full",
                  use_ai: bool = False) -> dict:
    """Generate text that imitates the style of the given novel."""

    if scope == "partial":
        text = text[:len(text) // 3]

    if use_ai and _ollama_available():
        sample = text[:3000]
        tags = "、".join(analysis.get("style_tags", []))
        prompt = (
            f"请模仿以下小说的写作风格，创作一篇约{target_length}字、"
            f"共{chapters}个章节的文章。\n"
            f"原文风格特点：{tags}\n"
            f"平均句长：{analysis.get('avg_sentence_len', 20)}字\n"
            f"对话比例：{analysis.get('dialogue_ratio', 0.1)*100:.0f}%\n\n"
            f"原文示例：\n{sample}\n\n"
            f"请模仿上述风格进行创作，不要复述原文。"
        )
        result = _ollama_generate(prompt)
        if result:
            return {"text": result, "source": "ai"}

    # Character-level n-gram Markov chain
    n = 6
    if len(text) < 500:
        n = 3
    elif len(text) < 2000:
        n = 4

    model = defaultdict(list)
    for i in range(len(text) - n):
        key = text[i:i + n]
        model[key].append(text[i + n])

    if not model:
        return {"text": "原文过短，无法生成仿写内容。请上传更长的文本。", "source": "template"}

    keys = list(model.keys())
    chapter_len = target_length // max(chapters, 1)
    output_parts = []

    for ch in range(chapters):
        if chapters > 1:
            output_parts.append(f"\n\n第{_chinese_num(ch + 1)}章\n\n")

        current = random.choice(keys)
        buf = []
        for _ in range(chapter_len):
            if current in model:
                nxt = random.choice(model[current])
                buf.append(nxt)
                current = current[1:] + nxt
            else:
                current = random.choice(keys)

        chunk = ''.join(buf)
        # Trim to last sentence boundary
        last_punc = max(chunk.rfind('。'), chunk.rfind('！'), chunk.rfind('？'))
        if last_punc > 0:
            chunk = chunk[:last_punc + 1]
        output_parts.append(chunk)

    return {"text": ''.join(output_parts), "source": "template"}


# ═══════════════════════════════════════════════════════════════════════
#  File Parsing Helpers
# ═══════════════════════════════════════════════════════════════════════

def parse_pdf(filepath: str) -> str:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return '\n'.join(text_parts)


def parse_docx(filepath: str) -> str:
    from docx import Document
    doc = Document(filepath)
    return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())


# ═══════════════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════════════

def _map_genre_to_name_style(genre: str, gender: str) -> str:
    mapping = {
        "仙侠": "xianxia", "玄幻": "xianxia", "武侠": "wuxia",
        "科幻": "scifi", "都市": "modern", "古代言情": "classical",
        "classical": "classical", "xianxia": "xianxia", "wuxia": "wuxia",
        "scifi": "scifi", "modern": "modern",
    }
    base = mapping.get(genre, "classical")
    if base == "classical":
        return f"classical_{'female' if gender == 'female' else 'male'}"
    return base


def _map_genre_to_ability_key(genre: str) -> str:
    mapping = {
        "仙侠": "xianxia", "玄幻": "xianxia", "武侠": "wuxia",
        "科幻": "scifi", "都市": "modern", "古代言情": "modern",
    }
    return mapping.get(genre, "xianxia")
