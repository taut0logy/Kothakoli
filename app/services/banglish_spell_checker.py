from rapidfuzz import process, fuzz
from typing import List, Tuple
import logging

# Sample dictionary of common Banglish words
common_banglish_words = [
    "ami", "tumi", "apni", "kemon", "acho", "achen", "bhalo", 
    "kothay", "ki", "korcho", "korchen", "bolo", "bolun", "dhaka",
    "bangla", "english", "shikhi", "shikhbo", "jani", "janina",
    "bujhi", "bujhina", "khub", "onek", "sundor", "habijabi",
    "kotha", "keno", "hobe", "koro", "korun", "jacche",

    # Additional 200 Banglish words
    "sokal", "bikel", "rat", "ghor", "bari", "bazar", "dokaan",
    "rasta", "gari", "bike", "bus", "taxi", "rickshaw", "train",
    "school", "college", "university", "hospital", "clinic",
    "restaurant", "hotel", "cafe", "park", "cinema", "theater",
    "library", "supermarket", "bank", "atm", "post_office",
    "police", "fire_station", "temple", "mosque", "church",
    "friend", "bondhu", "sathi", "dada", "didi", "bhai", "bhabi",
    "mama", "khala", "tushar", "sajib", "tanjim", "sadia",
    "kajal", "maruf", "nimra", "rajib", "rimjhim", "sourav",
    "tamim", "tina", "usha", "vicky", "yasmin", "zahid",
    "shona", "baba", "mama", "chacha", "teta", "mausi",
    "khoka", "boudi", "pita", "mata", "shonar", "pagol",
    "sundori", "shuvo", "proshno", "uttor", "bistar", "noyon",
    "chokh", "hath", "poyla", "boka", "dim", "mach", "taka",
    "pani", "cha", "dudh", "roti", "daal", "bhaji", "biriyani",
    "kacchi", "shal", "sabji", "morich", "ada", "shaak",
    "mitha", "gura", "moi", "murgi", "gosht", "miso", "moyla",
    "gola", "machher_jhol", "bhuna", "tandoori", "shorba",
    "chai", "mishti", "lidha", "jhal", "teekha", "nasta",
    "biscuit", "jam", "butter", "cheese", "ketchup", "mustard",
    "mayonnaise", "pickle", "salt", "chini", "sugar", "ghee",
    "tel", "goru", "goru_mangsho", "begun", "aaloo", "pyaz",
    "rosun", "kacha", "pakha", "soup", "salad", "samosa",
    "singara", "cutlet", "kathi_roll", "pitha", "doi",
    "lassi", "shorbot", "bottle", "glass", "cup", "plate",
    "katori", "bhagona", "chula", "kachchi", "kamla", "ghuri",
    "patay", "baji", "ranna", "bhaji", "gajar", "shosha",
    "kumro", "kamoch", "khichuri", "bhapa", "dum", "jhalmuri",
    "fuchka", "cha_bag", "banglar_ganer_sangeet", "gaan",
    "bajar", "praderito", "nrittyo", "natok", "bollywood",
    "sudoku", "khela", "shorir", "protidin", "shongshkar",
    "sopno", "mon", "bhabna", "bhul", "shorir", "thanda",
    "gorom", "ghum", "sustha", "choloman", "shishuder",
    "kichu", "kichute", "kintu", "jodi", "jodi_na",
    "tarpor", "sathik", "soman", "otomatik", "monojog",
    "bishesh", "bahar", "bhitor", "aboshesh", "shuru",
    "ses", "kheya", "khaowa", "pawa", "dawa", "dorkar",
    "proyojon", "shomoy", "din", "ratri", "soptaho", "mas",
    "bochor", "shishur", "bondhu", "shikkhok", "shikkha",
    "khela", "gana", "shiksha", "chintito", "chinta", "bhabna",
    "bhab", "shanti", "shikhkha", "shikh", "shikhe",
    "shikhon", "shikhya", "shikhaya", "shikhon_kora",
    "shikhon_pawa", "shikhon_shesh", "shikhon_shuru", "shikhon_bishesh",
    "shikhon_kichu", "shikhon_jodi", "shikhon_tarpor",
    "shikhon_sothik", "shikhon_soman", "shikhon_otomatik",
    "shikhon_monojog", "shikhon_bahar", "shikhon_bhitor",
    "shikhon_aboshesh", "shikhon_kheya", "shikhon_khaowa",
    "shikhon_pawa", "shikhon_dawa", "shikhon_dorkar",
    "shikhon_proyojon", "shikhon_shomoy", "shikhon_din",
    "shikhon_ratri", "shikhon_soptaho", "shikhon_mas",
    "shikhon_bochor", "shikhon_shishur",

    # Common Expressions
    "shubho", "shuvo_sondha", "shuvo_bela", "shuvo_ratri",
    "biday", "shuvo_biday", "shuvo_shondha", "shuvo_din",
    "bhalo_thakben", "shuvo_prottasha", "shuvo_ujjol",
    "shuvo_shurute", "shuvo_shesh",
    
    # Common Verbs
    "khaoya", "dawa", "jawa", "ashha", "dekha", "shona",
    "bolte", "chawa", "ghurbe", "shikhbe", "kora", "jana",
    "bhabi", "bhebe", "pona", "pona", "pona", "pona",
    "pona", "pona", "pona", "pona",

    # Common Nouns
    "shishur", "ghor", "shohor", "gaon", "pahar", "nodi",
    "jogot", "shomoy", "shomashya", "shomadhan", "bondhon",
    "shomporko", "sristi", "prakriti", "manush", "shishur",
    "shikkhok", "shikkhika", "shikkhoker", "shikkhita",
    "shikkhit", "shikkha_kendra", "shikkha_bibag", "shikkha_paddhati",
    "shikkha_samogrik", "shikkha_vyavastha", "shikkha_niti",
    "shikkha_prokolpo", "shikkha_somporke", "shikkha_bichar",
    "shikkha_madhyam", "shikkha_dorkar",
    
    # Additional Common Words
    "shorol", "kothin", "sukho", "dukkho", "shukher", "dukkher",
    "sukhi", "dukkhi", "shokto", "kom", "beshi", "kichu",
    "shokol", "sob", "sobaike", "sokal_sondha", "sokal_bikel",
    "ghurti", "ghurti_kora", "ghurti_gora", "ghurti_jawa",
    "ghurti_ashha", "ghurti_dekha", "ghurti_shona",
    "ghurti_bolte", "ghurti_chawa", "ghurti_ghurbe",
    "ghurti_shikhbe", "ghurti_kora", "ghurti_jana",
    "ghurti_bhabi", "ghurti_bhebe", "ghurti_pona",
    "ghurti_shorol", "ghurti_kothin", "ghurti_sukho",
    "ghurti_dukkho", "ghurti_shukher", "ghurti_dukkher",
    "ghurti_sukhi", "ghurti_dukkhi", "ghurti_shokto",
    "ghurti_kom", "ghurti_beshi", "ghurti_kichu",
    "ghurti_shokol", "ghurti_sob", "ghurti_sobaike",
    "ghurti_sokal_sondha", "ghurti_sokal_bikel",

    # Common Adjectives
    "lal", "nil", "shalok", "kalo", "hok", "sukhi", "dukkhi",
    "boro", "choto", "hote", "boroboro", "kharap", "bhalo",
    "shundor", "kotha", "sasto", "shorir", "lomba", "kom",
    "shomoshya", "shomadhan", "bosta", "bishal", "patla",
    "ghurte", "ghurte", "ghurte",

    # Common Adverbs
    "khub", "onek", "kharap", "shorol", "dheere", "turu",
    "kom", "besh", "khub_besha", "onek_besha", "shighro",
    "sheshe", "shurute", "shesh", "modhye", "porer",
    "age", "porer", "sorate",

    # Common Pronouns
    "tader", "tader_she", "tader_tumi", "tader_apni",
    "tader_ami", "tader_kemon", "tader_acho", "tader_achen",
    "tader_bhalo", "tader_kothay", "tader_ki",
    "tader_korcho", "tader_korchen", "tader_bolo",
    "tader_bolun", "tader_dhaka", "tader_bangla",
    "tader_english", "tader_shikhi", "tader_shikhbo",
    "tader_jani", "tader_janina", "tader_bujhi",
    "tader_bujhina", "tader_khub", "tader_onek",
    "tader_sundor", "tader_habijabi", "tader_kotha",
    "tader_keno", "tader_hobe", "tader_koro",
    "tader_korun", "tader_jacche",
    
    # Common Question Words
    "kothay", "keno", "ki", "koto", "kemon", "ke", "kiser",
    "keu", "kibhabe", "keno", "kaje", "kisu", "kibhabe",
    "khuje", "koto_taka", "kotha_theke", "konta",
    
    # Common Connectors
    "ebong", "ba", "kintu", "taile", "tai", "jodi", "jokhon",
    "jokhon", "tokhon", "karon", "tabe", "sobcheye",
    "jemon", "aram", "eta", "eta_holo", "eta_to", "eta_khujchi",
    "eta_khujte", "eta_khujchi_na",

    # Miscellaneous
    "shanto", "shokto", "ghotona", "ghoti", "ghoti_holo",
    "ghoti_ache", "ghoti_khujchi", "ghoti_khujte", "ghoti_khujche",
    "ghoti_khujben", "ghoti_khujbo", "ghoti_khobor",
    "ghoti_khobor_paoa", "ghoti_khobor_kharaj", "ghoti_khobor_nai",
    "ghoti_khobor_khaowa", "ghoti_khobor_jawa", "ghoti_khobor_ponano",
    "ghoti_khobor_bhul", "ghoti_khobor_shothik",
    
    # Days of the Week
    "shonibar", "roibur", "mongolbar", "buddhbar", "shukribar",
    "shonibar", "robibar", "mongolbar", "buddhbar", "shukribar",

    # Months
    "janoir", "februari", "march", "april", "may", "june",
    "july", "august", "september", "october", "november",
    "december",

    # Time-related
    "ghonta", "minute", "second", "kal", "agamikal", "shokal",
    "dupurer", "ratir", "shondha", "bikel", "sokal_bikel",

    # Common Places
    "shohor", "gaon", "pahar", "nodir_paaare", "shorshoter",
    "shomudro", "upajon", "lokkhaghor", "batash_bari",

    # Common Activities
    "khela", "gana", "nach", "shikka", "ranna", "ghurte",
    "kora", "jawa", "asbe", "ashbe", "gora", "khatna",
    "pora", "likha", "porashona", "shomprosaron",
    
    # Emotions
    "khushi", "dukhi", "bhoy", "shanti", "agrogroho",
    "utshaho", "chinta", "bhabna", "birokto", "bhul",
    
    # Nature
    "brikkho", "ful", "pata", "dour", "shishi", "chara",
    "ghorer_bahar", "bahire", "bhitore", "pata_gara",
    
    # Miscellaneous Common Words
    "shubho_biday", "shubho_din", "shubho_shondha", "shubho_ratri",
    "shubho_sokal", "shubho_bikel", "shubho_ujjol",
    "shubho_shurute", "shubho_shesh", "shubho_prottasha",
    "shubho_beshe", "shubho_kichu", "shubho_bondhon",
    "shubho_sristi", "shubho_prakriti", "shubho_manush",
    "shubho_shikkha", "shubho_shorir",
    
    # Common Household Items
    "television", "fridge", "fan", "air_conditioner",
    "microwave", "stove", "heater", "light", "bulb",
    "chair", "table", "sofa", "bed", "khat", "jhulna",
    "book", "pen", "kalam", "pencil", "notebook", "kapi",
    "katori", "plate", "glass", "bottle", "jar", "thali",
    "cutlery", "katori", "chopper", "spoon", "fork",
    "knife", "ladle", "sieve", "bowl", "bucket", "mug",
    "towel", "sheet", "blanket", "curtain", "carpet",
    "clock", "mirror", "fan", "heater", "cooler",
    
    # Common Body Parts
    "shorir", "matha", "chokh", "kanna", "naak", "mukh",
    "hath", "poyla", "pa", "kono", "kan", "pant", "paya",
    "korta", "bhitor", "pait", "pech", "pakha",
    
    # Common Colors
    "lal", "nil", "shalok", "kalo", "sobuj", "holud",
    "kashful", "peelo", "shobuj", "komola", "bainguni",
    "gulabi", "chakra", "swarna", "charai", "bejad",
    
    # Common Animals
    "goru", "bacha", "kukuri", "dim", "mach", "kukur",
    "bata", "morog", "haas", "bagh", "hati", "sher",
    "khargosh", "kabutar", "koyla", "kalo_mach",
    "chapla", "singara", "dakshin", "vutor", "sher",
    "haash", "chhutir", "tota", "goru_mangsho",

    # Common Fruits
    "sorbot", "ful", "fol", "kathal", "jam", "jamun",
    "am", "bael", "aam", "kola", "komola", "sembol",
    "jambu", "mosambi", "mangsho", "nut", "badam",
    "kisher", "pista", "shera", "kathal", "nariyal",
    "lebu", "kichu", "anchole", "sebo", "litchi",

    # Common Vegetables
    "aaloo", "begun", "aalur_dom", "padma", "gajor",
    "shosha", "kumro", "tomato", "pyaj", "rosun",
    "kak", "shak", "kobi", "sorisha", "chaula",
    "shimul", "bhendi", "kacha", "pakha", "paneer",
    "shilpo", "sojja", "sabji", "taka", "kakro",
    
    # Common Weather Terms
    "gori", "biporjoy", "barish", "dhula", "hawa",
    "kandhi", "badal", "bijli", "toofan", "hail",
    "muri", "jhora", "jor", "sheetal", "garmi",
    "thanda", "abash", "bata", "bishaal_bata",

    # Common Transportation
    "gari", "bike", "bus", "taxi", "rickshaw", "train",
    "plane", "ship", "cycle", "auto", "metro", "subway",
    "lorry", "truck", "car", "scooter", "van",
    
    # Common Technology
    "computer", "laptop", "smartphone", "tablet",
    "charger", "headphone", "speaker", "camera",
    "printer", "router", "modem", "usb", "bluetooth",
    "wifi", "software", "hardware", "app", "website",
    "internet", "keyboard", "mouse", "monitor",
    
    # Common Household Activities
    "ranna", "safai", "dhona", "porishkar", "mash", "chash",
    "basha_bari", "ghurte_jawa", "ghurte_ashha",
    "ghurte_dekha", "ghurte_kotha", "ghurte_bolo",
    "ghurte_shikhbe", "ghurte_korcho", "ghurte_korchen",
    
    # Common Greetings
    "shubho_biday", "shubho_din", "shubho_shondha",
    "shubho_ratri", "shubho_sokal", "shubho_bikel",
    "shubho_ujjol", "shubho_shurute", "shubho_shesh",
    "shubho_prottasha",

    # Common Miscellaneous
    "kichu", "besh", "kom", "onno", "choto", "boro",
    "shorol", "kothin", "sukho", "dukkho", "shokto",
    "sundor", "bhalo", "khub", "onek", "shono",
    "janate", "bujhate", "bolte", "dekha", "shona",
    "khaoya", "kora", "jana", "jana_na", "bhabi",
    "bhebe", "pona", "pona_na", "pona_kichu",
    "pona_shorol", "pona_kothin", "pona_sukho",
    "pona_dukkho", "pona_bhalo", "pona_khub",
    "pona_onnek", "pona_sundor"
]

logger = logging.getLogger(__name__)

def suggest_corrections(word: str, threshold: int = 65) -> List[Tuple[str, int]]:
    """
    Suggests corrections for a potentially misspelled Banglish word.
    """
    try:
        # Get top 3 matches using weighted ratio
        matches = process.extract(
            word,
            common_banglish_words,
            scorer=fuzz.WRatio,
            limit=3
        )
        
        # Filter matches above threshold and ensure proper tuple unpacking
        suggestions = []
        for match in matches:
            if isinstance(match, tuple) and len(match) >= 2:
                word_match, score = match[0], match[1]
                if score >= threshold:
                    suggestions.append((word_match, score))
            
        return suggestions
        
    except Exception as e:
        logger.error(f"Error in suggest_corrections: {e}")
        return []

def check_banglish_text(text: str) -> List[str]:
    """
    Checks a Banglish text and returns spelling suggestions.
    """
    try:
        words = text.lower().split()
        suggestions = []
        
        for word in words:
            word_suggestions = suggest_corrections(word)
            if word_suggestions:
                for suggested_word, score in word_suggestions:
                    if score > 65 and suggested_word != word:
                        suggested_text = text.replace(word, suggested_word)
                        if suggested_text not in suggestions:
                            suggestions.append(suggested_text)
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error in check_banglish_text: {e}")
        return []

# Make sure this function is available for import
__all__ = ['check_banglish_text', 'suggest_corrections']

# Test examples
if __name__ == "__main__":
    # Example 1: Common misspellings
    check_banglish_text("amee kmn acho")
    
    # Example 2: Multiple word variations
    check_banglish_text("tume valo acho kemon")
    
    # Example 3: Words requiring more fuzzy matching
    check_banglish_text("bujina janena kotha") 