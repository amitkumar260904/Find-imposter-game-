import http.server
import socketserver
import webbrowser
import threading
import json
import random
import os
import secrets
import time
import string
import urllib.parse
import signal
import sys

PORT = int(os.environ.get("PORT", 8000))
START_TIME = time.time()
HINT_TIMER_SECONDS = 7       # 7-second countdown timer when hint is viewed
LAST_GUESS_SECONDS = 25      # Imposter last-stand word guess window

# ===========================================================================
# DIFFICULTY LEVELS (1 to 5 — Friendly & Progressive)
# ===========================================================================
LEVELS = {
    1: {
        "level": 1, "name": "Beginner", "name_hi": "शुरुआती", "tag": "SUPER EASY",
        "rounds": 2, "hint_style": "full", "last_guess": False,
        "crew_pts": 100, "imposter_pts": 150, "color": "#00ff66",
        "desc": "Very simple words • Full clear hint (7s) • 2 clue rounds",
        "desc_hi": "बहुत आसान शब्द • पूरा हिंट (7 सेकंड) • 2 क्लू राउंड",
    },
    2: {
        "level": 2, "name": "Easy", "name_hi": "आसान", "tag": "EASY",
        "rounds": 2, "hint_style": "full", "last_guess": False,
        "crew_pts": 125, "imposter_pts": 175, "color": "#00f3ff",
        "desc": "Everyday familiar words • Full clear hint (7s) • 2 clue rounds",
        "desc_hi": "रोज़मर्रा के आसान शब्द • पूरा हिंट (7 सेकंड) • 2 क्लू राउंड",
    },
    3: {
        "level": 3, "name": "Medium", "name_hi": "मध्यम", "tag": "MEDIUM",
        "rounds": 2, "hint_style": "full", "last_guess": False,
        "crew_pts": 150, "imposter_pts": 225, "color": "#b026ff",
        "desc": "Fun places & objects • Helpful hint (7s) • 2 clue rounds",
        "desc_hi": "मज़ेदार जगहें और चीज़ें • मददगार हिंट (7 सेकंड) • 2 क्लू राउंड",
    },
    4: {
        "level": 4, "name": "Smart", "name_hi": "स्मार्ट", "tag": "MODERATE",
        "rounds": 3, "hint_style": "subtle", "last_guess": True,
        "crew_pts": 225, "imposter_pts": 325, "color": "#ff9900",
        "desc": "Fun creative words • Subtle hint (7s) • 3 rounds • Last-Stand",
        "desc_hi": "रोचक शब्द • हल्का हिंट (7 सेकंड) • 3 राउंड • अंतिम अनुमान",
    },
    5: {
        "level": 5, "name": "Pro", "name_hi": "प्रो", "tag": "CHALLENGE",
        "rounds": 3, "hint_style": "subtle", "last_guess": True,
        "crew_pts": 300, "imposter_pts": 450, "color": "#ff003c",
        "desc": "Clever mystery words • Short hint (7s) • 3 rounds • Last-Stand",
        "desc_hi": "चतुर रहस्यमय शब्द • छोटा हिंट (7 सेकंड) • 3 राउंड • अंतिम अनुमान",
    },
}

RANKS = [
    (0, "Rookie"),
    (200, "Operative"),
    (500, "Investigator"),
    (900, "Special Agent"),
    (1500, "Master Spy"),
    (2500, "Phantom Legend"),
]

def _get_rank(score):
    rank = RANKS[0][1]
    for threshold, title in RANKS:
        if score >= threshold:
            rank = title
    return rank

# ===========================================================================
# BILINGUAL WORD BANK (75 FUN & APPROACHABLE WORDS ACROSS 5 LEVELS)
# ===========================================================================
WORD_BANK = [
    # --- LEVEL 1: BEGINNER (SUPER EASY) ---
    {"level": 1, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Apple", "imposter_hint": "A crunchy red or green fruit.", "subtle_hint": "Keeps the doctor away."},
     "hi": {"word": "सेब", "imposter_hint": "एक कुरकुरा लाल या हरा फल।", "subtle_hint": "रोज़ खाने से सेहत अच्छी रहती है।"}},
    {"level": 1, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Water", "imposter_hint": "A clear drink everyone needs every day.", "subtle_hint": "Has no taste or color."},
     "hi": {"word": "पानी", "imposter_hint": "एक साफ पेय जो हर दिन ज़रूरी है।", "subtle_hint": "इसका कोई रंग या स्वाद नहीं होता।"}},
    {"level": 1, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Tea", "imposter_hint": "A hot drink people enjoy in the morning.", "subtle_hint": "Served in a cup with snacks."},
     "hi": {"word": "चाय", "imposter_hint": "सुबह पी जाने वाली गर्म चीज़।", "subtle_hint": "कप में बिस्कुट के साथ पीते हैं।"}},
    {"level": 1, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Mango", "imposter_hint": "A sweet yellow summer fruit.", "subtle_hint": "Called the king of fruits."},
     "hi": {"word": "आम", "imposter_hint": "गर्मियों का मीठा पीला फल।", "subtle_hint": "फलों का राजा कहा जाता है।"}},
    {"level": 1, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Cake", "imposter_hint": "A sweet baked treat cut on birthdays.", "subtle_hint": "Often topped with candles."},
     "hi": {"word": "केक", "imposter_hint": "जन्मदिन पर काटा जाने वाला मीठा व्यंजन।", "subtle_hint": "इस पर मोमबत्ती लगाई जाती है।"}},
    {"level": 1, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Dog", "imposter_hint": "A loyal pet animal that barks.", "subtle_hint": "Loves chasing balls."},
     "hi": {"word": "कुत्ता", "imposter_hint": "एक वफादार पालतू जानवर जो भौंकता है।", "subtle_hint": "गेंद पकड़ना पसंद करता है।"}},
    {"level": 1, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Cat", "imposter_hint": "A small cute pet that says meow.", "subtle_hint": "Loves drinking milk."},
     "hi": {"word": "बिल्ली", "imposter_hint": "एक छोटा पालतू जानवर जो म्याऊं करता है।", "subtle_hint": "दूध पीना बहुत पसंद है।"}},
    {"level": 1, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Sun", "imposter_hint": "Bright and warm in the daytime sky.", "subtle_hint": "Rises every morning."},
     "hi": {"word": "सूरज", "imposter_hint": "दिन में आसमान में चमकता और गर्मी देता है।", "subtle_hint": "हर सुबह उगता है।"}},
    {"level": 1, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Moon", "imposter_hint": "Shines softly in the night sky.", "subtle_hint": "Changes shape through the month."},
     "hi": {"word": "चाँद", "imposter_hint": "रात के आसमान में चमकता है।", "subtle_hint": "महीने में इसका आकार बदलता है।"}},
    {"level": 1, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Rain", "imposter_hint": "Water drops falling from clouds.", "subtle_hint": "Makes you open an umbrella."},
     "hi": {"word": "बारिश", "imposter_hint": "बादलों से गिरने वाली पानी की बूंदें।", "subtle_hint": "इसमें छाता खोलना पड़ता है।"}},
    {"level": 1, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Chair", "imposter_hint": "Furniture with four legs that you sit on.", "subtle_hint": "Kept around a table."},
     "hi": {"word": "कुर्सी", "imposter_hint": "चार पैरों वाला फर्नीचर जिस पर बैठते हैं।", "subtle_hint": "मेज़ के पास रखी जाती है।"}},
    {"level": 1, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Book", "imposter_hint": "Has many pages that you read.", "subtle_hint": "Found in school bags."},
     "hi": {"word": "किताब", "imposter_hint": "इसमें बहुत से पन्ने होते हैं जिन्हें पढ़ते हैं।", "subtle_hint": "स्कूल बैग में मिलती है।"}},
    {"level": 1, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Bed", "imposter_hint": "Soft furniture where you sleep at night.", "subtle_hint": "Has a pillow and blanket."},
     "hi": {"word": "बिस्तर", "imposter_hint": "जहाँ आप रात को सोते हैं।", "subtle_hint": "इस पर तकिया और चादर होती है।"}},
    {"level": 1, "category": "Gadgets", "category_hi": "गैजेट्स",
     "en": {"word": "Mobile Phone", "imposter_hint": "A pocket gadget for calls and messages.", "subtle_hint": "Needs daily charging."},
     "hi": {"word": "मोबाइल फोन", "imposter_hint": "कॉल और मैसेज के लिए जेब का गैजेट।", "subtle_hint": "रोज़ चार्ज करना पड़ता है।"}},
    {"level": 1, "category": "Transport", "category_hi": "परिवहन",
     "en": {"word": "Car", "imposter_hint": "A four-wheeled vehicle driven on roads.", "subtle_hint": "Has a steering wheel."},
     "hi": {"word": "कार", "imposter_hint": "सड़क पर चलने वाला चार पहियों का वाहन।", "subtle_hint": "इसमें स्टीयरिंग व्हील होता है।"}},

    # --- LEVEL 2: EASY (CASUAL) ---
    {"level": 2, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Pizza", "imposter_hint": "A round cheesy food cut into slices.", "subtle_hint": "Delivered in a flat square box."},
     "hi": {"word": "पिज़्ज़ा", "imposter_hint": "गोल चीज़ी खाना जिसे टुकड़ों में काटते हैं।", "subtle_hint": "चौकोर डिब्बे में आता है।"}},
    {"level": 2, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Ice Cream", "imposter_hint": "Cold, sweet dessert that melts fast.", "subtle_hint": "Eaten in cones or cups."},
     "hi": {"word": "आइस क्रीम", "imposter_hint": "ठंडी मीठी चीज़ जो जल्दी पिघलती है।", "subtle_hint": "कोन या कप में खाते हैं।"}},
    {"level": 2, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Chocolate", "imposter_hint": "A sweet brown treat everyone loves.", "subtle_hint": "Often gifted on celebrations."},
     "hi": {"word": "चॉकलेट", "imposter_hint": "मीठी भूरी चीज़ जो सबको पसंद है।", "subtle_hint": "खास मौकों पर उपहार में देते हैं।"}},
    {"level": 2, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Banana", "imposter_hint": "A long yellow fruit you peel to eat.", "subtle_hint": "Monkeys love it."},
     "hi": {"word": "केला", "imposter_hint": "लंबा पीला फल जिसे छीलकर खाते हैं।", "subtle_hint": "बंदरों को बहुत पसंद है।"}},
    {"level": 2, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "School", "imposter_hint": "A place where students go to learn.", "subtle_hint": "Has classrooms and a bell."},
     "hi": {"word": "स्कूल", "imposter_hint": "जहाँ छात्र पढ़ने और सीखने जाते हैं।", "subtle_hint": "यहाँ कक्षाएं और घंटी होती हैं।"}},
    {"level": 2, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Beach", "imposter_hint": "A sunny place with sand and ocean waves.", "subtle_hint": "Great for building sandcastles."},
     "hi": {"word": "समुद्र तट", "imposter_hint": "रेत, पानी और लहरों वाली जगह।", "subtle_hint": "यहाँ रेत के घर बनाते हैं।"}},
    {"level": 2, "category": "Sports", "category_hi": "खेल",
     "en": {"word": "Cricket", "imposter_hint": "A popular sport played with a bat and ball.", "subtle_hint": "Has wickets and sixes."},
     "hi": {"word": "क्रिकेट", "imposter_hint": "बल्ले और गेंद से खेला जाने वाला लोकप्रिय खेल।", "subtle_hint": "इसमें विकेट और छक्के होते हैं।"}},
    {"level": 2, "category": "Sports", "category_hi": "खेल",
     "en": {"word": "Football", "imposter_hint": "A team game where you kick a ball into a goal.", "subtle_hint": "Played on a green field."},
     "hi": {"word": "फुटबॉल", "imposter_hint": "पैर से गेंद मारकर गोल करने का खेल।", "subtle_hint": "हरे मैदान पर खेला जाता है।"}},
    {"level": 2, "category": "Gadgets", "category_hi": "गैजेट्स",
     "en": {"word": "Television", "imposter_hint": "A big screen watched at home with a remote.", "subtle_hint": "Shows movies and news."},
     "hi": {"word": "टेलीविज़न", "imposter_hint": "घर में रिमोट से देखी जाने वाली बड़ी स्क्रीन।", "subtle_hint": "इस पर फिल्में और खबरें आती हैं।"}},
    {"level": 2, "category": "Gadgets", "category_hi": "गैजेट्स",
     "en": {"word": "Fan", "imposter_hint": "Spins fast to keep a room breezy.", "subtle_hint": "Usually hangs on the ceiling."},
     "hi": {"word": "पंखा", "imposter_hint": "घूमकर कमरे में हवा देता है।", "subtle_hint": "अक्सर छत पर लगा होता है।"}},
    {"level": 2, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Umbrella", "imposter_hint": "Protects you from rain or hot sun.", "subtle_hint": "Folds up when dry."},
     "hi": {"word": "छाता", "imposter_hint": "बारिश या तेज धूप से बचाता है।", "subtle_hint": "इस्तेमाल के बाद बंद कर देते हैं।"}},
    {"level": 2, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Clock", "imposter_hint": "Shows the hours and minutes on a wall.", "subtle_hint": "Ticks all day and night."},
     "hi": {"word": "घड़ी", "imposter_hint": "दीवार पर समय बताती है।", "subtle_hint": "दिन-रात टिक-टिक करती है।"}},
    {"level": 2, "category": "Transport", "category_hi": "परिवहन",
     "en": {"word": "Bicycle", "imposter_hint": "A two-wheeled ride powered by pedals.", "subtle_hint": "Has a handlebar and bell."},
     "hi": {"word": "साइकिल", "imposter_hint": "पैडल से चलने वाला दो पहियों का वाहन।", "subtle_hint": "इसमें हैंडल और घंटी होती है।"}},
    {"level": 2, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Elephant", "imposter_hint": "A huge gray animal with a long trunk.", "subtle_hint": "Has big flapping ears."},
     "hi": {"word": "हाथी", "imposter_hint": "लंबी सूंड वाला बहुत बड़ा जानवर।", "subtle_hint": "इसके बड़े-बड़े कान होते हैं।"}},
    {"level": 2, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Lion", "imposter_hint": "A wild big cat called king of the jungle.", "subtle_hint": "Has a loud roar."},
     "hi": {"word": "शेर", "imposter_hint": "जंगल का राजा कहा जाने वाला जानवर।", "subtle_hint": "इसकी दहाड़ बहुत तेज़ होती है।"}},

    # --- LEVEL 3: MEDIUM (NORMAL) ---
    {"level": 3, "category": "Gadgets", "category_hi": "गैजेट्स",
     "en": {"word": "Laptop", "imposter_hint": "A folding portable computer for work or study.", "subtle_hint": "Has a built-in keyboard and screen."},
     "hi": {"word": "लैपटॉप", "imposter_hint": "काम या पढ़ाई के लिए फोल्ड होने वाला कंप्यूटर।", "subtle_hint": "कीबोर्ड और स्क्रीन एक साथ होते हैं।"}},
    {"level": 3, "category": "Gadgets", "category_hi": "गैजेट्स",
     "en": {"word": "Refrigerator", "imposter_hint": "Keeps food and drinks cold in the kitchen.", "subtle_hint": "Its light turns on when you open the door."},
     "hi": {"word": "फ्रिज", "imposter_hint": "रसोई में खाने-पीने की चीज़ों को ठंडा रखता है।", "subtle_hint": "दरवाज़ा खोलते ही अंदर बत्ती जलती है।"}},
    {"level": 3, "category": "Gadgets", "category_hi": "गैजेट्स",
     "en": {"word": "Washing Machine", "imposter_hint": "Cleans dirty clothes with water and soap.", "subtle_hint": "Spins clothes dry inside a drum."},
     "hi": {"word": "वॉशिंग मशीन", "imposter_hint": "पानी और साबुन से कपड़े धोने की मशीन।", "subtle_hint": "कपड़ों को तेज़ी से घुमाकर साफ करती है।"}},
    {"level": 3, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Hospital", "imposter_hint": "A building where doctors treat sick people.", "subtle_hint": "Ambulances arrive here."},
     "hi": {"word": "अस्पताल", "imposter_hint": "जहाँ डॉक्टर बीमार लोगों का इलाज करते हैं।", "subtle_hint": "यहाँ एम्बुलेंस आती है।"}},
    {"level": 3, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Library", "imposter_hint": "A quiet room full of shelves and books.", "subtle_hint": "Everyone whispers here."},
     "hi": {"word": "पुस्तकालय", "imposter_hint": "किताबों की अलमारियों से भरी शांत जगह।", "subtle_hint": "यहाँ शांत रहना ज़रूरी है।"}},
    {"level": 3, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Airport", "imposter_hint": "Where airplanes take off and land.", "subtle_hint": "Travelers carry luggage and boarding passes."},
     "hi": {"word": "हवाई अड्डा", "imposter_hint": "जहाँ से हवाई जहाज़ उड़ते और उतरते हैं।", "subtle_hint": "यात्री सामान और टिकट लेकर जाते हैं।"}},
    {"level": 3, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Restaurant", "imposter_hint": "A place where you order meals from a menu.", "subtle_hint": "Waiters bring food to your table."},
     "hi": {"word": "रेस्टोरेंट", "imposter_hint": "जहाँ मेन्यू देखकर खाना ऑर्डर करते हैं।", "subtle_hint": "वेटर मेज़ पर खाना लाते हैं।"}},
    {"level": 3, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Park", "imposter_hint": "An open green place with trees and benches.", "subtle_hint": "Great for morning walks and kids."},
     "hi": {"word": "पार्क", "imposter_hint": "पेड़ों और बेंचों वाली खुली हरी जगह।", "subtle_hint": "सुबह की सैर के लिए बढ़िया जगह।"}},
    {"level": 3, "category": "Professions", "category_hi": "पेशे",
     "en": {"word": "Doctor", "imposter_hint": "A medical expert who cures patients.", "subtle_hint": "Wears a white coat."},
     "hi": {"word": "डॉक्टर", "imposter_hint": "मरीज़ों का इलाज करने वाले विशेषज्ञ।", "subtle_hint": "सफेद कोट पहनते हैं।"}},
    {"level": 3, "category": "Professions", "category_hi": "पेशे",
     "en": {"word": "Teacher", "imposter_hint": "A person who teaches lessons in class.", "subtle_hint": "Writes on a board and checks homework."},
     "hi": {"word": "शिक्षक", "imposter_hint": "कक्षा में छात्रों को पढ़ाने वाले व्यक्ति।", "subtle_hint": "बोर्ड पर लिखते हैं और होमवर्क जांचते हैं।"}},
    {"level": 3, "category": "Professions", "category_hi": "पेशे",
     "en": {"word": "Police", "imposter_hint": "Officers who protect people and catch criminals.", "subtle_hint": "Wear uniforms and patrol streets."},
     "hi": {"word": "पुलिस", "imposter_hint": "लोगों की सुरक्षा करने और कानून बचाने वाले।", "subtle_hint": "वर्दी पहनकर गश्त लगाते हैं।"}},
    {"level": 3, "category": "Transport", "category_hi": "परिवहन",
     "en": {"word": "Train", "imposter_hint": "A long vehicle running on iron tracks.", "subtle_hint": "Stops at railway stations."},
     "hi": {"word": "ट्रेन", "imposter_hint": "लोहे की पटरी पर चलने वाला लंबा वाहन।", "subtle_hint": "स्टेशनों पर रुकती है।"}},
    {"level": 3, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Peacock", "imposter_hint": "A colorful bird that dances in the rain.", "subtle_hint": "Has bright blue and green feathers."},
     "hi": {"word": "मोर", "imposter_hint": "बारिश में नाचने वाला रंग-बिरंगा पक्षी।", "subtle_hint": "इसके नीले-हरे सुंदर पंख होते हैं।"}},
    {"level": 3, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Mountain", "imposter_hint": "A very tall natural peak touching the clouds.", "subtle_hint": "Often topped with snow."},
     "hi": {"word": "पहाड़", "imposter_hint": "बादलों को छूने वाली बहुत ऊँची चोटी।", "subtle_hint": "ऊपर अक्सर बर्फ जमी होती है।"}},
    {"level": 3, "category": "Food", "category_hi": "खान-पान",
     "en": {"word": "Coffee", "imposter_hint": "A dark, strong drink that keeps you awake.", "subtle_hint": "Made from roasted beans."},
     "hi": {"word": "कॉफ़ी", "imposter_hint": "नींद भगाने वाला गहरा और स्वादिष्ट पेय।", "subtle_hint": "भुने हुए बीजों से बनती है।"}},

    # --- LEVEL 4: SMART (MODERATE) ---
    {"level": 4, "category": "Gadgets", "category_hi": "गैजेट्स",
     "en": {"word": "Camera", "imposter_hint": "A device used to capture photos and videos.", "subtle_hint": "People smile and say cheese for it."},
     "hi": {"word": "कैमरा", "imposter_hint": "फोटो और वीडियो खींचने का उपकरण।", "subtle_hint": "इसके सामने सब मुस्कुराते हैं।"}},
    {"level": 4, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Guitar", "imposter_hint": "A musical instrument with six strings.", "subtle_hint": "Played by strumming with fingers."},
     "hi": {"word": "गिटार", "imposter_hint": "छह तारों वाला संगीत वाद्ययंत्र।", "subtle_hint": "उंगलियों से तार छेड़कर बजाते हैं।"}},
    {"level": 4, "category": "Sports", "category_hi": "खेल",
     "en": {"word": "Chess", "imposter_hint": "A brainy board game with black and white squares.", "subtle_hint": "You try to checkmate the king."},
     "hi": {"word": "शतरंज", "imposter_hint": "काले-सफेद खानों वाला दिमागी खेल।", "subtle_hint": "राजा को मात देनी होती है।"}},
    {"level": 4, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Passport", "imposter_hint": "An official travel booklet for other countries.", "subtle_hint": "Gets stamped at the airport."},
     "hi": {"word": "पासपोर्ट", "imposter_hint": "विदेश यात्रा के लिए ज़रूरी पुस्तिका।", "subtle_hint": "हवाई अड्डे पर इस पर मुहर लगती है।"}},
    {"level": 4, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Wedding", "imposter_hint": "A big celebration when two people get married.", "subtle_hint": "Full of music, lights, and feasts."},
     "hi": {"word": "शादी", "imposter_hint": "दो लोगों के विवाह का बड़ा जश्न।", "subtle_hint": "संगीत, रोशनी और दावत होती है।"}},
    {"level": 4, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Cinema", "imposter_hint": "A dark hall with a giant movie screen.", "subtle_hint": "People eat popcorn here."},
     "hi": {"word": "सिनेमा हॉल", "imposter_hint": "बड़ी स्क्रीन पर फिल्म देखने की जगह।", "subtle_hint": "यहाँ लोग पॉपकॉर्न खाते हैं।"}},
    {"level": 4, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Rainbow", "imposter_hint": "A colorful seven-color arc in the sky.", "subtle_hint": "Appears when sun shines after rain."},
     "hi": {"word": "इंद्रधनुष", "imposter_hint": "आसमान में सात रंगों का सुंदर घेरा।", "subtle_hint": "बारिश के बाद धूप निकलने पर दिखता है।"}},
    {"level": 4, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Castle", "imposter_hint": "A huge old stone palace for kings and queens.", "subtle_hint": "Has tall towers and big gates."},
     "hi": {"word": "किला", "imposter_hint": "राजा-रानियों का बड़ा पत्थर का महल।", "subtle_hint": "ऊँची मीनारें और बड़े दरवाज़े होते हैं।"}},
    {"level": 4, "category": "Transport", "category_hi": "परिवहन",
     "en": {"word": "Rocket", "imposter_hint": "A powerful spacecraft that blasts into space.", "subtle_hint": "Launches after a countdown."},
     "hi": {"word": "रॉकेट", "imposter_hint": "अंतरिक्ष में जाने वाला शक्तिशाली यान।", "subtle_hint": "उलटी गिनती के बाद उड़ता है।"}},
    {"level": 4, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Island", "imposter_hint": "A piece of land surrounded by water.", "subtle_hint": "Reached by boat or plane."},
     "hi": {"word": "द्वीप", "imposter_hint": "चारों ओर पानी से घिरी ज़मीन।", "subtle_hint": "नाव या जहाज़ से वहाँ पहुँचते हैं।"}},
    {"level": 4, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Diamond", "imposter_hint": "A sparkling, super hard precious stone.", "subtle_hint": "Often set in expensive rings."},
     "hi": {"word": "हीरा", "imposter_hint": "चमकदार और सबसे कठोर कीमती रत्न।", "subtle_hint": "अक्सर कीमती अंगूठी में जड़ा जाता है।"}},
    {"level": 4, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Volcano", "imposter_hint": "A mountain that erupts with hot red lava.", "subtle_hint": "Sends smoke and fire into the sky."},
     "hi": {"word": "ज्वालामुखी", "imposter_hint": "ऐसा पहाड़ जिससे गर्म लावा निकलता है।", "subtle_hint": "आसमान में धुआँ और आग उगलता है।"}},
    {"level": 4, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Jungle", "imposter_hint": "A thick wild forest full of trees and animals.", "subtle_hint": "Home to tigers, monkeys, and vines."},
     "hi": {"word": "जंगल", "imposter_hint": "पेड़ों और जंगली जानवरों से भरा घना वन।", "subtle_hint": "बाघ और बंदर यहाँ रहते हैं।"}},
    {"level": 4, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Superhero", "imposter_hint": "A fictional hero with amazing powers.", "subtle_hint": "Wears a cape or mask and saves cities."},
     "hi": {"word": "सुपरहीरो", "imposter_hint": "अद्भुत शक्तियों वाला काल्पनिक नायक।", "subtle_hint": "शहर को बुराई से बचाता है।"}},
    {"level": 4, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Birthday", "imposter_hint": "A special day celebrated once every year.", "subtle_hint": "Balloons, wishes, and gifts."},
     "hi": {"word": "जन्मदिन", "imposter_hint": "साल में एक बार मनाया जाने वाला खास दिन।", "subtle_hint": "गुब्बारे, तोहफे और शुभकामनाएं मिलती हैं।"}},

    # --- LEVEL 5: PRO (CHALLENGE) ---
    {"level": 5, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Shadow", "imposter_hint": "A dark shape following you in the light.", "subtle_hint": "Disappears completely in total darkness."},
     "hi": {"word": "परछाई", "imposter_hint": "रोशनी में आपके साथ चलने वाली काली आकृति।", "subtle_hint": "पूरी तरह अंधेरे में गायब हो जाती है।"}},
    {"level": 5, "category": "Nature", "category_hi": "प्रकृति",
     "en": {"word": "Echo", "imposter_hint": "Your own voice bouncing back in hills.", "subtle_hint": "Repeats whatever you shout in a valley."},
     "hi": {"word": "गूंज", "imposter_hint": "पहाड़ियों से टकराकर वापस आती आपकी आवाज़।", "subtle_hint": "जो बोलो वही वापस सुनाई देता है।"}},
    {"level": 5, "category": "Abstract", "category_hi": "अमूर्त विचार",
     "en": {"word": "Dream", "imposter_hint": "Stories and pictures seen while sleeping.", "subtle_hint": "Often forgotten right after waking up."},
     "hi": {"word": "सपना", "imposter_hint": "सोते समय मन में दिखने वाली कहानियाँ।", "subtle_hint": "जागने के बाद अक्सर याद नहीं रहता।"}},
    {"level": 5, "category": "Abstract", "category_hi": "अमूर्त विचार",
     "en": {"word": "Secret", "imposter_hint": "Something private you don't tell everyone.", "subtle_hint": "Whispered only to a trusted friend."},
     "hi": {"word": "राज़", "imposter_hint": "ऐसी निजी बात जो सबको नहीं बताई जाती।", "subtle_hint": "केवल खास दोस्त को धीरे से बताते हैं।"}},
    {"level": 5, "category": "Abstract", "category_hi": "अमूर्त विचार",
     "en": {"word": "Ghost", "imposter_hint": "A spooky invisible figure in scary stories.", "subtle_hint": "Said to haunt old empty houses at night."},
     "hi": {"word": "भूत", "imposter_hint": "डरावनी कहानियों का अदृश्य पात्र।", "subtle_hint": "रात को पुराने खंडहरों की कहानियों में आता है।"}},
    {"level": 5, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Treasure", "imposter_hint": "Hidden gold, coins, and jewels in a chest.", "subtle_hint": "Pirates search for it with an old map."},
     "hi": {"word": "खज़ाना", "imposter_hint": "संदूक में छिपा सोना और हीरे-जवाहरात।", "subtle_hint": "पुराने नक्शे से इसकी तलाश होती है।"}},
    {"level": 5, "category": "Abstract", "category_hi": "अमूर्त विचार",
     "en": {"word": "Magic", "imposter_hint": "Amazing tricks that seem impossible.", "subtle_hint": "Pulling a rabbit out of a hat."},
     "hi": {"word": "जादू", "imposter_hint": "असंभव लगने वाले हैरतअंगेज़ करतब।", "subtle_hint": "टोपी से खरगोश निकालने जैसा कमाल।"}},
    {"level": 5, "category": "Daily Life", "category_hi": "दैनिक जीवन",
     "en": {"word": "Mirror", "imposter_hint": "Shiny glass that shows your exact reflection.", "subtle_hint": "Copies every move you make in front of it."},
     "hi": {"word": "आईना", "imposter_hint": "चमकदार शीशा जो आपका चेहरा दिखाता है।", "subtle_hint": "आपकी हर हरकत की नकल करता है।"}},
    {"level": 5, "category": "Professions", "category_hi": "पेशे",
     "en": {"word": "Detective", "imposter_hint": "A clever investigator who solves mysteries.", "subtle_hint": "Looks for footprints and hidden clues."},
     "hi": {"word": "जासूस", "imposter_hint": "रहस्य सुलझाने वाला चतुर खोजकर्ता।", "subtle_hint": "छिपे हुए सुराग ढूंढता है।"}},
    {"level": 5, "category": "Gadgets", "category_hi": "गैजेट्स",
     "en": {"word": "Robot", "imposter_hint": "A smart machine that moves and does tasks.", "subtle_hint": "Made of metal and programmed with code."},
     "hi": {"word": "रोबोट", "imposter_hint": "इंसान जैसे काम करने वाली स्मार्ट मशीन।", "subtle_hint": "धातु और कंप्यूटर कोड से बना होता है।"}},
    {"level": 5, "category": "Science", "category_hi": "विज्ञान",
     "en": {"word": "Alien", "imposter_hint": "A creature imagined to live on another planet.", "subtle_hint": "Often shown flying in a UFO."},
     "hi": {"word": "एलियन", "imposter_hint": "दूसरे ग्रह पर रहने वाला काल्पनिक प्राणी।", "subtle_hint": "उड़न तश्तरी में दिखाया जाता है।"}},
    {"level": 5, "category": "Science", "category_hi": "विज्ञान",
     "en": {"word": "Magnet", "imposter_hint": "An object that pulls iron and metal toward it.", "subtle_hint": "Has a north pole and a south pole."},
     "hi": {"word": "चुंबक", "imposter_hint": "लोहे को अपनी तरफ खींचने वाली चीज़।", "subtle_hint": "इसके दो ध्रुव होते हैं।"}},
    {"level": 5, "category": "Science", "category_hi": "विज्ञान",
     "en": {"word": "Compass", "imposter_hint": "A pocket tool that always points north.", "subtle_hint": "Helps travelers find direction."},
     "hi": {"word": "कम्पास", "imposter_hint": "हमेशा उत्तर दिशा बताने वाला छोटा यंत्र।", "subtle_hint": "यात्रियों को रास्ता दिखाता है।"}},
    {"level": 5, "category": "Science", "category_hi": "विज्ञान",
     "en": {"word": "Telescope", "imposter_hint": "A tube with lenses to view stars and planets.", "subtle_hint": "Makes the moon look super close."},
     "hi": {"word": "दूरबीन", "imposter_hint": "तारों और ग्रहों को पास से देखने का यंत्र।", "subtle_hint": "चाँद को बहुत करीब दिखाती है।"}},
    {"level": 5, "category": "Places", "category_hi": "स्थान",
     "en": {"word": "Pyramid", "imposter_hint": "A giant ancient triangle monument in Egypt.", "subtle_hint": "Built out of massive stone blocks in the desert."},
     "hi": {"word": "पिरामिड", "imposter_hint": "मिस्र का विशाल तिकोना प्राचीन स्मारक।", "subtle_hint": "रेगिस्तान में बड़े पत्थरों से बना है।"}},
]

CATEGORIES = sorted({w["category"] for w in WORD_BANK})

# ===========================================================================
# STATE & HELPERS
# ===========================================================================
GAMES = {}
GAMES_LOCK = threading.Lock()
GAME_TTL_SECONDS = 3 * 60 * 60
MAX_VOICE_BYTES = 60_000
MAX_CHAT_LEN = 200
MAX_CHAT_HISTORY = 200

def _cleanup_stale_games():
    now = time.time()
    with GAMES_LOCK:
        stale = [c for c, g in GAMES.items() if now - g["last_activity"] > GAME_TTL_SECONDS]
        for c in stale:
            del GAMES[c]

def _new_code():
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        if code not in GAMES:
            return code

def _make_player(token, name):
    return {
        "token": token, "name": name, "joined_at": time.time(),
        "role_word": "", "role_hint": "", "is_imposter": False,
        "clue": "", "clue_audio": None, "vote": None, "ready": False,
        "score": 0, "wins": 0, "streak": 0, "eliminated": False,
        "hint_viewed": False, "hint_viewed_at": None,
    }

def _active_players(game):
    return [p for p in game["players"] if not p.get("eliminated")]

def _tally_votes(game):
    active = _active_players(game)
    counts = {p["name"]: 0 for p in active}
    for p in active:
        if p["vote"] in counts:
            counts[p["vote"]] += 1
    top = max(counts.values()) if counts else 0
    leaders = [n for n, c in counts.items() if c == top and c > 0]
    if len(leaders) == 1:
        return leaders[0], False, counts
    return None, True, counts

def _pick_word(game):
    lvl = game.get("level", 1)
    cat = game.get("category", "All")
    used = set(game.get("used_words", []))

    pool = [w for w in WORD_BANK if w["level"] == lvl and (cat == "All" or w["category"] == cat)]
    if not pool:
        pool = [w for w in WORD_BANK if w["level"] == lvl]
    if not pool:
        pool = list(WORD_BANK)

    fresh = [w for w in pool if w["en"]["word"] not in used]
    if fresh:
        pool = fresh
    choice = random.choice(pool)
    game.setdefault("used_words", []).append(choice["en"]["word"])
    if len(game["used_words"]) > 40:
        game["used_words"] = game["used_words"][-40:]
    return choice

def _build_hint_for_level(entry, lang, level_cfg):
    data = entry[lang]
    cat_label = entry["category_hi"] if lang == "hi" else entry["category"]
    style = level_cfg["hint_style"]
    if style == "full":
        return f"[{cat_label}] {data['imposter_hint']}"
    elif style == "subtle":
        return f"[{cat_label}] {data.get('subtle_hint') or data['imposter_hint']}"
    elif style == "category":
        if lang == "hi":
            return f"केवल श्रेणी: {cat_label} — ध्यान से सुराग सुनें!"
        return f"Category Only: {cat_label} — Read the room carefully!"
    else:  # cryptic (Level 5)
        subtle = data.get("subtle_hint") or data["imposter_hint"]
        if lang == "hi":
            return f"गुप्त संकेत: {subtle}"
        return f"Cryptic Intel: {subtle}"

def _crew_hint_text(entry, lang):
    cat_label = entry["category_hi"] if lang == "hi" else entry["category"]
    if lang == "hi":
        return f"श्रेणी: {cat_label} • शब्द बोले बिना चतुराई से संकेत दें!"
    return f"Category: {cat_label} • Give a smart clue without being too obvious!"

def _award_points(game, winner):
    lvl_cfg = LEVELS.get(game.get("level", 1), LEVELS[1])
    crew_pts = lvl_cfg["crew_pts"]
    imp_pts = lvl_cfg["imposter_pts"]
    for p in game["players"]:
        won = (winner == "crew" and not p["is_imposter"]) or (winner == "imposter" and p["is_imposter"])
        if won:
            p["streak"] = p.get("streak", 0) + 1
            streak_bonus = (p["streak"] - 1) * 25
            base = crew_pts if winner == "crew" else imp_pts
            p["score"] = p.get("score", 0) + base + streak_bonus
            p["wins"] = p.get("wins", 0) + 1
        else:
            p["streak"] = 0

def _player_hint_timer(player):
    duration = HINT_TIMER_SECONDS
    if not player or not player.get("hint_viewed_at"):
        return {"active": False, "started_at": None, "duration": duration, "remaining": duration, "expired": False}
    elapsed = time.time() - player["hint_viewed_at"]
    remaining = max(0.0, duration - elapsed)
    return {
        "active": remaining > 0,
        "started_at": player["hint_viewed_at"],
        "duration": duration,
        "remaining": round(remaining, 2),
        "expired": remaining <= 0,
    }

def _finalize_result(game, winner, reason_text=""):
    game["phase"] = "result"
    game["result_banner"] = winner
    if reason_text:
        game["result_reason"] = reason_text
    _award_points(game, winner)

def _public_state(game, token):
    lvl_cfg = LEVELS.get(game.get("level", 1), LEVELS[1])
    players = []
    for p in game["players"]:
        voice_out = None
        if p.get("clue_audio") and game["phase"] in ("summary", "vote", "last_guess", "result"):
            voice_out = p["clue_audio"]
        players.append({
            "name": p["name"],
            "ready": p["ready"],
            "has_clue": bool(p["clue"] or p.get("clue_audio")),
            "clue": p["clue"] if game["phase"] in ("summary", "vote", "last_guess", "result") else "",
            "clue_audio": voice_out,
            "has_voted": p["vote"] is not None,
            "score": p.get("score", 0),
            "wins": p.get("wins", 0),
            "streak": p.get("streak", 0),
            "rank": _get_rank(p.get("score", 0)),
            "eliminated": p.get("eliminated", False),
            "hint_viewed": p.get("hint_viewed", False),
        })
    me = next((p for p in game["players"] if p["token"] == token), None)
    host = next((p for p in game["players"] if p["token"] == game["host_token"]), None)
    my_hint_timer = _player_hint_timer(me)
    state = {
        "code": game["code"],
        "phase": game["phase"],
        "lang": game["lang"],
        "level": game.get("level", 1),
        "level_info": lvl_cfg,
        "category": game.get("category", "All"),
        "word_category": game.get("word_category", ""),
        "round": game["round"],
        "max_rounds": game.get("max_rounds", lvl_cfg["rounds"]),
        "last_guess_enabled": game.get("last_guess_enabled", lvl_cfg["last_guess"]),
        "players": players,
        "is_host": bool(me and me["token"] == game["host_token"]),
        "host_name": host["name"] if host else "",
        "imposter_count": game["imposter_count"],
        "remaining_imposters": sum(1 for p in game["players"] if p["is_imposter"] and not p.get("eliminated")),
        "clue_history": game.get("clue_history", []),
        "hint_timer": my_hint_timer,
        "hint_viewed_by": game.get("hint_viewed_by", []),
        "chat": game.get("chat", [])[-60:],
        "chat_open": game.get("chat_open", True),
        "reactions": game.get("reactions", []),
        "elimination_notice": game.get("elimination_notice", ""),
        "you": None,
    }
    if me:
        state["you"] = {
            "name": me["name"], "ready": me["ready"],
            "clue": me["clue"], "clue_audio": me.get("clue_audio"),
            "has_voted": me["vote"] is not None,
            "score": me.get("score", 0), "wins": me.get("wins", 0),
            "streak": me.get("streak", 0), "rank": _get_rank(me.get("score", 0)),
            "eliminated": me.get("eliminated", False),
            "hint_viewed": me.get("hint_viewed", False),
            "hint_expired": my_hint_timer["expired"],
        }
        if game["phase"] in ("reveal", "clue", "summary", "vote", "last_guess", "result"):
            state["your_word"] = me["role_word"]
            can_see_hint = (my_hint_timer["active"] and not my_hint_timer["expired"]) or game["phase"] == "result"
            state["your_hint"] = me["role_hint"] if can_see_hint else ""
            state["hint_available"] = bool(me["role_hint"])
            state["you_are_imposter"] = me["is_imposter"]
    if game["phase"] == "last_guess":
        started = game.get("last_guess_started_at") or time.time()
        rem = max(0, int(round(LAST_GUESS_SECONDS - (time.time() - started))))
        state["last_guess_imposter"] = game.get("voted_out_name")
        state["last_guess_remaining"] = rem
        state["you_can_guess"] = bool(me and me["name"] == game.get("voted_out_name"))
    if game["phase"] == "result":
        state["imposter_names"] = game["imposter_names"]
        state["secret_word"] = game["word"]
        state["result_banner"] = game["result_banner"]
        state["result_reason"] = game.get("result_reason", "")
        state["imposter_guess_text"] = game.get("imposter_guess_text", "")
        state["vote_counts"] = game["vote_counts"]
        state["voted_out_name"] = game["voted_out_name"]
        state["vote_tie"] = game["vote_tie"]
        state["scores"] = {p["name"]: p.get("score", 0) for p in game["players"]}
    return state


# ===========================================================================
# HTTP HANDLER
# ===========================================================================
class GameHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def setup(self):
        super().setup()
        try:
            self.connection.settimeout(20)
        except Exception:
            pass

    def _send(self, status, body, content_type="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False))

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return None

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._send(200, HTML_PAGE, "text/html; charset=utf-8")
        elif path == "/api/ping":
            self._json(200, {"ok": True, "games": len(GAMES), "ts": int(time.time())})
        elif path in ("/health", "/healthz"):
            self._json(200, {"status": "ok", "games": len(GAMES), "uptime": int(time.time() - START_TIME)})
        elif path == "/api/words":
            self._json(200, {
                "words": WORD_BANK,
                "levels": LEVELS,
                "categories": CATEGORIES,
                "hint_timer_seconds": HINT_TIMER_SECONDS,
            })
        elif path == "/join":
            qs = urllib.parse.urlparse(self.path).query
            self.send_response(302)
            self.send_header("Location", "/?" + qs)
            self.end_headers()
        else:
            self._send(404, "Not found", "text/plain")

    def do_POST(self):
        path = self.path.split("?")[0]
        routes = {
            "/api/create": self._handle_create,
            "/api/join": self._handle_join,
            "/api/state": self._handle_state,
            "/api/ready": self._handle_ready,
            "/api/config": self._handle_config,
            "/api/start": self._handle_start,
            "/api/see_hint": self._handle_see_hint,
            "/api/timer_expire": self._handle_timer_expire,
            "/api/clue": self._handle_clue,
            "/api/audio": self._handle_audio,
            "/api/advance": self._handle_advance,
            "/api/vote": self._handle_vote,
            "/api/imposter_guess": self._handle_imposter_guess,
            "/api/reset": self._handle_reset,
            "/api/next_level": self._handle_next_level,
            "/api/chat": self._handle_chat,
            "/api/react": self._handle_react,
            "/api/leave": self._handle_leave,
            "/api/kick": self._handle_kick,
            "/api/end": self._handle_end,
        }
        fn = routes.get(path)
        if not fn:
            return self._send(404, "Not found", "text/plain")
        try:
            fn()
        except BrokenPipeError:
            pass
        except Exception as e:
            try:
                self._json(500, {"error": "server_error", "detail": str(e)})
            except Exception:
                pass

    def _with_game(self, payload, fn):
        if not payload:
            return self._json(400, {"error": "bad_request"})
        code = (payload.get("code") or "").upper().strip()
        token = payload.get("token") or ""
        if not code or not token:
            return self._json(400, {"error": "missing_code_or_token"})
        _cleanup_stale_games()
        with GAMES_LOCK:
            game = GAMES.get(code)
            if not game:
                return self._json(404, {"error": "game_not_found"})
            if not any(p["token"] == token for p in game["players"]):
                return self._json(403, {"error": "not_in_game"})
            game["last_activity"] = time.time()
            self._check_timers(game)
            return fn(game, token, payload)

    def _check_timers(self, game):
        # Auto-resolve Imposter Last-Stand timer if expired
        if game["phase"] == "last_guess":
            started = game.get("last_guess_started_at") or 0
            if started and (time.time() - started) >= LAST_GUESS_SECONDS:
                game["imposter_guess_text"] = "(Timed Out)"
                _finalize_result(game, "crew", "Imposter failed to guess the secret word in time!")
                self._add_chat(game, "System", "⏰ Imposter timed out on final guess — Crew wins!")

    def _snapshot_round_clues(self, game):
        cur_round = game["round"]
        # Avoid duplicating snapshot for same round
        if any(h["round"] == cur_round for h in game.get("clue_history", [])):
            return
        entries = []
        for p in _active_players(game):
            entries.append({
                "name": p["name"],
                "clue": p.get("clue", ""),
                "clue_audio": p.get("clue_audio"),
            })
        game.setdefault("clue_history", []).append({"round": cur_round, "clues": entries})

    def _find_player(self, game, token):
        return next((p for p in game["players"] if p["token"] == token), None)

    def _add_chat(self, game, sender_name, text):
        text = str(text or "").strip()[:MAX_CHAT_LEN]
        if not text:
            return
        entry = {"ts": int(time.time() * 1000), "name": sender_name, "text": text}
        game.setdefault("chat", []).append(entry)
        game["chat"] = game["chat"][-MAX_CHAT_HISTORY:]

    def _handle_create(self):
        payload = self._read_json() or {}
        lang = payload.get("lang", "en")
        if lang not in ("en", "hi"):
            lang = "en"
        name = (payload.get("name") or "").strip()[:20] or "Host"
        token = secrets.token_urlsafe(16)
        with GAMES_LOCK:
            code = _new_code()
            GAMES[code] = {
                "code": code, "lang": lang, "phase": "lobby", "host_token": token,
                "players": [_make_player(token, name)],
                "level": 1, "category": "All", "word_category": "",
                "max_rounds": 2, "last_guess_enabled": False,
                "word": "", "imposter_hint": "", "imposter_index": 0,
                "imposter_count": 1, "imposter_names": [],
                "result_banner": "", "result_reason": "", "imposter_guess_text": "",
                "vote_counts": {}, "voted_out_name": None, "vote_tie": False,
                "elimination_notice": "",
                "clue_history": [], "used_words": [],
                "hint_timer_started_at": None, "hint_timer_duration": HINT_TIMER_SECONDS,
                "hint_timer_handled": False, "hint_viewed_by": [],
                "last_guess_started_at": None,
                "round": 1, "chat": [], "chat_open": True,
                "reactions": [],
                "created_at": time.time(), "last_activity": time.time(),
            }
            game = GAMES[code]
        self._json(200, {"code": code, "token": token, "state": _public_state(game, token)})

    def _handle_join(self):
        payload = self._read_json() or {}
        code = (payload.get("code") or "").upper().strip()
        name = (payload.get("name") or "").strip()[:20]
        if not code or not name:
            return self._json(400, {"error": "missing_fields"})
        with GAMES_LOCK:
            game = GAMES.get(code)
            if not game:
                return self._json(404, {"error": "game_not_found"})
            if game["phase"] != "lobby":
                return self._json(409, {"error": "game_in_progress"})
            if len(game["players"]) >= 10:
                return self._json(409, {"error": "game_full"})
            if any(p["name"].lower() == name.lower() for p in game["players"]):
                return self._json(409, {"error": "name_taken"})
            token = secrets.token_urlsafe(16)
            game["players"].append(_make_player(token, name))
            self._add_chat(game, "System", f"{name} joined the room")
        self._json(200, {"code": code, "token": token, "state": _public_state(game, token)})

    def _handle_state(self):
        payload = self._read_json() or {}
        self._with_game(payload, lambda g, t, p: self._json(200, _public_state(g, t)))

    def _handle_ready(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            me = self._find_player(game, token)
            me["ready"] = bool(payload.get("ready", True))
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_config(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            if token != game["host_token"]:
                return self._json(403, {"error": "host_only"})
            if game["phase"] != "lobby":
                return self._json(409, {"error": "lobby_only"})
            if "level" in payload:
                try:
                    lvl = max(1, min(5, int(payload["level"])))
                    game["level"] = lvl
                    game["max_rounds"] = LEVELS[lvl]["rounds"]
                    game["last_guess_enabled"] = LEVELS[lvl]["last_guess"]
                except (TypeError, ValueError):
                    pass
            if "category" in payload:
                cat = str(payload["category"])
                game["category"] = cat if (cat == "All" or cat in CATEGORIES) else "All"
            if "num_imposters" in payload:
                try:
                    n = len(game["players"])
                    max_k = max(1, (n - 1) // 2)
                    game["imposter_count"] = max(1, min(int(payload["num_imposters"]), max_k, 3))
                except (TypeError, ValueError):
                    pass
            if "last_guess_enabled" in payload:
                game["last_guess_enabled"] = bool(payload["last_guess_enabled"])
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_start(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            if token != game["host_token"]:
                return self._json(403, {"error": "host_only"})
            if game["phase"] != "lobby":
                return self._json(409, {"error": "already_started"})
            n = len(game["players"])
            if n < 3:
                return self._json(400, {"error": "need_3_players"})

            try:
                lvl = max(1, min(5, int(payload.get("level", game.get("level", 1)))))
            except (TypeError, ValueError):
                lvl = 1
            game["level"] = lvl
            lvl_cfg = LEVELS[lvl]
            game["max_rounds"] = lvl_cfg["rounds"]
            if "last_guess_enabled" in payload:
                game["last_guess_enabled"] = bool(payload["last_guess_enabled"])
            else:
                game["last_guess_enabled"] = lvl_cfg["last_guess"]

            cat = payload.get("category", game.get("category", "All"))
            game["category"] = cat if (cat == "All" or cat in CATEGORIES) else "All"

            try:
                k = int(payload.get("num_imposters", game.get("imposter_count", 1)))
            except (TypeError, ValueError):
                k = 1
            max_k = max(1, (n - 1) // 2)
            k = max(1, min(k, max_k, 3))

            custom_word = (payload.get("custom_word") or "").strip()[:40]
            custom_hint = (payload.get("custom_hint") or "").strip()[:120]
            if custom_word:
                game["word"] = custom_word
                game["word_category"] = "Custom"
                imp_hint = custom_hint or "No custom hint provided — blend in carefully!"
                crew_hint = "Custom Mission Word • Give clever clues without saying it!"
            else:
                entry = _pick_word(game)
                lang = game["lang"]
                game["word"] = entry[lang]["word"]
                game["word_category"] = entry["category_hi"] if lang == "hi" else entry["category"]
                imp_hint = _build_hint_for_level(entry, lang, lvl_cfg)
                crew_hint = _crew_hint_text(entry, lang)

            game["imposter_hint"] = imp_hint
            game["imposter_count"] = k
            imposter_indices = set(random.sample(range(n), k))
            game["imposter_index"] = next(iter(imposter_indices))
            game["imposter_names"] = [game["players"][i]["name"] for i in sorted(imposter_indices)]
            for i, p in enumerate(game["players"]):
                p["is_imposter"] = i in imposter_indices
                p["eliminated"] = False
                p["hint_viewed"] = False
                p["hint_viewed_at"] = None
                if p["is_imposter"]:
                    p["role_word"] = ""
                    p["role_hint"] = imp_hint
                else:
                    p["role_word"] = game["word"]
                    p["role_hint"] = crew_hint
                p["clue"] = ""
                p["clue_audio"] = None
                p["vote"] = None

            game["phase"] = "reveal"
            game["round"] = 1
            game["clue_history"] = []
            game["result_banner"] = ""
            game["result_reason"] = ""
            game["imposter_guess_text"] = ""
            game["vote_counts"] = {}
            game["voted_out_name"] = None
            game["vote_tie"] = False
            game["elimination_notice"] = ""
            game["hint_timer_started_at"] = None
            game["hint_timer_handled"] = False
            game["hint_viewed_by"] = []
            game["last_guess_started_at"] = None
            game["reactions"] = []
            self._add_chat(game, "System", f"Level {lvl} ({lvl_cfg['name']}) started! Check your secret role.")
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_see_hint(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            if game["phase"] not in ("reveal", "clue", "summary", "vote"):
                return self._json(409, {"error": "not_in_active_game"})
            me = self._find_player(game, token)
            if not me["hint_viewed"]:
                me["hint_viewed"] = True
                me["hint_viewed_at"] = time.time()
                if me["name"] not in game.get("hint_viewed_by", []):
                    game.setdefault("hint_viewed_by", []).append(me["name"])
                self._add_chat(game, "System", f"⏱️ {me['name']} opened their 7-second hint!")
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_timer_expire(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            self._check_timers(game)
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_clue(self):
        payload = self._read_json() or {}
        text = (payload.get("text") or "").strip()[:80]
        def run(game, token, payload):
            if game["phase"] != "clue":
                return self._json(409, {"error": "not_clue_phase"})
            me = self._find_player(game, token)
            if me.get("eliminated"):
                return self._json(403, {"error": "eliminated"})
            if not text:
                return self._json(400, {"error": "empty_clue"})
            if me["clue"] or me.get("clue_audio"):
                return self._json(409, {"error": "already_submitted"})
            if game["word"] and game["word"].lower() in text.lower():
                return self._json(400, {"error": "contains_word"})
            me["clue"] = text
            if all(p["clue"] or p.get("clue_audio") for p in _active_players(game)):
                self._snapshot_round_clues(game)
                game["phase"] = "summary"
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_audio(self):
        payload = self._read_json() or {}
        data = payload.get("audio") or ""
        def run(game, token, payload):
            if game["phase"] != "clue":
                return self._json(409, {"error": "not_clue_phase"})
            me = self._find_player(game, token)
            if me.get("eliminated"):
                return self._json(403, {"error": "eliminated"})
            if me["clue"] or me.get("clue_audio"):
                return self._json(409, {"error": "already_submitted"})
            if not data.startswith("data:audio/"):
                return self._json(400, {"error": "bad_audio_format"})
            if len(data) > MAX_VOICE_BYTES:
                return self._json(413, {"error": "audio_too_large"})
            me["clue_audio"] = data
            me["clue"] = ""
            if all(p["clue"] or p.get("clue_audio") for p in _active_players(game)):
                self._snapshot_round_clues(game)
                game["phase"] = "summary"
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_advance(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            if token != game["host_token"]:
                return self._json(403, {"error": "host_only"})
            if game["phase"] == "reveal":
                game["phase"] = "clue"
                game["round"] = 1
                for p in game["players"]:
                    p["clue"] = ""
                    p["clue_audio"] = None
            elif game["phase"] == "summary":
                if game["round"] < game.get("max_rounds", 2):
                    game["round"] += 1
                    game["phase"] = "clue"
                    for p in game["players"]:
                        p["clue"] = ""
                        p["clue_audio"] = None
                else:
                    game["phase"] = "vote"
                    game["elimination_notice"] = ""
                    for p in game["players"]:
                        p["vote"] = None
            game["reactions"] = []
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _resolve_votes(self, game, timed_out=False):
        top_name, is_tie, counts = _tally_votes(game)
        game["vote_counts"] = counts
        game["vote_tie"] = is_tie
        game["voted_out_name"] = top_name
        imposter_names = set(game["imposter_names"])

        if is_tie or not top_name:
            reason = "Vote ended in a tie — Imposters escaped!"
            _finalize_result(game, "imposter", reason)
            self._add_chat(game, "System", "Imposters win! (Tie vote)")
            return

        victim = next((p for p in game["players"] if p["name"] == top_name), None)
        if victim and top_name in imposter_names:
            victim["eliminated"] = True
            remaining_imps = [p for p in game["players"] if p["is_imposter"] and not p.get("eliminated")]
            if remaining_imps:
                # Multi-imposter mode: 1 caught, others still loose!
                game["elimination_notice"] = f"🎯 {top_name} WAS AN IMPOSTER! {len(remaining_imps)} imposter still at large — vote again!"
                for p in game["players"]:
                    p["vote"] = None
                game["phase"] = "vote"
                self._add_chat(game, "System", f"🎯 {top_name} caught! {len(remaining_imps)} imposter remaining — new vote started!")
                return
            # All imposters caught! Check Imposter Last-Stand
            if game.get("last_guess_enabled"):
                game["phase"] = "last_guess"
                game["last_guess_started_at"] = time.time()
                self._add_chat(game, "System", f"🔥 {top_name} caught! Imposter Last Stand — 25s to guess the secret word!")
            else:
                _finalize_result(game, "crew", f"All Imposters eliminated! {top_name} was caught.")
                self._add_chat(game, "System", "🎉 Crew wins!")
        else:
            reason = f"{top_name} was innocent Crew! Imposters win."
            _finalize_result(game, "imposter", reason)
            self._add_chat(game, "System", f"😈 {top_name} was innocent — Imposters win!")

    def _handle_vote(self):
        payload = self._read_json() or {}
        target = payload.get("target")
        def run(game, token, payload):
            if game["phase"] != "vote":
                return self._json(409, {"error": "not_vote_phase"})
            me = self._find_player(game, token)
            if me.get("eliminated"):
                return self._json(403, {"error": "eliminated"})
            active = _active_players(game)
            names = [p["name"] for p in active]
            if target not in names:
                return self._json(400, {"error": "bad_target"})
            if target == me["name"]:
                return self._json(400, {"error": "cannot_vote_self"})
            me["vote"] = target
            if all(p["vote"] for p in active):
                self._resolve_votes(game)
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_imposter_guess(self):
        payload = self._read_json() or {}
        guess = (payload.get("guess") or "").strip()[:60]
        def run(game, token, payload):
            if game["phase"] != "last_guess":
                return self._json(409, {"error": "not_last_guess"})
            me = self._find_player(game, token)
            if not me or me["name"] != game.get("voted_out_name"):
                return self._json(403, {"error": "not_caught_imposter"})
            game["imposter_guess_text"] = guess or "(Skipped)"
            secret = (game["word"] or "").strip().lower()
            if guess and guess.lower() == secret:
                _finalize_result(game, "imposter", f"🔥 CLUTCH STEAL! {me['name']} guessed '{game['word']}' correctly!")
                self._add_chat(game, "System", f"🔥 {me['name']} guessed the secret word and STOLE the win!")
            else:
                _finalize_result(game, "crew", f"{me['name']} guessed '{guess or 'nothing'}' — WRONG! Crew wins!")
                self._add_chat(game, "System", f"🎉 {me['name']} missed the final guess — Crew wins!")
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _reset_to_lobby(self, game, next_level=False):
        if next_level and game.get("level", 1) < 5:
            game["level"] = game.get("level", 1) + 1
        lvl_cfg = LEVELS.get(game.get("level", 1), LEVELS[1])
        game["phase"] = "lobby"
        game["round"] = 1
        game["max_rounds"] = lvl_cfg["rounds"]
        game["last_guess_enabled"] = lvl_cfg["last_guess"]
        game["word"] = ""
        game["word_category"] = ""
        game["imposter_hint"] = ""
        game["imposter_names"] = []
        game["result_banner"] = ""
        game["result_reason"] = ""
        game["imposter_guess_text"] = ""
        game["vote_counts"] = {}
        game["voted_out_name"] = None
        game["vote_tie"] = False
        game["elimination_notice"] = ""
        game["clue_history"] = []
        game["hint_timer_started_at"] = None
        game["hint_timer_handled"] = False
        game["hint_viewed_by"] = []
        game["last_guess_started_at"] = None
        game["chat_open"] = True
        game["reactions"] = []
        for p in game["players"]:
            p["clue"] = ""
            p["clue_audio"] = None
            p["vote"] = None
            p["ready"] = False
            p["is_imposter"] = False
            p["eliminated"] = False
            p["hint_viewed"] = False
            p["hint_viewed_at"] = None
            p["role_word"] = ""
            p["role_hint"] = ""

    def _handle_reset(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            if token != game["host_token"]:
                return self._json(403, {"error": "host_only"})
            self._reset_to_lobby(game, next_level=False)
            self._add_chat(game, "System", "New mission ready — everyone, please ready up.")
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_next_level(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            if token != game["host_token"]:
                return self._json(403, {"error": "host_only"})
            self._reset_to_lobby(game, next_level=True)
            lvl = game["level"]
            self._add_chat(game, "System", f"🚀 Advanced to Level {lvl} ({LEVELS[lvl]['name']})! Ready up!")
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_end(self):
        payload = self._read_json() or {}
        code = (payload.get("code") or "").upper().strip()
        token = payload.get("token") or ""
        with GAMES_LOCK:
            game = GAMES.get(code)
            if not game:
                return self._json(404, {"error": "game_not_found"})
            if token != game["host_token"]:
                return self._json(403, {"error": "host_only"})
            del GAMES[code]
        self._json(200, {"ok": True})

    def _handle_chat(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            raw_text = payload.get("text", "")
            text = str(raw_text).strip()[:MAX_CHAT_LEN]
            if not game.get("chat_open", True):
                return self._json(403, {"error": "chat_locked"})
            me = self._find_player(game, token)
            if not me:
                return self._json(403, {"error": "not_in_game"})
            if not text:
                return self._json(400, {"error": "empty"})
            if game["phase"] == "clue" and not me.get("eliminated") and not (me["clue"] or me.get("clue_audio")):
                return self._json(403, {"error": "chat_blocked_during_clue"})
            self._add_chat(game, me["name"], text)
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_react(self):
        payload = self._read_json() or {}
        emoji = payload.get("emoji", "")
        def run(game, token, payload):
            me = self._find_player(game, token)
            if emoji:
                game.setdefault("reactions", []).append({
                    "emoji": emoji, "name": me["name"], "ts": time.time()
                })
                now = time.time()
                game["reactions"] = [r for r in game["reactions"] if now - r["ts"] < 3.0]
            self._json(200, {"ok": True})
        self._with_game(payload, run)

    def _handle_leave(self):
        payload = self._read_json() or {}
        code = (payload.get("code") or "").upper().strip()
        token = payload.get("token") or ""
        with GAMES_LOCK:
            game = GAMES.get(code)
            if not game:
                return self._json(200, {"ok": True})
            me = next((p for p in game["players"] if p["token"] == token), None)
            if not me:
                return self._json(200, {"ok": True})
            game["players"].remove(me)
            self._add_chat(game, "System", f"{me['name']} left the room")
            if me["token"] == game["host_token"] and game["players"]:
                game["host_token"] = game["players"][0]["token"]
                self._add_chat(game, "System", f"{game['players'][0]['name']} is now the host")
            if not game["players"]:
                del GAMES[code]
            elif len(game["players"]) < 3 and game["phase"] != "lobby":
                self._reset_to_lobby(game, next_level=False)
                self._add_chat(game, "System", "Not enough players — game reset to lobby")
        self._json(200, {"ok": True})

    def _handle_kick(self):
        payload = self._read_json() or {}
        target = payload.get("target") or ""
        def run(game, token, payload):
            if token != game["host_token"]:
                return self._json(403, {"error": "host_only"})
            if game["phase"] != "lobby":
                return self._json(409, {"error": "lobby_only"})
            victim = next((p for p in game["players"] if p["name"] == target), None)
            if not victim:
                return self._json(404, {"error": "player_not_found"})
            if victim["token"] == game["host_token"]:
                return self._json(400, {"error": "cannot_kick_self"})
            game["players"].remove(victim)
            self._add_chat(game, "System", f"{target} was removed by the host")
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)


# ===========================================================================
# HTML (ADVANCED IMPOSTER PROTOCOL — LEVELS + 5-MIN HINT TIMER + SFX + HUD)
# ===========================================================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Imposter Protocol — Advanced Edition</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&display=swap');

  :root {
    --bg-base: #05050f;
    --bg-card: rgba(15, 17, 30, 0.88);
    --neon-cyan: #00f3ff;
    --neon-purple: #b026ff;
    --neon-red: #ff003c;
    --neon-green: #00ff66;
    --neon-amber: #ffb000;
    --text-main: #e2e8f0;
    --text-muted: #94a3b8;
    --font-ui: 'Rajdhani', sans-serif;
    --font-mono: 'Share Tech Mono', monospace;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: var(--font-ui);
    background-color: var(--bg-base);
    background-image:
      radial-gradient(circle at 20% 20%, rgba(0, 243, 255, 0.07) 0%, transparent 45%),
      radial-gradient(circle at 80% 80%, rgba(176, 38, 255, 0.08) 0%, transparent 45%),
      linear-gradient(rgba(0, 243, 255, 0.045) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 243, 255, 0.045) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 30px 30px, 30px 30px;
    color: var(--text-main);
    min-height: 100vh;
    display: flex; align-items: flex-start; justify-content: center;
    padding: 16px;
    padding-bottom: 100px;
    overflow-x: hidden;
  }

  body::after {
    content: " ";
    display: block; position: fixed; inset: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.22) 50%),
                linear-gradient(90deg, rgba(255, 0, 0, 0.04), rgba(0, 255, 0, 0.015), rgba(0, 0, 255, 0.04));
    z-index: 2; background-size: 100% 2px, 3px 100%; pointer-events: none;
  }

  .app {
    width: 100%; max-width: 580px;
    background: var(--bg-card);
    border: 1px solid rgba(0, 243, 255, 0.35);
    border-radius: 18px; padding: 24px 22px 28px;
    box-shadow: 0 0 30px rgba(0, 243, 255, 0.12), inset 0 0 24px rgba(0, 243, 255, 0.04);
    backdrop-filter: blur(12px);
    margin: auto; position: relative; z-index: 5;
  }

  .app::before {
    content: ''; position: absolute; inset: -1px; border-radius: 18px; pointer-events: none;
    border: 1px solid transparent;
    background: linear-gradient(135deg, var(--neon-cyan) 0%, transparent 38%, transparent 62%, var(--neon-purple) 100%) border-box;
    -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: destination-out; mask-composite: exclude;
  }

  /* TOP TOOLBAR */
  .top-bar {
    display: flex; align-items: center; justify-content: space-between;
    gap: 8px; margin-bottom: 10px;
  }
  .top-badges { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .top-actions { display: flex; gap: 8px; align-items: center; }
  .icon-btn {
    width: 36px; height: 36px; padding: 0; margin: 0; border-radius: 50%;
    border: 1px solid rgba(0, 243, 255, 0.4); color: var(--neon-cyan);
    background: rgba(0, 0, 0, 0.45); font-size: 1rem;
    display: flex; align-items: center; justify-content: center; cursor: pointer;
    transition: all 0.2s;
  }
  .icon-btn:hover { background: rgba(0, 243, 255, 0.18); box-shadow: 0 0 12px rgba(0, 243, 255, 0.35); transform: translateY(-1px); }
  .icon-btn.purple { border-color: var(--neon-purple); color: var(--neon-purple); }
  .icon-btn.amber { border-color: var(--neon-amber); color: var(--neon-amber); }

  /* PERSISTENT 5-MINUTE HINT COUNTDOWN TIMER HUD */
  .hint-timer-hud {
    display: none;
    margin: 6px 0 16px;
    padding: 12px 14px;
    border-radius: 12px;
    background: rgba(0, 18, 30, 0.85);
    border: 1px solid var(--neon-cyan);
    box-shadow: 0 0 18px rgba(0, 243, 255, 0.18);
    transition: border-color 0.3s, box-shadow 0.3s, background 0.3s;
  }
  .hint-timer-hud.active { display: block; animation: glitch-in 0.25s ease; }
  .hint-timer-hud.warn {
    border-color: var(--neon-amber);
    background: rgba(35, 22, 0, 0.85);
    box-shadow: 0 0 20px rgba(255, 176, 0, 0.28);
  }
  .hint-timer-hud.critical {
    border-color: var(--neon-red);
    background: rgba(45, 0, 14, 0.9);
    box-shadow: 0 0 24px rgba(255, 0, 60, 0.45);
    animation: pulse-timer 1s infinite;
  }
  @keyframes pulse-timer {
    0%, 100% { box-shadow: 0 0 14px rgba(255, 0, 60, 0.35); }
    50% { box-shadow: 0 0 30px rgba(255, 0, 60, 0.75); }
  }
  .timer-top {
    display: flex; align-items: center; justify-content: space-between; gap: 10px;
  }
  .timer-label {
    font-family: var(--font-mono); font-size: 0.78rem; letter-spacing: 1px;
    text-transform: uppercase; color: var(--text-muted);
    display: flex; align-items: center; gap: 6px;
  }
  .timer-dot {
    width: 8px; height: 8px; border-radius: 50%; background: var(--neon-cyan);
    box-shadow: 0 0 8px var(--neon-cyan); display: inline-block;
    animation: blink 1s infinite;
  }
  .hint-timer-hud.warn .timer-dot { background: var(--neon-amber); box-shadow: 0 0 8px var(--neon-amber); }
  .hint-timer-hud.critical .timer-dot { background: var(--neon-red); box-shadow: 0 0 8px var(--neon-red); }
  @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.25; } }
  .timer-clock {
    font-family: var(--font-mono); font-size: 1.55rem; font-weight: 700;
    color: var(--neon-cyan); letter-spacing: 3px;
    text-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
  }
  .hint-timer-hud.warn .timer-clock { color: var(--neon-amber); text-shadow: 0 0 10px rgba(255, 176, 0, 0.6); }
  .hint-timer-hud.critical .timer-clock { color: var(--neon-red); text-shadow: 0 0 12px rgba(255, 0, 60, 0.8); }
  .timer-bar-bg {
    width: 100%; height: 6px; border-radius: 99px; margin-top: 8px;
    background: rgba(255, 255, 255, 0.1); overflow: hidden;
  }
  .timer-bar-fill {
    height: 100%; width: 100%; border-radius: 99px;
    background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan));
    transition: width 0.5s linear, background 0.3s;
  }
  .hint-timer-hud.warn .timer-bar-fill { background: linear-gradient(90deg, #ff7b00, var(--neon-amber)); }
  .hint-timer-hud.critical .timer-bar-fill { background: linear-gradient(90deg, #ff003c, #ff5e7e); }

  h1 {
    font-size: 1.95rem; text-align: center; margin-bottom: 4px;
    text-transform: uppercase; letter-spacing: 2px; color: #fff;
    text-shadow: 0 0 10px var(--neon-cyan), 0 0 20px rgba(0, 243, 255, 0.5);
  }
  h2 {
    font-size: 1.3rem; text-align: center; margin-bottom: 8px;
    text-transform: uppercase; letter-spacing: 1px; color: var(--neon-cyan);
  }
  .subtitle { text-align: center; color: var(--text-muted); font-size: 0.92rem; margin-bottom: 16px; font-family: var(--font-mono); }

  .screen { display: none; }
  .screen.active { display: block; animation: glitch-in 0.28s ease; }
  @keyframes glitch-in {
    0% { opacity: 0; transform: translateY(10px) scale(0.98); filter: blur(3px); }
    100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
  }

  label { display: block; font-size: 0.88rem; color: var(--neon-cyan); margin-bottom: 6px; margin-top: 14px; text-transform: uppercase; letter-spacing: 1px; }

  select, input[type="text"] {
    width: 100%; padding: 13px 14px; border-radius: 8px;
    border: 1px solid rgba(0, 243, 255, 0.4);
    background: rgba(0, 0, 0, 0.52);
    color: var(--text-main); font-size: 1.05rem; font-family: var(--font-mono);
    transition: all 0.2s;
  }
  input[type="text"]:focus, select:focus {
    outline: none; border-color: var(--neon-cyan);
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
  }

  button {
    width: 100%; padding: 14px 16px; margin-top: 14px; border: none;
    border-radius: 8px;
    background: rgba(0, 243, 255, 0.1);
    border: 1px solid var(--neon-cyan);
    color: var(--neon-cyan);
    font-family: var(--font-ui); font-size: 1.08rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
    cursor: pointer; transition: all 0.2s;
    box-shadow: 0 0 10px rgba(0, 243, 255, 0.08);
  }
  button:hover:not(:disabled) {
    background: rgba(0, 243, 255, 0.2);
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.38);
    transform: translateY(-2px);
  }
  button:active:not(:disabled) { transform: translateY(0); }
  button:disabled { opacity: 0.32; cursor: not-allowed; border-color: var(--text-muted); color: var(--text-muted); box-shadow: none; }

  button.secondary { border-color: var(--text-muted); color: var(--text-muted); background: rgba(148, 163, 184, 0.08); }
  button.secondary:hover:not(:disabled) { border-color: #fff; color: #fff; box-shadow: 0 0 15px rgba(255, 255, 255, 0.18); }
  button.danger { border-color: var(--neon-red); color: var(--neon-red); background: rgba(255, 0, 60, 0.1); }
  button.danger:hover:not(:disabled) { background: rgba(255, 0, 60, 0.22); box-shadow: 0 0 20px rgba(255, 0, 60, 0.4); }
  button.amber { border-color: var(--neon-amber); color: var(--neon-amber); background: rgba(255, 176, 0, 0.12); }
  button.amber:hover:not(:disabled) { background: rgba(255, 176, 0, 0.24); box-shadow: 0 0 22px rgba(255, 176, 0, 0.45); }
  button.success { border-color: var(--neon-green); color: var(--neon-green); background: rgba(0, 255, 102, 0.1); }
  button.success:hover:not(:disabled) { background: rgba(0, 255, 102, 0.2); box-shadow: 0 0 20px rgba(0, 255, 102, 0.4); }
  button.big { padding: 22px 16px; font-size: 1.18rem; }

  /* LEVEL CARDS SELECTOR */
  .level-grid {
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-top: 8px;
  }
  .level-chip {
    background: rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(148, 163, 184, 0.28);
    border-radius: 10px; padding: 10px 4px; text-align: center;
    cursor: pointer; transition: all 0.2s; margin-top: 0;
    color: var(--text-muted); font-family: var(--font-mono);
    display: flex; flex-direction: column; align-items: center; gap: 2px;
  }
  .level-chip .lv-num { font-size: 1.1rem; font-weight: 700; color: #fff; }
  .level-chip .lv-name { font-size: 0.65rem; letter-spacing: 0.5px; text-transform: uppercase; }
  .level-chip.active {
    border-color: var(--lv-color, var(--neon-cyan));
    background: rgba(0, 243, 255, 0.14);
    box-shadow: 0 0 14px rgba(0, 243, 255, 0.28);
    transform: translateY(-2px);
  }
  .level-chip.active .lv-num, .level-chip.active .lv-name { color: var(--lv-color, var(--neon-cyan)); }
  .level-info-box {
    margin-top: 8px; padding: 10px 12px; border-radius: 8px;
    background: rgba(0, 0, 0, 0.42); border-left: 3px solid var(--neon-cyan);
    font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-main); line-height: 1.45;
  }

  /* CHECKBOX ROW & COLLAPSIBLE */
  .toggle-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 12px; margin-top: 10px; border-radius: 8px;
    background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(0, 243, 255, 0.22);
    font-family: var(--font-mono); font-size: 0.84rem;
  }
  .toggle-row input[type="checkbox"] { width: 18px; height: 18px; accent-color: var(--neon-cyan); cursor: pointer; }

  .mode-grid { display: grid; gap: 14px; margin-top: 18px; }
  .mode-card {
    background: rgba(0, 0, 0, 0.42); border: 1px solid rgba(176, 38, 255, 0.42);
    border-radius: 12px; padding: 18px; cursor: pointer; text-align: left;
    transition: all 0.2s; color: var(--text-main); position: relative; overflow: hidden;
  }
  .mode-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
    background: var(--neon-purple); transition: width 0.2s;
  }
  .mode-card:hover { border-color: var(--neon-purple); box-shadow: 0 0 18px rgba(176, 38, 255, 0.25); transform: translateX(4px); }
  .mode-card:hover::before { width: 100%; opacity: 0.08; }
  .mode-card .icon { font-size: 1.9rem; margin-bottom: 6px; }
  .mode-card .title { font-size: 1.2rem; font-weight: 700; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px; color: #fff; }
  .mode-card .desc { font-size: 0.88rem; color: var(--text-muted); line-height: 1.4; }

  .feature-strip {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 16px;
  }
  .feat-pill {
    background: rgba(0, 243, 255, 0.06); border: 1px solid rgba(0, 243, 255, 0.22);
    border-radius: 8px; padding: 8px 6px; text-align: center;
    font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-muted);
  }
  .feat-pill strong { display: block; color: var(--neon-cyan); font-size: 0.82rem; margin-bottom: 2px; }

  /* ROLE CARD + LOCKED HINT VAULT */
  .role-card {
    text-align: center; padding: 26px 18px; border-radius: 14px; margin-top: 14px;
    position: relative; border: 1px solid;
  }
  .role-card.crew { border-color: var(--neon-green); background: rgba(0, 255, 102, 0.05); box-shadow: inset 0 0 30px rgba(0, 255, 102, 0.09); }
  .role-card.imposter { border-color: var(--neon-red); background: rgba(255, 0, 60, 0.06); box-shadow: inset 0 0 30px rgba(255, 0, 60, 0.12); }
  .role-label { font-size: 0.88rem; text-transform: uppercase; letter-spacing: 2px; color: var(--text-muted); font-family: var(--font-mono); }
  .role-word { font-size: 2.1rem; font-weight: 700; margin: 12px 0; word-break: break-word; text-transform: uppercase; letter-spacing: 2px; }
  .role-card.crew .role-word { color: var(--neon-green); text-shadow: 0 0 15px rgba(0, 255, 102, 0.5); }
  .role-card.imposter .role-word { color: var(--neon-red); text-shadow: 0 0 15px rgba(255, 0, 60, 0.5); }

  .hint-vault {
    margin-top: 14px; padding: 14px; border-radius: 10px;
    background: rgba(0, 0, 0, 0.52); border: 1px dashed rgba(255, 176, 0, 0.55);
  }
  .hint-vault.unlocked {
    border-style: solid; border-color: var(--neon-amber);
    background: rgba(255, 176, 0, 0.08);
    box-shadow: 0 0 16px rgba(255, 176, 0, 0.18);
  }
  .hint-blurred {
    font-family: var(--font-mono); font-size: 0.88rem; color: var(--text-muted);
    letter-spacing: 1px; margin-bottom: 10px;
  }
  .hint-revealed-text {
    font-family: var(--font-mono); font-size: 0.96rem; color: #fff;
    line-height: 1.5; white-space: pre-line;
  }
  .hint-timer-note {
    margin-top: 8px; font-family: var(--font-mono); font-size: 0.76rem; color: var(--neon-amber);
  }

  .progress { text-align: center; font-size: 0.84rem; color: var(--neon-purple); margin-top: 14px; font-family: var(--font-mono); letter-spacing: 1px; }

  .vote-list { display: grid; gap: 10px; margin-top: 14px; }
  .vote-btn {
    margin-top: 0; background: rgba(0, 0, 0, 0.42); border: 1px solid rgba(0, 243, 255, 0.3);
    color: var(--text-main); text-align: left; padding: 14px 16px; border-radius: 8px;
    font-family: var(--font-mono); font-size: 0.98rem; text-transform: uppercase;
    display: flex; justify-content: space-between; align-items: center;
  }
  .vote-btn:hover:not(:disabled) { border-color: var(--neon-cyan); background: rgba(0, 243, 255, 0.1); color: var(--neon-cyan); }
  .vote-btn.selected { border-color: var(--neon-cyan); background: rgba(0, 243, 255, 0.16); color: #fff; box-shadow: 0 0 15px rgba(0, 243, 255, 0.3); }
  .vote-btn.done { opacity: 0.5; border-style: dashed; }

  .notice-box {
    margin: 12px 0; padding: 12px 14px; border-radius: 10px;
    background: rgba(255, 176, 0, 0.12); border: 1px solid var(--neon-amber);
    color: #fff; font-family: var(--font-mono); font-size: 0.9rem; text-align: center;
  }

  .result-detail { text-align: center; color: var(--text-main); font-size: 0.96rem; line-height: 1.75; margin-top: 14px; font-family: var(--font-mono); }
  .result-detail strong { color: #fff; text-shadow: 0 0 5px rgba(255,255,255,0.45); }

  /* CLUE TABS & SUSPECT MARKING */
  .round-tabs { display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap; justify-content: center; }
  .round-tab {
    width: auto; margin-top: 0; padding: 6px 12px; font-size: 0.78rem;
    border-radius: 6px; font-family: var(--font-mono);
    border-color: rgba(148, 163, 184, 0.3); color: var(--text-muted); background: rgba(0,0,0,0.35);
  }
  .round-tab.active { border-color: var(--neon-cyan); color: var(--neon-cyan); background: rgba(0,243,255,0.14); }

  .clue-item {
    padding: 11px 14px; background: rgba(0, 0, 0, 0.42); border-radius: 8px;
    font-size: 0.92rem; color: var(--text-main); line-height: 1.5;
    border-left: 3px solid var(--neon-purple); font-family: var(--font-mono);
    display: flex; justify-content: space-between; align-items: center; gap: 10px;
  }
  .clue-item .name { color: var(--neon-purple); font-weight: 600; text-transform: uppercase; }
  .clue-item.mine { border-left-color: var(--neon-cyan); }
  .clue-item.suspect { border-left-color: var(--neon-red); background: rgba(255, 0, 60, 0.08); }
  .clue-item .play-btn { margin-top: 6px; padding: 5px 10px; font-size: 0.78rem; width: auto; background: rgba(0, 243, 255, 0.1); border: 1px solid var(--neon-cyan); color: var(--neon-cyan); }
  .sus-btn {
    width: auto; margin: 0; padding: 4px 8px; font-size: 0.75rem; border-radius: 6px; flex-shrink: 0;
    border: 1px solid rgba(255,255,255,0.2); color: var(--text-muted); background: transparent;
  }
  .sus-btn.marked { border-color: var(--neon-red); color: var(--neon-red); background: rgba(255,0,60,0.15); }

  .round-header { text-align: center; margin: 8px 0 10px; font-size: 0.88rem; color: var(--neon-cyan); font-weight: 600; letter-spacing: 2px; text-transform: uppercase; font-family: var(--font-mono); }
  .error { color: var(--neon-red); text-align: center; font-size: 0.88rem; margin-top: 10px; min-height: 1em; font-family: var(--font-mono); text-shadow: 0 0 5px rgba(255, 0, 60, 0.5); }

  .vote-summary { margin-top: 12px; display: grid; gap: 8px; }
  .vote-row { display: flex; justify-content: space-between; padding: 10px 14px; background: rgba(0, 0, 0, 0.42); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; font-size: 0.92rem; color: var(--text-main); font-family: var(--font-mono); }
  .vote-row .count { color: var(--neon-cyan); font-weight: 600; }
  .vote-row.top { border-color: var(--neon-cyan); box-shadow: 0 0 10px rgba(0, 243, 255, 0.14); }

  .code-row { display: flex; gap: 8px; align-items: stretch; margin: 12px 0; }
  .code-box {
    flex: 1; text-align: center; font-size: 2.2rem; font-weight: 800; letter-spacing: 7px; font-family: var(--font-mono);
    color: #fff; background: rgba(0, 0, 0, 0.6); padding: 12px; border-radius: 12px;
    border: 1px solid var(--neon-cyan); box-shadow: 0 0 18px rgba(0, 243, 255, 0.18), inset 0 0 14px rgba(0, 243, 255, 0.08);
    user-select: all; text-shadow: 0 0 10px var(--neon-cyan);
  }
  .copy-btn { width: auto; margin: 0; padding: 0 14px; font-size: 0.85rem; white-space: nowrap; }

  .players-list { display: grid; gap: 8px; margin-top: 14px; }
  .player-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(0, 0, 0, 0.42); border-radius: 8px; font-size: 0.92rem; font-family: var(--font-mono); border: 1px solid rgba(148,163,184,0.12); }
  .player-row .tag { font-size: 0.78rem; color: var(--text-muted); }
  .player-row.ready { border-color: var(--neon-green); background: rgba(0, 255, 102, 0.05); }
  .player-row.ready .tag { color: var(--neon-green); }
  .player-row.eliminated { opacity: 0.45; text-decoration: line-through; border-color: rgba(255,0,60,0.3); }

  .tabs { display: flex; gap: 10px; margin-top: 14px; }
  .tabs button { margin-top: 0; }
  .small { font-size: 0.78rem; color: var(--text-muted); text-align: center; margin-top: 10px; font-family: var(--font-mono); }

  .qr-wrap { text-align: center; margin: 12px 0; }
  .qr-wrap img { width: 155px; height: 155px; border-radius: 12px; background: white; padding: 8px; box-shadow: 0 0 18px rgba(0, 243, 255, 0.28); }

  .imposter-pill { display: inline-block; background: rgba(255, 0, 60, 0.12); color: var(--neon-red); border: 1px solid var(--neon-red); border-radius: 4px; padding: 4px 12px; font-size: 0.85rem; margin: 4px; text-transform: uppercase; font-family: var(--font-mono); box-shadow: 0 0 8px rgba(255,0,60,0.2); }

  .banner { text-align: center; padding: 18px 14px; border-radius: 12px; margin-top: 10px; font-size: 1.35rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; border: 1px solid; }
  .banner.crew { border-color: var(--neon-green); background: rgba(0, 255, 102, 0.1); color: #fff; text-shadow: 0 0 10px var(--neon-green); box-shadow: 0 0 20px rgba(0, 255, 102, 0.2); }
  .banner.imposter { border-color: var(--neon-red); background: rgba(255, 0, 60, 0.1); color: #fff; text-shadow: 0 0 10px var(--neon-red); box-shadow: 0 0 20px rgba(255, 0, 60, 0.2); }
  .banner.tie { border-color: #fde68a; background: rgba(253, 224, 71, 0.1); color: #fff; text-shadow: 0 0 10px #fde68a; }

  .pass-banner { text-align: center; padding: 28px 18px; background: rgba(0, 243, 255, 0.05); border: 1px dashed var(--neon-cyan); border-radius: 12px; margin-bottom: 14px; }
  .pass-banner .who { font-size: 1.55rem; font-weight: 700; color: #fff; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
  .pass-banner .msg { font-size: 0.92rem; color: var(--text-muted); line-height: 1.5; font-family: var(--font-mono); }

  .recorder { display: flex; align-items: center; gap: 14px; background: rgba(0,0,0,0.42); border: 1px solid rgba(255, 0, 60, 0.3); border-radius: 12px; padding: 14px; margin-top: 10px; }
  .rec-btn { width: 58px; height: 58px; border-radius: 50%; background: rgba(255, 0, 60, 0.1); border: 2px solid var(--neon-red); color: var(--neon-red); font-size: 1.45rem; padding: 0; margin: 0; flex-shrink: 0; cursor: pointer; transition: all 0.2s; }
  .rec-btn.recording { background: var(--neon-red); color: #fff; animation: pulse-red 1s infinite; }
  @keyframes pulse-red { 0%, 100% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0.7); } 50% { box-shadow: 0 0 0 14px rgba(255, 0, 60, 0); } }
  .rec-info { flex: 1; font-size: 0.86rem; color: var(--text-main); line-height: 1.4; font-family: var(--font-mono); }
  .rec-timer { color: var(--neon-red); font-weight: 700; font-size: 1.05rem; }
  .rec-clear { padding: 7px 14px; font-size: 0.8rem; width: auto; margin: 0; background: transparent; border: 1px solid var(--text-muted); color: var(--text-muted); }

  .scoreboard { background: rgba(0, 0, 0, 0.42); border: 1px solid rgba(176, 38, 255, 0.35); border-radius: 12px; padding: 14px; margin-top: 16px; }
  .scoreboard h4 { font-size: 0.88rem; color: var(--neon-purple); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 2px; text-align: center; }
  .score-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; font-size: 0.9rem; font-family: var(--font-mono); border-bottom: 1px solid rgba(255,255,255,0.06); }
  .score-row:last-child { border-bottom: none; }
  .score-row .pts { color: var(--neon-cyan); font-weight: 700; }
  .rank-tag { font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; background: rgba(176,38,255,0.16); color: #d8b4fe; margin-left: 6px; }
  .streak-tag { font-size: 0.72rem; color: var(--neon-amber); margin-left: 6px; }

  .badge { display: inline-block; background: rgba(0, 243, 255, 0.1); border: 1px solid var(--neon-cyan); color: var(--neon-cyan); padding: 3px 10px; border-radius: 5px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; font-family: var(--font-mono); letter-spacing: 1px; }
  .badge.local { background: rgba(0, 255, 102, 0.1); border-color: var(--neon-green); color: var(--neon-green); }
  .badge.level { background: rgba(176, 38, 255, 0.14); border-color: var(--neon-purple); color: #e9d5ff; }

  /* LAST STAND BOX */
  .last-stand-box {
    text-align: center; padding: 24px 18px; border-radius: 14px;
    border: 1px solid var(--neon-red); background: rgba(255, 0, 60, 0.08);
    box-shadow: 0 0 28px rgba(255, 0, 60, 0.25); margin-top: 12px;
  }
  .last-stand-clock { font-family: var(--font-mono); font-size: 2.5rem; color: var(--neon-red); font-weight: 700; margin: 10px 0; }

  /* FABS & MODALS */
  .chat-fab { position: fixed; bottom: 22px; right: 22px; width: 56px; height: 56px; border-radius: 50%; background: var(--bg-card); border: 1px solid var(--neon-cyan); box-shadow: 0 0 18px rgba(0, 243, 255, 0.3); color: var(--neon-cyan); font-size: 1.4rem; padding: 0; margin: 0; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 100; }
  .chat-fab .unread { position: absolute; top: 0; right: 0; background: var(--neon-red); color: #fff; font-size: 0.72rem; font-family: var(--font-mono); min-width: 20px; height: 20px; border-radius: 10px; display: flex; align-items: center; justify-content: center; padding: 0 4px; font-weight: 700; }

  .chat-panel { position: fixed; inset: 0; background: rgba(5, 5, 15, 0.96); backdrop-filter: blur(10px); z-index: 200; display: none; flex-direction: column; }
  .chat-panel.open { display: flex; }
  .chat-header { padding: 18px 20px; border-bottom: 1px solid rgba(0, 243, 255, 0.3); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.5); }
  .chat-header h3 { font-size: 1.15rem; text-transform: uppercase; letter-spacing: 2px; color: var(--neon-cyan); }
  .chat-close { background: transparent; border: none; color: var(--text-muted); font-size: 2rem; width: auto; padding: 0 8px; margin: 0; cursor: pointer; }
  .chat-messages { flex: 1; overflow-y: auto; padding: 18px; display: flex; flex-direction: column; gap: 10px; }
  .chat-msg { max-width: 85%; padding: 10px 14px; border-radius: 8px; font-size: 0.92rem; line-height: 1.4; font-family: var(--font-mono); word-wrap: break-word; }
  .chat-msg.mine { align-self: flex-end; background: rgba(0, 243, 255, 0.1); border: 1px solid var(--neon-cyan); color: #fff; border-bottom-right-radius: 0; }
  .chat-msg.other { align-self: flex-start; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-main); border-bottom-left-radius: 0; }
  .chat-msg.system { align-self: center; background: transparent; color: var(--neon-purple); font-size: 0.78rem; font-style: italic; text-align: center; padding: 6px; }
  .chat-msg .sender { font-size: 0.72rem; opacity: 0.85; margin-bottom: 3px; font-weight: 700; text-transform: uppercase; color: var(--neon-purple); }
  .chat-input-row { padding: 14px 18px 26px; border-top: 1px solid rgba(0, 243, 255, 0.3); display: flex; gap: 10px; background: rgba(0,0,0,0.5); }
  .chat-input-row input { flex: 1; margin: 0; }
  .chat-input-row button { width: auto; padding: 12px 20px; margin: 0; }
  .chat-locked { padding: 14px; text-align: center; color: var(--neon-red); font-size: 0.88rem; font-family: var(--font-mono); background: rgba(255, 0, 60, 0.1); border-top: 1px solid rgba(255, 0, 60, 0.3); }

  .menu-fab { position: fixed; bottom: 22px; left: 22px; width: 48px; height: 48px; border-radius: 50%; background: var(--bg-card); border: 1px solid rgba(255, 255, 255, 0.25); color: #fff; font-size: 1.3rem; padding: 0; margin: 0; z-index: 100; display: flex; align-items: center; justify-content: center; cursor: pointer; }
  .menu-panel { position: fixed; inset: 0; background: rgba(5, 5, 15, 0.85); backdrop-filter: blur(6px); z-index: 300; display: none; align-items: center; justify-content: center; padding: 20px; }
  .menu-panel.open { display: flex; }
  .menu-card { background: var(--bg-card); border: 1px solid var(--neon-cyan); border-radius: 16px; padding: 24px; max-width: 420px; width: 100%; box-shadow: 0 0 30px rgba(0, 243, 255, 0.22); }
  .menu-card h3 { margin-bottom: 14px; text-align: center; font-size: 1.35rem; text-transform: uppercase; letter-spacing: 2px; color: #fff; }

  /* TUTORIAL MODAL */
  .tutorial-modal { position: fixed; inset: 0; background: rgba(5, 5, 15, 0.95); backdrop-filter: blur(8px); z-index: 500; display: none; align-items: center; justify-content: center; padding: 20px; overflow: hidden; }
  .tutorial-modal.open { display: flex; }
  .tutorial-bg { position: absolute; inset: 0; z-index: 1; pointer-events: none; opacity: 0.15; }
  .bg-grid { position: absolute; inset: -100%; background-image: linear-gradient(var(--neon-cyan) 1px, transparent 1px), linear-gradient(90deg, var(--neon-cyan) 1px, transparent 1px); background-size: 40px 40px; animation: moveGrid 20s linear infinite; }
  @keyframes moveGrid { 0% { transform: translate(0, 0); } 100% { transform: translate(40px, 40px); } }
  .bg-spy { position: absolute; bottom: 10%; left: -100px; font-size: 5rem; animation: sneak 8s linear infinite; }
  @keyframes sneak { 0% { left: -100px; transform: scaleX(1); } 45% { left: 50%; transform: scaleX(1); } 50% { left: 50%; transform: scaleX(-1); } 95% { left: -100px; transform: scaleX(-1); } 100% { left: -100px; transform: scaleX(1); } }
  .tutorial-card { position: relative; z-index: 10; background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(12px); border: 1px solid var(--neon-cyan); border-radius: 16px; padding: 22px; max-width: 500px; width: 100%; max-height: 85vh; overflow-y: auto; }
  .tutorial-step { margin-bottom: 14px; padding-left: 14px; border-left: 2px solid var(--neon-purple); }
  .tutorial-step h4 { color: #fff; font-size: 1.02rem; margin-bottom: 3px; text-transform: uppercase; }
  .tutorial-step p { color: var(--text-main); font-size: 0.86rem; line-height: 1.48; font-family: var(--font-mono); }

  /* LIVE REACTION BAR */
  .reaction-bar { position: fixed; bottom: 22px; left: 50%; transform: translateX(-50%); display: none; gap: 6px; background: rgba(15, 23, 42, 0.85); border: 1px solid var(--neon-cyan); padding: 6px 10px; border-radius: 30px; z-index: 150; backdrop-filter: blur(4px); }
  .reaction-bar.active { display: flex; }
  .reaction-btn { background: transparent; border: none; font-size: 1.4rem; padding: 4px; margin: 0; cursor: pointer; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; }
  .reaction-btn:hover { transform: scale(1.22); }
  .floating-reaction { position: fixed; bottom: 80px; font-size: 2.8rem; pointer-events: none; z-index: 9999; animation: floatUp 2s ease-out forwards; }
  @keyframes floatUp { 0% { opacity: 1; transform: translateY(0) scale(0.5); } 20% { transform: translateY(-20px) scale(1.2); } 100% { opacity: 0; transform: translateY(-150px) scale(1); } }
</style>
</head>
<body>
<div class="app">
  <!-- TOP HUD BAR -->
  <div class="top-bar">
    <div class="top-badges">
      <span id="modeBadge" class="badge" style="display:none;"></span>
      <span id="levelBadge" class="badge level" style="display:none;">LVL 1 • ROOKIE</span>
    </div>
    <div class="top-actions">
      <button id="rolePeekBtn" class="icon-btn amber" onclick="openRolePeek()" title="See My Role & Hint" style="display:none;">👁️</button>
      <button id="sfxBtn" class="icon-btn" onclick="toggleSfx()" title="Toggle Sound">🔊</button>
      <button class="icon-btn purple" onclick="toggleTutorial()" title="How to Play">?</button>
    </div>
  </div>

  <!-- 7-SECOND HINT COUNTDOWN TIMER HUD -->
  <div class="hint-timer-hud" id="hintTimerHud">
    <div class="timer-top">
      <div class="timer-label"><span class="timer-dot"></span><span id="hintTimerLabel">⏱️ HINT VISIBLE — MEMORIZE FAST!</span></div>
      <div class="timer-clock" id="hintTimerClock">00:07</div>
    </div>
    <div class="timer-bar-bg"><div class="timer-bar-fill" id="hintTimerFill"></div></div>
  </div>

  <h1>Imposter Protocol</h1>
  <p class="subtitle">Advanced Social Deduction • Levels 1–5 • 7s Hint Timer</p>

  <!-- MODE PICKER -->
  <div id="screen-mode" class="screen active">
    <div class="mode-grid">
      <div class="mode-card" onclick="pickMode('online')">
        <div class="icon">🌐</div>
        <div class="title">Network Link (Multiplayer)</div>
        <div class="desc">Play online across devices with live Lobby Code, QR, Voice Clues, Levels 1–5 &amp; 7-second Hint Timer.</div>
      </div>
      <div class="mode-card" onclick="pickMode('local')">
        <div class="icon">📱</div>
        <div class="title">Local Terminal (Pass &amp; Play)</div>
        <div class="desc">Pass one device around. Full 5-Level progression, 7-second Hint Timer, Suspect Marking &amp; Imposter Last-Stand.</div>
      </div>
    </div>
    <div class="feature-strip">
      <div class="feat-pill"><strong>5 LEVELS</strong>Beginner → Pro</div>
      <div class="feat-pill"><strong>7s TIMER</strong>Hint Auto-Locks</div>
      <div class="feat-pill"><strong>LAST STAND</strong>Imposter Word Steal</div>
    </div>
    <div class="small" id="resumeHint" style="display:none; margin-top:18px;">
      <button class="secondary" onclick="resumeSession()">Resume Active Link</button>
    </div>
  </div>

  <!-- ONLINE HOME -->
  <div id="screen-home" class="screen">
    <button class="secondary" onclick="backToMode()" style="width:auto;padding:8px 14px;font-size:0.85rem;margin:0 0 12px;">← Disconnect</button>
    <label for="playerName">Agent Name</label>
    <input type="text" id="playerName" maxlength="20" placeholder="ENTER ID..." autocomplete="off">
    <div class="tabs">
      <button onclick="createGame()">Host Game</button>
      <button class="secondary" onclick="showJoin()">Join Game</button>
    </div>
    <div id="joinBox" style="display:none; margin-top:14px;">
      <label for="joinCode">Lobby Code</label>
      <input type="text" id="joinCode" maxlength="6" placeholder="XK4P2Q"
             style="text-transform:uppercase;letter-spacing:6px;text-align:center;font-size:1.45rem;" autocomplete="off">
      <button onclick="joinGame()">Establish Connection</button>
    </div>
    <label for="lang" style="margin-top:20px;">Language / भाषा</label>
    <select id="lang">
      <option value="en">English</option>
      <option value="hi">हिन्दी (Hindi)</option>
    </select>
    <div id="homeError" class="error"></div>
  </div>

  <!-- LOCAL SETUP -->
  <div id="screen-local-setup" class="screen">
    <button class="secondary" onclick="backToMode()" style="width:auto;padding:8px 14px;font-size:0.85rem;margin:0 0 10px;">← Disconnect</button>
    <h2>Local Terminal</h2>
    <p class="subtitle">Select Level, Agents &amp; Mission Parameters.</p>

    <label>Difficulty Level (1–5)</label>
    <div class="level-grid" id="localLevelGrid"></div>
    <div class="level-info-box" id="localLevelDesc"></div>

    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
      <div>
        <label for="localLang">Language / भाषा</label>
        <select id="localLang" onchange="updateLocalLevelDesc()">
          <option value="en">English</option>
          <option value="hi">हिन्दी (Hindi)</option>
        </select>
      </div>
      <div>
        <label for="localCategory">Word Category</label>
        <select id="localCategory"><option value="All">All Categories</option></select>
      </div>
    </div>

    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
      <div>
        <label for="localNumPlayers">Agents (3–10)</label>
        <input type="text" id="localNumPlayers" value="4" inputmode="numeric" style="text-align:center;font-size:1.2rem;">
      </div>
      <div>
        <label for="localNumImposters">Imposters</label>
        <select id="localNumImposters"><option value="1">1 Imposter</option></select>
      </div>
    </div>
    <div class="small" id="localImposterNote" style="margin-top:4px;"></div>

    <div class="toggle-row">
      <span>🔥 Imposter Last-Stand Guess (25s)</span>
      <input type="checkbox" id="localLastGuess">
    </div>
    <div class="toggle-row">
      <span>✍️ Use Custom Secret Word</span>
      <input type="checkbox" id="localCustomToggle" onchange="$('localCustomBox').style.display = this.checked ? 'block' : 'none'">
    </div>
    <div id="localCustomBox" style="display:none; margin-top:8px;">
      <input type="text" id="localCustomWord" maxlength="40" placeholder="Custom Secret Word..." style="margin-bottom:8px;">
      <input type="text" id="localCustomHint" maxlength="120" placeholder="Custom Imposter Hint...">
    </div>

    <div id="localNameInputs" style="margin-top:10px;"></div>
    <button class="success" onclick="startLocalGame()" style="margin-top:18px;">▶ Initialize Protocol</button>
    <div id="localError" class="error"></div>
  </div>

  <!-- ONLINE LOBBY -->
  <div id="screen-lobby" class="screen">
    <h2>Waiting Room</h2>
    <p class="subtitle">Scan QR or share Lobby Code</p>
    <div class="code-row">
      <div class="code-box" id="lobbyCode">------</div>
      <button class="secondary copy-btn" id="copyLinkBtn" onclick="copyInviteLink()">📋 Copy Link</button>
    </div>
    <div class="qr-wrap" id="qrWrap"></div>
    <div class="players-list" id="lobbyPlayers"></div>
    <div class="progress" id="lobbyProgress"></div>

    <!-- HOST / MISSION SETTINGS -->
    <div id="hostSettingsBox" style="margin-top:14px;">
      <label>Mission Level (1–5)</label>
      <div class="level-grid" id="onlineLevelGrid"></div>
      <div class="level-info-box" id="onlineLevelDesc"></div>

      <div id="hostExtraControls" style="display:none;">
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
          <div>
            <label for="numImposters">Imposter Count</label>
            <select id="numImposters" onchange="syncHostConfig()"></select>
          </div>
          <div>
            <label for="onlineCategory">Category</label>
            <select id="onlineCategory" onchange="syncHostConfig()"><option value="All">All Categories</option></select>
          </div>
        </div>
        <div class="small" id="imposterNote"></div>
        <div class="toggle-row">
          <span>🔥 Imposter Last-Stand Guess (25s)</span>
          <input type="checkbox" id="onlineLastGuess" onchange="syncHostConfig()">
        </div>
        <div class="toggle-row">
          <span>✍️ Custom Secret Word</span>
          <input type="checkbox" id="onlineCustomToggle" onchange="$('onlineCustomBox').style.display = this.checked ? 'block' : 'none'">
        </div>
        <div id="onlineCustomBox" style="display:none; margin-top:8px;">
          <input type="text" id="onlineCustomWord" maxlength="40" placeholder="Custom Secret Word..." style="margin-bottom:8px;">
          <input type="text" id="onlineCustomHint" maxlength="120" placeholder="Custom Imposter Hint...">
        </div>
      </div>
    </div>

    <button id="lobbyReadyBtn" onclick="toggleReady()" style="margin-top:18px;">Ready Up</button>
    <button id="lobbyStartBtn" class="success" onclick="startGame()" style="display:none; margin-top:12px;">▶ Start Protocol</button>
    <div class="error" id="lobbyError"></div>
    <div class="small">Syncing live telemetry...</div>
  </div>

  <!-- LOCAL PASS SCREEN -->
  <div id="screen-pass" class="screen">
    <div class="pass-banner">
      <div class="who">Pass Terminal to <span id="passWho">Agent 1</span></div>
      <div class="msg">Ensure no other agents are watching the screen.</div>
    </div>
    <button class="big" onclick="revealRole()">I am <span id="passWhoInline">Agent 1</span> — Show Role</button>
  </div>

  <!-- ROLE REVEAL + SEE HINT (7-SECOND TIMER) -->
  <div id="screen-reveal" class="screen">
    <div class="round-header" id="revealRound">ROLE REVEAL</div>
    <h2>Your Secret Role</h2>
    <p class="subtitle">Memorize this. Tap "See Hint" to view intel for 7 seconds.</p>
    <div id="revealCard" class="role-card">
      <div class="role-label" id="revealLabel">—</div>
      <div class="role-word" id="revealWord">—</div>
      <div class="hint-vault" id="revealHintVault">
        <div id="revealHintLocked">
          <div class="hint-blurred">🔒 ENCRYPTED INTEL LOCKED</div>
          <button class="amber" id="seeHintBtn" onclick="triggerSeeHint()" style="margin-top:6px;">👁️ SEE HINT (7 SEC TIMER)</button>
        </div>
        <div id="revealHintUnlocked" style="display:none;">
          <div class="hint-revealed-text" id="revealHintText"></div>
          <div class="hint-timer-note" id="revealHintTimerNote">⏱️ Hiding in 7s...</div>
        </div>
        <div id="revealHintExpired" style="display:none;">
          <div class="hint-blurred" style="margin-bottom:0; color:var(--neon-red);">🔒 HINT LOCKED — 7s TIME UP</div>
        </div>
      </div>
    </div>
    <button class="success" onclick="hostAdvance()" id="revealNextBtn" style="display:none;">Proceed to Clues →</button>
    <button class="secondary" onclick="localHideAndContinue()" id="revealLocalBtn" style="display:none;">Hide &amp; Continue</button>
    <div class="progress" id="revealProgress">Waiting for host...</div>
  </div>

  <!-- CLUE PHASE -->
  <div id="screen-clue" class="screen">
    <div class="round-header" id="clueRoundHeader">ROUND 1 — CLUES</div>
    <h2>Transmit Clue</h2>
    <p class="subtitle">Provide a smart clue. Do not say the secret word.</p>
    <div style="text-align:center; margin-bottom:12px; display:flex; justify-content:center; gap:8px; flex-wrap:wrap;">
      <span class="badge" id="cluePlayerName">—</span>
      <button class="amber" id="clueSeeHintBtn" onclick="openRolePeek()" style="width:auto;margin:0;padding:4px 12px;font-size:0.78rem;">👁️ See Role / Hint (7s)</button>
    </div>
    <label for="clueInput">Text Transmission</label>
    <input type="text" id="clueInput" maxlength="80" placeholder="ENTER CLUE..." autocomplete="off">
    <button id="clueSubmitBtn" onclick="submitClue()">Send Text</button>
    <div style="text-align:center;color:var(--neon-cyan);font-size:0.85rem;margin:14px 0 8px; font-family: var(--font-mono);">— OR RECORD VOICE —</div>
    <div class="recorder" id="recorderBox">
      <button class="rec-btn" id="recBtn" onclick="toggleRecording()">🎙️</button>
      <div class="rec-info" id="recInfo">Tap to record voice clue.<br>Max 10 seconds.</div>
      <button class="rec-clear" id="recClearBtn" onclick="clearRecording()" style="display:none;">Clear</button>
    </div>
    <audio id="recPlayback" controls style="width:100%;margin-top:10px;display:none; border-radius:8px;"></audio>
    <button id="voiceSubmitBtn" onclick="submitVoice()" style="display:none;">Send Audio</button>
    <div class="error" id="clueError"></div>
    <div class="players-list" id="clueWaitingList"></div>
    <div class="progress" id="clueProgress"></div>
  </div>

  <!-- SUMMARY / DATA LOG (ALL ROUNDS + SUSPECT MARKING) -->
  <div id="screen-summary" class="screen">
    <div class="round-header" id="summaryHeader">ROUND 1 COMPLETE</div>
    <h2>Clue Intelligence Log</h2>
    <p class="subtitle">Compare clues across rounds &amp; flag suspects 🔍</p>
    <div class="round-tabs" id="summaryTabs"></div>
    <div id="summaryList" style="display:grid;gap:9px;margin-top:12px;"></div>
    <button class="success" onclick="hostAdvance()" id="summaryNextBtn" style="display:none;">Next Round →</button>
    <div class="progress" id="summaryProgress">Waiting for host...</div>
  </div>

  <!-- VOTING PHASE -->
  <div id="screen-vote" class="screen">
    <h2>Voting Phase</h2>
    <p class="subtitle">Identify and eject the Imposter.</p>
    <div id="voteElimNotice" class="notice-box" style="display:none;"></div>
    <div style="text-align:center; margin-bottom:12px;"><span class="badge" id="voteVoterName">—</span></div>
    <label>Select Target</label>
    <div id="voteList" class="vote-list"></div>
    <button id="voteSubmitBtn" class="danger" onclick="submitVote()" disabled>Lock Vote</button>
    <div class="error" id="voteError"></div>
    <div class="players-list" id="voteWaitingList"></div>
    <div class="small" id="voteChatHint">💬 Use Secure Comms to debate clues.</div>
  </div>

  <!-- IMPOSTER LAST STAND (SECRET WORD GUESS) -->
  <div id="screen-last-guess" class="screen">
    <div class="round-header">🔥 IMPOSTER LAST STAND</div>
    <h2>Final Counter-Attack!</h2>
    <div class="last-stand-box">
      <div class="role-label" id="lastGuessInfo">Caught Imposter gets ONE shot to guess the Secret Word!</div>
      <div class="last-stand-clock" id="lastGuessClock">25s</div>
      <div id="lastGuessInputWrap" style="display:none;">
        <input type="text" id="lastGuessInput" maxlength="60" placeholder="TYPE EXACT SECRET WORD..." autocomplete="off">
        <button class="danger" onclick="submitImposterGuess()">⚡ Submit Final Guess</button>
      </div>
      <div class="small" id="lastGuessWaitMsg" style="display:none;">Waiting for the caught Imposter to guess...</div>
    </div>
  </div>

  <!-- RESULT SCREEN -->
  <div id="screen-result" class="screen">
    <div id="resultBanner" class="banner">—</div>
    <div class="result-detail" id="resultDetail"></div>
    <div id="voteSummaryBox" style="margin-top:16px;">
      <div class="round-header">VOTE TALLY</div>
      <div id="voteSummary" class="vote-summary"></div>
    </div>
    <div id="imposterBox" style="margin-top:16px;text-align:center;"></div>
    <div class="scoreboard" id="scoreboard"></div>
    <div id="resultClues" style="margin-top:16px;"></div>
    <button class="success" onclick="nextLevelPlay()" id="nextLevelBtn" style="display:none;">🚀 Advance to Next Level →</button>
    <button onclick="playAgain()" id="playAgainBtn" style="display:none;">Play Same Level Again</button>
    <button class="secondary" onclick="backToMode()" style="margin-top:12px;">Disconnect</button>
    <div class="progress" id="resultProgress"></div>
  </div>
</div>

<!-- LIVE REACTION BAR -->
<div class="reaction-bar" id="reactionBar">
  <button class="reaction-btn" onclick="sendReaction('😂')">😂</button>
  <button class="reaction-btn" onclick="sendReaction('😱')">😱</button>
  <button class="reaction-btn" onclick="sendReaction('🤔')">🤔</button>
  <button class="reaction-btn" onclick="sendReaction('🔥')">🔥</button>
  <button class="reaction-btn" onclick="sendReaction('🕵️')">🕵️</button>
</div>

<!-- ROLE & HINT PEEK MODAL -->
<div class="menu-panel" id="rolePeekModal">
  <div class="menu-card">
    <h3>👁️ Secret Intel</h3>
    <div id="peekCard" class="role-card" style="margin-top:4px; padding:18px 14px;">
      <div class="role-label" id="peekLabel">—</div>
      <div class="role-word" id="peekWord" style="font-size:1.7rem;">—</div>
      <div class="hint-vault" id="peekHintVault" style="margin-top:10px;">
        <div id="peekHintLocked">
          <div class="hint-blurred">🔒 HINT LOCKED</div>
          <button class="amber" onclick="triggerSeeHint(true)" style="margin-top:6px;">👁️ SEE HINT (7 SEC TIMER)</button>
        </div>
        <div id="peekHintUnlocked" style="display:none;">
          <div class="hint-revealed-text" id="peekHintText"></div>
          <div class="hint-timer-note" id="peekTimerNote">⏱️ Hiding in 7s...</div>
        </div>
        <div id="peekHintExpired" style="display:none;">
          <div class="hint-blurred" style="margin-bottom:0; color:var(--neon-red);">🔒 HINT LOCKED — 7s TIME UP</div>
        </div>
      </div>
    </div>
    <button class="secondary" onclick="closeRolePeek()">Close Intel</button>
  </div>
</div>

<!-- TUTORIAL MODAL -->
<div class="tutorial-modal" id="tutorialModal">
  <div class="tutorial-bg">
    <div class="bg-grid"></div>
    <div class="bg-spy">🕵️</div>
  </div>
  <div class="tutorial-card">
    <h2>How to Play — Advanced Edition</h2>
    <div class="tutorial-step">
      <h4>1. Choose a Level (1–5)</h4>
      <p><strong>Level 1 Beginner</strong> (Super easy words, clear hint) up to <strong>Level 5 Pro</strong> (Clever mystery words, 3 rounds, Last-Stand). Advance levels after every match!</p>
    </div>
    <div class="tutorial-step">
      <h4>2. 7-Second Hint Timer (⏱️ 00:07)</h4>
      <p>Clicking <strong>"👁️ See Hint"</strong> reveals your hint for <strong>7 seconds</strong> with a live countdown. Memorize it fast before it automatically locks again!</p>
    </div>
    <div class="tutorial-step">
      <h4>3. Multi-Round Clues &amp; Suspect Marking</h4>
      <p>Give clever text or voice clues without saying the secret word. Review all past rounds in the Data Log and tap <strong>🔍</strong> to mark suspicious agents.</p>
    </div>
    <div class="tutorial-step">
      <h4>4. Imposter Last Stand (Levels 4–5)</h4>
      <p>When caught, the Imposter gets <strong>25 seconds</strong> to guess the exact secret word and steal the victory — so Crew must not be too obvious!</p>
    </div>
    <div class="tutorial-step">
      <h4>5. Ranks &amp; Win Streaks</h4>
      <p>Earn points, build 🔥 Win Streaks, and climb ranks from <strong>Rookie</strong> to <strong>Phantom Legend</strong>.</p>
    </div>
    <button onclick="toggleTutorial()">Understood</button>
  </div>
</div>

<!-- CHAT FAB & PANEL -->
<button class="chat-fab" id="chatFab" onclick="toggleChat()" style="display:none;">
  💬<span class="unread" id="chatUnread" style="display:none;">0</span>
</button>
<div class="chat-panel" id="chatPanel">
  <div class="chat-header">
    <h3>Secure Comms</h3>
    <button class="chat-close" onclick="toggleChat()">×</button>
  </div>
  <div class="chat-messages" id="chatMessages"></div>
  <div class="chat-locked" id="chatLocked" style="display:none;">Submit your clue first to unlock Comms.</div>
  <div class="chat-input-row" id="chatInputRow">
    <input type="text" id="chatInput" maxlength="200" placeholder="Transmit message..." autocomplete="off">
    <button onclick="sendChat()">Send</button>
  </div>
</div>

<!-- SYSTEM MENU -->
<button class="menu-fab" id="menuFab" onclick="toggleMenu()" style="display:none;">☰</button>
<div class="menu-panel" id="menuPanel">
  <div class="menu-card">
    <h3>System Menu</h3>
    <div class="small" style="margin-bottom:16px;">
      Lobby: <strong id="menuRoomCode">------</strong><br>
      Agent: <strong id="menuYouName">—</strong><br>
      Rank: <strong id="menuYouRank">Rookie</strong>
    </div>
    <button class="secondary" onclick="leaveGame()">🚪 Disconnect</button>
    <button class="danger" id="menuEndBtn" onclick="endGame()" style="display:none;">🛑 Terminate Lobby</button>
    <button class="secondary" onclick="toggleMenu()">Cancel</button>
  </div>
</div>
<script>
const STORAGE_KEY = 'imposter_session_v10';
const HINT_TIMER_DURATION = 7; // 7-second countdown timer when hint is viewed
const LAST_GUESS_DURATION = 25;

const DEFAULT_LEVELS = {
  1: { level: 1, name: 'Beginner', name_hi: 'शुरुआती', tag: 'SUPER EASY', rounds: 2, hint_style: 'full', last_guess: false, crew_pts: 100, imposter_pts: 150, color: '#00ff66', desc: 'Very simple words • Full clear hint (7s) • 2 clue rounds', desc_hi: 'बहुत आसान शब्द • पूरा हिंट (7 सेकंड) • 2 क्लू राउंड' },
  2: { level: 2, name: 'Easy', name_hi: 'आसान', tag: 'EASY', rounds: 2, hint_style: 'full', last_guess: false, crew_pts: 125, imposter_pts: 175, color: '#00f3ff', desc: 'Everyday familiar words • Full clear hint (7s) • 2 clue rounds', desc_hi: 'रोज़मर्रा के आसान शब्द • पूरा हिंट (7 सेकंड) • 2 क्लू राउंड' },
  3: { level: 3, name: 'Medium', name_hi: 'मध्यम', tag: 'MEDIUM', rounds: 2, hint_style: 'full', last_guess: false, crew_pts: 150, imposter_pts: 225, color: '#b026ff', desc: 'Fun places & objects • Helpful hint (7s) • 2 clue rounds', desc_hi: 'मज़ेदार जगहें और चीज़ें • मददगार हिंट (7 सेकंड) • 2 क्लू राउंड' },
  4: { level: 4, name: 'Smart', name_hi: 'स्मार्ट', tag: 'MODERATE', rounds: 3, hint_style: 'subtle', last_guess: true, crew_pts: 225, imposter_pts: 325, color: '#ff9900', desc: 'Fun creative words • Subtle hint (7s) • 3 rounds • Last-Stand', desc_hi: 'रोचक शब्द • हल्का हिंट (7 सेकंड) • 3 राउंड • अंतिम अनुमान' },
  5: { level: 5, name: 'Pro', name_hi: 'प्रो', tag: 'CHALLENGE', rounds: 3, hint_style: 'subtle', last_guess: true, crew_pts: 300, imposter_pts: 450, color: '#ff003c', desc: 'Clever mystery words • Short hint (7s) • 3 rounds • Last-Stand', desc_hi: 'चतुर रहस्यमय शब्द • छोटा हिंट (7 सेकंड) • 3 राउंड • अंतिम अनुमान' },
};

let LEVELS_DATA = { ...DEFAULT_LEVELS };
let CATEGORIES_DATA = ['Abstract', 'Daily Life', 'Food', 'Gadgets', 'Nature', 'Places', 'Professions', 'Science', 'Sports', 'Transport'];

let session = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
let current = null;
let pollTimer = null;
let selectedVote = null;
let chatOpen = false;
let lastChatCount = 0;
let activeReactionTimers = {};
let lastLobbyCodeRendered = '';
let lastLobbyPlayerCount = -1;
let summaryRoundFilter = 'all';
let markedSuspects = new Set();
let audioRegistry = {};
let audioSeq = 0;

// 5-Minute Hint Timer client state
let hintTimerInterval = null;
let hintTimerDeadlineMs = null; // epoch ms when 7s hint timer reaches 0
let hintTimerDurationSec = HINT_TIMER_DURATION;
let hintTimerExpiredFired = false;
let lastTickWarnSecond = -1;

// Last-Stand countdown interval
let lastGuessInterval = null;

// Voice recorder
let mediaRecorder = null;
let recordedChunks = [];
let recordedAudioDataUrl = null;
let recordTimer = null;
let recordSeconds = 0;

// Local mode state
let local = null;
let localResult = null;
let localNames = ['', '', '', ''];
let localWordCache = null;
let localSelectedLevel = 1;
let localUsedWords = [];

// Sound Effects (Web Audio API — Zero External Files)
let sfxEnabled = true;
let audioCtx = null;

const $ = id => document.getElementById(id);
const show = id => {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  $(id).classList.add('active');
};
const esc = s => String(s ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

function getRank(score) {
  const tiers = [[0,'Rookie'],[200,'Operative'],[500,'Investigator'],[900,'Special Agent'],[1500,'Master Spy'],[2500,'Phantom Legend']];
  let r = 'Rookie';
  for (const [t, name] of tiers) if (score >= t) r = name;
  return r;
}

function registerAudio(dataUrl) {
  const id = 'a' + (++audioSeq);
  audioRegistry[id] = dataUrl;
  return id;
}
function playAudioById(id) {
  const url = audioRegistry[id];
  if (!url) return;
  const a = new Audio(url);
  a.play().catch(() => alert('Tap again to play audio'));
}

// ============================================================================
// SYNTH SOUND EFFECTS ENGINE
// ============================================================================
function playSfx(type) {
  if (!sfxEnabled) return;
  try {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    if (!audioCtx) audioCtx = new AC();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const now = audioCtx.currentTime;

    const tone = (freq, dur, wave = 'sine', vol = 0.08, delay = 0) => {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = wave;
      osc.frequency.setValueAtTime(freq, now + delay);
      gain.gain.setValueAtTime(vol, now + delay);
      gain.gain.exponentialRampToValueAtTime(0.001, now + delay + dur);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start(now + delay);
      osc.stop(now + delay + dur);
    };

    if (type === 'click') tone(640, 0.06, 'triangle', 0.05);
    else if (type === 'hint') { tone(520, 0.12, 'sine', 0.09, 0); tone(780, 0.18, 'triangle', 0.09, 0.1); tone(1040, 0.25, 'sine', 0.07, 0.22); }
    else if (type === 'imposter') { tone(160, 0.28, 'sawtooth', 0.08, 0); tone(120, 0.35, 'sawtooth', 0.07, 0.2); }
    else if (type === 'crew') { tone(440, 0.14, 'sine', 0.07, 0); tone(660, 0.2, 'sine', 0.07, 0.12); }
    else if (type === 'tick') tone(880, 0.06, 'square', 0.04);
    else if (type === 'alarm') {
      for (let i = 0; i < 3; i++) tone(920, 0.18, 'sawtooth', 0.1, i * 0.24);
    } else if (type === 'win') {
      tone(523, 0.15, 'triangle', 0.08, 0);
      tone(659, 0.15, 'triangle', 0.08, 0.13);
      tone(784, 0.28, 'triangle', 0.09, 0.26);
    } else if (type === 'lose') {
      tone(300, 0.22, 'sawtooth', 0.07, 0);
      tone(220, 0.32, 'sawtooth', 0.07, 0.2);
    }
  } catch (e) {}
}

function toggleSfx() {
  sfxEnabled = !sfxEnabled;
  $('sfxBtn').textContent = sfxEnabled ? '🔊' : '🔇';
  if (sfxEnabled) playSfx('click');
}

// ============================================================================
// 7-SECOND HINT COUNTDOWN TIMER HUD ENGINE
// ============================================================================
let hintHudHideTimeout = null;

function formatMMSS(sec) {
  const s = Math.max(0, Math.floor(sec));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return String(m).padStart(2, '0') + ':' + String(r).padStart(2, '0');
}

function startHintTimerHud(remainingSec, durationSec = HINT_TIMER_DURATION) {
  if (hintHudHideTimeout) { clearTimeout(hintHudHideTimeout); hintHudHideTimeout = null; }
  hintTimerDurationSec = durationSec || HINT_TIMER_DURATION;
  hintTimerDeadlineMs = Date.now() + Math.max(0, remainingSec) * 1000;
  hintTimerExpiredFired = remainingSec <= 0;
  lastTickWarnSecond = -1;
  $('hintTimerHud').classList.add('active');
  updateHintTimerTick();
  if (!hintTimerInterval) {
    hintTimerInterval = setInterval(updateHintTimerTick, 100);
  }
}

function stopHintTimerHud() {
  if (hintTimerInterval) { clearInterval(hintTimerInterval); hintTimerInterval = null; }
  if (hintHudHideTimeout) { clearTimeout(hintHudHideTimeout); hintHudHideTimeout = null; }
  hintTimerDeadlineMs = null;
  hintTimerExpiredFired = false;
  lastTickWarnSecond = -1;
  const hud = $('hintTimerHud');
  hud.classList.remove('active', 'warn', 'critical');
  $('hintTimerClock').textContent = '00:07';
  $('hintTimerFill').style.width = '100%';
  $('hintTimerLabel').textContent = '⏱️ HINT VISIBLE — MEMORIZE FAST!';
}

function updateHintTimerTick() {
  if (!hintTimerDeadlineMs) return;
  const remMs = Math.max(0, hintTimerDeadlineMs - Date.now());
  const remSec = Math.ceil(remMs / 1000);
  const pct = Math.max(0, Math.min(100, (remMs / (hintTimerDurationSec * 1000)) * 100));

  const hud = $('hintTimerHud');
  $('hintTimerClock').textContent = formatMMSS(remSec);
  $('hintTimerFill').style.width = pct.toFixed(1) + '%';

  hud.classList.remove('warn', 'critical');
  if (remSec <= 0) {
    hud.classList.add('critical');
    $('hintTimerLabel').textContent = '🔒 7s UP — HINT LOCKED!';
    if (!hintTimerExpiredFired) {
      hintTimerExpiredFired = true;
      playSfx('alarm');
      onHintTimerExpired();
    }
  } else if (remSec <= 2) {
    hud.classList.add('critical');
    $('hintTimerLabel').textContent = `⚠️ HINT HIDING IN ${remSec}s!`;
    if (remSec !== lastTickWarnSecond) {
      lastTickWarnSecond = remSec;
      playSfx('tick');
    }
  } else if (remSec <= 4) {
    hud.classList.add('warn');
    $('hintTimerLabel').textContent = `⏱️ MEMORIZE FAST — ${remSec}s LEFT`;
    if (remSec === 3 && remSec !== lastTickWarnSecond) {
      lastTickWarnSecond = remSec;
      playSfx('tick');
    }
  } else {
    $('hintTimerLabel').textContent = `⏱️ HINT VISIBLE — ${remSec}s LEFT`;
  }

  if ($('peekTimerNote') && $('peekHintUnlocked').style.display !== 'none') {
    $('peekTimerNote').textContent = remSec > 0
      ? `⏱️ Auto-hiding in ${remSec}s...`
      : '🔒 7s Time Up!';
  }
  if ($('revealHintTimerNote') && $('revealHintUnlocked').style.display !== 'none') {
    $('revealHintTimerNote').textContent = remSec > 0
      ? `⏱️ Auto-hiding in ${remSec}s...`
      : '🔒 7s Time Up!';
  }
}

function setHintVaultState(prefix, status, hintText = '') {
  const vault = $(prefix + 'HintVault');
  const locked = $(prefix + 'HintLocked');
  const unlocked = $(prefix + 'HintUnlocked');
  const expired = $(prefix + 'HintExpired');
  vault.className = 'hint-vault' + (status === 'unlocked' ? ' unlocked' : '');
  locked.style.display = status === 'locked' ? 'block' : 'none';
  unlocked.style.display = status === 'unlocked' ? 'block' : 'none';
  expired.style.display = status === 'expired' ? 'block' : 'none';
  if (status === 'unlocked') {
    $(prefix + 'HintText').textContent = hintText;
  } else {
    $(prefix + 'HintText').textContent = '';
  }
}

async function onHintTimerExpired() {
  if (hintTimerInterval) { clearInterval(hintTimerInterval); hintTimerInterval = null; }
  // Auto-hide the hint on both Reveal screen & Peek Modal!
  if ($('revealHintUnlocked').style.display !== 'none') {
    setHintVaultState('reveal', 'expired');
  }
  if ($('peekHintUnlocked').style.display !== 'none') {
    setHintVaultState('peek', 'expired');
  }
  hintHudHideTimeout = setTimeout(() => {
    $('hintTimerHud').classList.remove('active', 'warn', 'critical');
  }, 1800);

  if (local) {
    const p = $('screen-reveal').classList.contains('active')
      ? local.players[local.passIndex]
      : local.players[local.clueIndex];
    if (p) p.hintExpired = true;
    return;
  }
  if (session) {
    try { applyState(await api('state', session)); } catch (e) {}
  }
}

// ============================================================================
// API & SESSION HELPERS
// ============================================================================
async function api(path, body) {
  const res = await fetch('/api/' + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {})
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
  return data;
}
async function apiGet(path) {
  const res = await fetch('/api/' + path);
  if (!res.ok) throw new Error('HTTP ' + res.status);
  return res.json();
}
function saveSession(s) {
  session = s;
  if (s) localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  else localStorage.removeItem(STORAGE_KEY);
}

function setLevelBadge(lvl) {
  const cfg = LEVELS_DATA[lvl] || LEVELS_DATA[1];
  const b = $('levelBadge');
  b.style.display = 'inline-block';
  b.textContent = `LVL ${cfg.level} • ${cfg.name.toUpperCase()}`;
  b.style.borderColor = cfg.color;
  b.style.color = cfg.color;
}

function renderLevelGrid(containerId, selectedLvl, onSelect, interactive = true) {
  const el = $(containerId);
  el.innerHTML = '';
  for (let lv = 1; lv <= 5; lv++) {
    const cfg = LEVELS_DATA[lv];
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'level-chip' + (lv === selectedLvl ? ' active' : '');
    btn.style.setProperty('--lv-color', cfg.color);
    btn.disabled = !interactive;
    btn.innerHTML = `<span class="lv-num">L${lv}</span><span class="lv-name">${cfg.name}</span>`;
    if (interactive) {
      btn.onclick = () => { playSfx('click'); onSelect(lv); };
    }
    el.appendChild(btn);
  }
}

function populateCategorySelect(selectId, selectedVal = 'All') {
  const sel = $(selectId);
  const cur = selectedVal || sel.value || 'All';
  sel.innerHTML = '<option value="All">All Categories</option>';
  CATEGORIES_DATA.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    sel.appendChild(opt);
  });
  sel.value = cur;
}

// ============================================================================
// MODE & TUTORIAL
// ============================================================================
async function pickMode(mode) {
  playSfx('click');
  await ensureWordCache();
  if (mode === 'online') {
    local = null;
    $('modeBadge').style.display = 'none';
    $('levelBadge').style.display = 'none';
    $('rolePeekBtn').style.display = 'none';
    stopHintTimerHud();
    show('screen-home');
  } else {
    stopPolling();
    $('modeBadge').style.display = 'inline-block';
    $('modeBadge').textContent = 'LOCAL';
    $('modeBadge').className = 'badge local';
    $('rolePeekBtn').style.display = 'none';
    stopHintTimerHud();
    initLocalSetup();
    show('screen-local-setup');
  }
}

function backToMode() {
  stopPolling();
  stopHintTimerHud();
  if (lastGuessInterval) { clearInterval(lastGuessInterval); lastGuessInterval = null; }
  local = null;
  $('chatFab').style.display = 'none';
  $('menuFab').style.display = 'none';
  $('rolePeekBtn').style.display = 'none';
  $('reactionBar').classList.remove('active');
  $('menuPanel').classList.remove('open');
  $('chatPanel').classList.remove('open');
  $('rolePeekModal').classList.remove('open');
  $('modeBadge').style.display = 'none';
  $('levelBadge').style.display = 'none';
  $('resumeHint').style.display = session ? 'block' : 'none';
  show('screen-mode');
}

function toggleTutorial() {
  playSfx('click');
  $('tutorialModal').classList.toggle('open');
}

// ============================================================================
// LIVE REACTIONS
// ============================================================================
async function sendReaction(emoji) {
  if (!session || local) return;
  spawnFloatingEmoji(emoji);
  try { await api('react', { ...session, emoji }); } catch (e) {}
}
function spawnFloatingEmoji(emoji) {
  const el = document.createElement('div');
  el.className = 'floating-reaction';
  el.textContent = emoji;
  el.style.left = (20 + Math.random() * 60) + '%';
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2000);
}
function checkReactions(s) {
  if (!s.reactions || s.reactions.length === 0) return;
  const now = Date.now() / 1000;
  s.reactions.forEach(r => {
    const key = r.ts + '_' + r.name;
    if (!activeReactionTimers[key] && (now - r.ts < 2.5)) {
      activeReactionTimers[key] = true;
      spawnFloatingEmoji(r.emoji);
      setTimeout(() => { delete activeReactionTimers[key]; }, 2500);
    }
  });
}

// ============================================================================
// ONLINE HOME
// ============================================================================
function showJoin() {
  playSfx('click');
  $('joinBox').style.display = 'block';
  const params = new URLSearchParams(location.search);
  const c = params.get('code');
  if (c) $('joinCode').value = c.toUpperCase();
  $('joinCode').focus();
}
function err(msg) { $('homeError').textContent = msg || ''; }

async function createGame() {
  err('');
  const name = $('playerName').value.trim();
  if (!name) return err('Enter Agent Name');
  const lang = $('lang').value;
  try {
    await ensureWordCache();
    const r = await api('create', { name, lang });
    saveSession({ code: r.code, token: r.token, name });
    playSfx('click');
    applyState(r.state);
  } catch (e) { err(e.message); }
}

async function joinGame() {
  err('');
  const name = $('playerName').value.trim();
  const code = $('joinCode').value.trim().toUpperCase();
  if (!name) return err('Enter Agent Name');
  if (code.length !== 6) return err('Invalid Lobby Code (6 chars)');
  try {
    await ensureWordCache();
    const r = await api('join', { name, code });
    saveSession({ code: r.code, token: r.token, name });
    playSfx('click');
    applyState(r.state);
  } catch (e) {
    const m = { game_not_found: 'Lobby not found', game_in_progress: 'Lobby already started',
                game_full: 'Lobby full (10 max)', name_taken: 'Name taken in this lobby' };
    err(m[e.message] || e.message);
  }
}

async function resumeSession() {
  if (!session) return;
  try {
    await ensureWordCache();
    applyState(await api('state', session));
  } catch (e) {
    saveSession(null); $('resumeHint').style.display = 'none'; alert('Lobby expired.');
  }
}

// ============================================================================
// ONLINE POLLING & STATE APPLICATION
// ============================================================================
function startPolling() {
  stopPolling();
  pollTimer = setInterval(async () => {
    if (!session) return;
    try { applyState(await api('state', session)); }
    catch (e) {
      if (e.message === 'game_not_found' || e.message === 'not_in_game') {
        saveSession(null); stopPolling(); backToMode();
      }
    }
  }, 1500);
}
function stopPolling() { if (pollTimer) { clearInterval(pollTimer); pollTimer = null; } }

function syncOnlineHintTimer(s) {
  const ht = s.hint_timer;
  if (ht && ht.active && !ht.expired && s.phase !== 'lobby' && s.phase !== 'result') {
    const targetDeadline = Date.now() + ht.remaining * 1000;
    if (!hintTimerDeadlineMs || Math.abs(hintTimerDeadlineMs - targetDeadline) > 1500) {
      startHintTimerHud(ht.remaining, ht.duration);
    }
  } else if (s.phase === 'lobby' || s.phase === 'result') {
    stopHintTimerHud();
  }
}

function applyState(s) {
  const prevPhase = current ? current.phase : null;
  current = s;
  $('modeBadge').style.display = 'none';
  setLevelBadge(s.level || 1);

  const p = s.phase;
  const activePhase = ['reveal', 'clue', 'summary', 'vote'].includes(p);
  $('rolePeekBtn').style.display = activePhase ? 'flex' : 'none';
  syncOnlineHintTimer(s);

  if (prevPhase && prevPhase !== p) {
    if (p === 'reveal') playSfx(s.you_are_imposter ? 'imposter' : 'crew');
    else if (p === 'result') {
      const iWon = (s.result_banner === 'crew' && !s.you_are_imposter) || (s.result_banner === 'imposter' && s.you_are_imposter);
      playSfx(iWon ? 'win' : 'lose');
    }
  }

  if (p === 'lobby')           renderLobby(s);
  else if (p === 'reveal')     renderRevealOnline(s);
  else if (p === 'clue')       renderClue(s);
  else if (p === 'summary')    renderSummary(s);
  else if (p === 'vote')       renderVoteOnline(s);
  else if (p === 'last_guess') renderLastGuessOnline(s);
  else if (p === 'result')     renderResult(s);

  updateChatBadge(s);
  checkReactions(s);
  if (chatOpen) renderChat(s);

  $('menuFab').style.display = 'flex';
  $('reactionBar').classList.add('active');
  $('menuRoomCode').textContent = s.code;
  $('menuYouName').textContent = s.you ? s.you.name : '—';
  $('menuYouRank').textContent = s.you ? `${s.you.rank} (${s.you.score} pts)` : 'Rookie';
  $('menuEndBtn').style.display = s.is_host ? 'block' : 'none';
  startPolling();
}

// ============================================================================
// ONLINE LOBBY
// ============================================================================
function copyInviteLink() {
  if (!current) return;
  const url = location.origin + '/join?code=' + current.code;
  navigator.clipboard?.writeText(url).then(() => {
    $('copyLinkBtn').textContent = '✅ Copied!';
    setTimeout(() => { $('copyLinkBtn').textContent = '📋 Copy Link'; }, 1800);
  }).catch(() => prompt('Copy this invite link:', url));
}

function renderLobby(s) {
  show('screen-lobby');
  $('lobbyCode').textContent = s.code;
  if (lastLobbyCodeRendered !== s.code) {
    lastLobbyCodeRendered = s.code;
    const joinUrl = location.origin + '/join?code=' + s.code;
    $('qrWrap').innerHTML = `<img alt="QR" src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&color=0f172a&bgcolor=ffffff&data=${encodeURIComponent(joinUrl)}">`;
    populateCategorySelect('onlineCategory', s.category || 'All');
  }

  const list = $('lobbyPlayers');
  list.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'player-row' + (p.ready ? ' ready' : '');
    const mine = p.name === s.you.name;
    const kick = s.is_host && !mine
      ? ` <button class="rec-clear" style="padding:3px 9px;font-size:0.75rem;border-color:var(--neon-red);color:var(--neon-red);" onclick="kickPlayer('${esc(p.name)}')">✕</button>` : '';
    const ptsTag = p.score > 0 ? `<span class="rank-tag">${p.score}pt</span>` : '';
    d.innerHTML = `<span>${esc(p.name)}${mine ? ' (YOU)' : ''}${p.name === s.host_name ? ' 👑' : ''}${ptsTag}</span>
                   <span class="tag">${p.ready ? '✅ READY' : '⏳ WAIT'}${kick}</span>`;
    list.appendChild(d);
  });

  const n = s.players.length;
  $('lobbyProgress').textContent = `AGENTS: ${n} / 10 — MIN 3`;
  $('lobbyReadyBtn').textContent = s.you.ready ? 'Stand Down' : 'Ready Up';
  $('lobbyReadyBtn').className = s.you.ready ? 'secondary' : '';

  const lvl = s.level || 1;
  const lvlCfg = LEVELS_DATA[lvl] || LEVELS_DATA[1];
  renderLevelGrid('onlineLevelGrid', lvl, (newLv) => syncHostConfig({ level: newLv }), s.is_host);
  $('onlineLevelDesc').style.borderLeftColor = lvlCfg.color;
  $('onlineLevelDesc').innerHTML =
    `<strong>LVL ${lvl} — ${lvlCfg.name.toUpperCase()} (${lvlCfg.tag})</strong><br>` +
    `${s.lang === 'hi' ? lvlCfg.desc_hi : lvlCfg.desc}<br>` +
    `<span style="color:var(--neon-amber);">⏱️ 7s Hint Timer when Hint is viewed • Crew +${lvlCfg.crew_pts} / Imp +${lvlCfg.imposter_pts} pts</span>`;

  if (s.is_host) {
    $('hostExtraControls').style.display = 'block';
    const maxK = Math.max(1, Math.floor((n - 1) / 2));
    if (lastLobbyPlayerCount !== n) {
      lastLobbyPlayerCount = n;
      const sel = $('numImposters');
      sel.innerHTML = '';
      for (let k = 1; k <= Math.min(3, maxK); k++) {
        const opt = document.createElement('option');
        opt.value = k; opt.textContent = k + ' Imposter' + (k > 1 ? 's' : '');
        sel.appendChild(opt);
      }
    }
    $('numImposters').value = String(Math.min(s.imposter_count, Math.min(3, maxK)));
    $('onlineCategory').value = s.category || 'All';
    $('onlineLastGuess').checked = !!s.last_guess_enabled;
    $('imposterNote').textContent = `Max ${maxK} imposter${maxK > 1 ? 's' : ''} with ${n} agents.`;

    $('lobbyStartBtn').style.display = 'block';
    const allReady = s.players.every(p => p.ready);
    $('lobbyStartBtn').disabled = !(n >= 3 && allReady);
    $('lobbyStartBtn').textContent = n < 3
      ? `Need ${3 - n} more agents`
      : (allReady ? `▶ START LEVEL ${lvl}` : 'Waiting for all agents to Ready Up');
  } else {
    $('hostExtraControls').style.display = 'none';
    $('lobbyStartBtn').style.display = 'none';
  }
  $('chatFab').style.display = 'flex';
}

async function syncHostConfig(overrides = {}) {
  if (!session || !current || !current.is_host) return;
  const body = {
    ...session,
    num_imposters: parseInt($('numImposters').value, 10) || 1,
    category: $('onlineCategory').value || 'All',
    last_guess_enabled: $('onlineLastGuess').checked,
    ...overrides,
  };
  try { applyState(await api('config', body)); } catch (e) {}
}

async function toggleReady() {
  if (!session) return;
  playSfx('click');
  try { applyState(await api('ready', { ...session, ready: !current.you.ready })); }
  catch (e) { $('lobbyError').textContent = e.message; }
}

async function startGame() {
  if (!session) return;
  $('lobbyError').textContent = '';
  const body = {
    ...session,
    level: current.level || 1,
    num_imposters: parseInt($('numImposters').value, 10) || 1,
    category: $('onlineCategory').value || 'All',
    last_guess_enabled: $('onlineLastGuess').checked,
  };
  if ($('onlineCustomToggle').checked) {
    body.custom_word = $('onlineCustomWord').value.trim();
    body.custom_hint = $('onlineCustomHint').value.trim();
  }
  try {
    markedSuspects.clear();
    applyState(await api('start', body));
  } catch (e) { $('lobbyError').textContent = e.message; }
}

async function kickPlayer(name) {
  if (!session) return;
  if (!confirm(`Remove ${name}?`)) return;
  try { applyState(await api('kick', { ...session, target: name })); }
  catch (e) { alert(e.message); }
}

// ============================================================================
// HINT UNLOCK (ONLINE & LOCAL) + ROLE PEEK MODAL
// ============================================================================
async function triggerSeeHint(fromModal = false) {
  playSfx('hint');
  if (local) {
    localTriggerSeeHint(fromModal);
    return;
  }
  if (!session) return;
  try {
    const s = await api('see_hint', session);
    applyState(s);
    if (fromModal) renderRolePeekModal();
  } catch (e) { alert(e.message); }
}

function openRolePeek() {
  playSfx('click');
  renderRolePeekModal();
  $('rolePeekModal').classList.add('open');
}
function closeRolePeek() {
  $('rolePeekModal').classList.remove('open');
}

function renderRolePeekModal() {
  if (local) {
    const p = local.phase === 'clue' ? local.players[local.clueIndex] : null;
    if (!p) return;
    const isImp = p.isImposter;
    $('peekCard').className = 'role-card ' + (isImp ? 'imposter' : 'crew');
    $('peekLabel').textContent = isImp ? `${p.name} — IMPOSTER` : `${p.name} — CREW SECRET WORD`;
    $('peekWord').textContent = isImp ? '🤫 IMPOSTER' : (local.word || '—');
    const st = getLocalPlayerHintStatus(p);
    setHintVaultState('peek', st.status, isImp ? local.imposterHint : local.crewHint);
    if (st.status === 'unlocked') startHintTimerHud(st.remaining, HINT_TIMER_DURATION);
    return;
  }
  if (!current) return;
  const isImp = !!current.you_are_imposter;
  $('peekCard').className = 'role-card ' + (isImp ? 'imposter' : 'crew');
  $('peekLabel').textContent = isImp ? 'YOU ARE THE IMPOSTER' : 'YOUR SECRET WORD';
  $('peekWord').textContent = isImp ? '🤫 IMPOSTER' : (current.your_word || '—');
  const ht = current.hint_timer || {};
  if (current.you && current.you.hint_expired) {
    setHintVaultState('peek', 'expired');
  } else if (current.you && current.you.hint_viewed && ht.active) {
    setHintVaultState('peek', 'unlocked', current.your_hint || '—');
  } else {
    setHintVaultState('peek', 'locked');
  }
}

// ============================================================================
// ONLINE GAME SCREENS
// ============================================================================
function renderRevealOnline(s) {
  show('screen-reveal');
  const card = $('revealCard');
  const isImp = !!s.you_are_imposter;
  card.className = 'role-card ' + (isImp ? 'imposter' : 'crew');
  $('revealLabel').textContent = isImp ? 'YOU ARE THE IMPOSTER' : 'YOUR SECRET WORD';
  $('revealWord').textContent = isImp ? '🤫 IMPOSTER' : (s.your_word || '—');

  const ht = s.hint_timer || {};
  if (s.you && s.you.hint_expired) {
    setHintVaultState('reveal', 'expired');
  } else if (s.you && s.you.hint_viewed && ht.active) {
    setHintVaultState('reveal', 'unlocked', s.your_hint || '');
  } else {
    setHintVaultState('reveal', 'locked');
  }

  $('revealRound').textContent = `LEVEL ${s.level} (${s.level_info.name.toUpperCase()}) • ${s.imposter_count} IMPOSTER${s.imposter_count > 1 ? 'S' : ''}`;
  $('revealNextBtn').style.display = s.is_host ? 'block' : 'none';
  $('revealLocalBtn').style.display = 'none';
  $('revealProgress').textContent = s.is_host ? 'Tap Proceed when agents have checked roles.' : 'Waiting for host to start Round 1...';
  $('chatFab').style.display = 'flex';
}

function renderClue(s) {
  show('screen-clue');
  $('clueRoundHeader').textContent = `LEVEL ${s.level} • ROUND ${s.round} OF ${s.max_rounds} — CLUES`;
  $('cluePlayerName').textContent = s.you ? s.you.name : '—';
  $('cluePlayerName').className = 'badge';
  $('clueSeeHintBtn').style.display = 'inline-block';

  const eliminated = !!(s.you && s.you.eliminated);
  const submitted = !!(s.you && (s.you.clue || s.you.clue_audio));

  if (!submitted && !eliminated && $('clueInput').disabled) {
    $('clueInput').value = '';
  }

  $('clueInput').disabled = submitted || eliminated;
  $('clueSubmitBtn').disabled = submitted || eliminated;
  $('clueSubmitBtn').textContent = eliminated ? 'ELIMINATED' : (submitted ? 'Transmitted ✅' : 'Send Text');
  if (submitted && s.you.clue) $('clueInput').value = s.you.clue;

  $('voiceSubmitBtn').style.display = recordedAudioDataUrl && !submitted && !eliminated ? 'block' : 'none';
  $('voiceSubmitBtn').disabled = submitted || eliminated;

  const wl = $('clueWaitingList');
  wl.innerHTML = '';
  const activePlayers = s.players.filter(p => !p.eliminated);
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'player-row' + (p.eliminated ? ' eliminated' : '');
    const tag = p.eliminated ? '💀 OUT' : (p.has_clue ? '✅ SENT' : '✏️ INPUTTING...');
    d.innerHTML = `<span>${esc(p.name)}</span><span class="tag">${tag}</span>`;
    wl.appendChild(d);
  });
  const done = activePlayers.filter(p => p.has_clue).length;
  $('clueProgress').textContent = `STATUS: ${done} / ${activePlayers.length} TRANSMITTED`;
  $('chatFab').style.display = (submitted || eliminated) ? 'flex' : 'none';
  if (chatOpen && (submitted || eliminated)) renderChat(s);
}

function toggleSuspect(name) {
  playSfx('click');
  if (markedSuspects.has(name)) markedSuspects.delete(name);
  else markedSuspects.add(name);
  if (local) localRenderSummary();
  else if (current) renderSummary(current);
}

function renderClueHistoryInto(container, history, myName = null, allowSuspect = false) {
  container.innerHTML = '';
  const rounds = history || [];
  const filtered = summaryRoundFilter === 'all' ? rounds : rounds.filter(r => String(r.round) === String(summaryRoundFilter));
  filtered.forEach(rObj => {
    const hdr = document.createElement('div');
    hdr.className = 'round-header';
    hdr.style.marginTop = '8px';
    hdr.textContent = `— ROUND ${rObj.round} —`;
    container.appendChild(hdr);
    (rObj.clues || []).forEach(c => {
      const d = document.createElement('div');
      const isSus = markedSuspects.has(c.name);
      d.className = 'clue-item' + (myName && c.name === myName ? ' mine' : '') + (isSus ? ' suspect' : '');
      let leftHtml = '';
      if (c.clue) {
        leftHtml = `<div><span class="name">${esc(c.name)}:</span> ${esc(c.clue)}</div>`;
      } else if (c.clue_audio) {
        const aid = registerAudio(c.clue_audio);
        leftHtml = `<div><span class="name">${esc(c.name)}:</span> 🎙️ VOICE <button class="play-btn" onclick="playAudioById('${aid}')">▶ Play</button></div>`;
      } else {
        leftHtml = `<div><span class="name">${esc(c.name)}:</span> —</div>`;
      }
      const rightHtml = allowSuspect
        ? `<button class="sus-btn ${isSus ? 'marked' : ''}" onclick="toggleSuspect('${esc(c.name)}')" title="Flag Suspect">${isSus ? '🚩 SUS' : '🔍'}</button>`
        : '';
      d.innerHTML = leftHtml + rightHtml;
      container.appendChild(d);
    });
  });
}

function renderRoundTabs(container, history, onChange) {
  container.innerHTML = '';
  if (!history || history.length <= 1) return;
  const tabs = [{ id: 'all', label: 'All Rounds' }, ...history.map(h => ({ id: String(h.round), label: `Round ${h.round}` }))];
  tabs.forEach(t => {
    const b = document.createElement('button');
    b.className = 'round-tab' + (String(summaryRoundFilter) === t.id ? ' active' : '');
    b.textContent = t.label;
    b.onclick = () => { summaryRoundFilter = t.id; onChange(); };
    container.appendChild(b);
  });
}

function renderSummary(s) {
  show('screen-summary');
  $('summaryHeader').textContent = `ROUND ${s.round} OF ${s.max_rounds} COMPLETE`;
  const history = s.clue_history && s.clue_history.length ? s.clue_history : [{ round: s.round, clues: s.players }];
  renderRoundTabs($('summaryTabs'), history, () => renderSummary(s));
  renderClueHistoryInto($('summaryList'), history, s.you ? s.you.name : null, true);
  const btn = $('summaryNextBtn');
  if (s.is_host) {
    btn.style.display = 'block';
    btn.textContent = s.round < s.max_rounds ? `Start Round ${s.round + 1} →` : 'Proceed to Voting →';
  } else btn.style.display = 'none';
  $('summaryProgress').textContent = s.is_host ? 'Discuss in Secure Comms, then advance.' : 'Waiting for host...';
  $('chatFab').style.display = 'flex';
}

function renderVoteOnline(s) {
  show('screen-vote');
  $('voteVoterName').textContent = s.you ? s.you.name : '—';
  const notice = $('voteElimNotice');
  if (s.elimination_notice) {
    notice.style.display = 'block';
    notice.textContent = s.elimination_notice;
  } else notice.style.display = 'none';

  const eliminated = !!(s.you && s.you.eliminated);
  const voted = !!(s.you && s.you.has_voted);
  if (voted || eliminated) selectedVote = null;
  $('voteSubmitBtn').disabled = !selectedVote || voted || eliminated;
  $('voteSubmitBtn').textContent = eliminated ? 'ELIMINATED (SPECTATING)' : (voted ? 'VOTE LOCKED ✅' : 'LOCK VOTE');

  const list = $('voteList');
  list.innerHTML = '';
  s.players.filter(p => !p.eliminated).forEach(p => {
    const btn = document.createElement('button');
    const isSus = markedSuspects.has(p.name);
    btn.className = 'vote-btn' + (p.name === selectedVote ? ' selected' : '') + (voted || eliminated ? ' done' : '');
    btn.innerHTML = `<span>${esc(p.name)}${p.name === s.you.name ? ' (YOU)' : ''}</span><span>${isSus ? '🚩' : ''}</span>`;
    if (p.name === s.you.name || eliminated) btn.disabled = true;
    else if (!voted) {
      btn.onclick = () => {
        playSfx('click');
        selectedVote = p.name;
        document.querySelectorAll('.vote-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        $('voteSubmitBtn').disabled = false;
      };
    }
    list.appendChild(btn);
  });

  const wl = $('voteWaitingList');
  wl.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'player-row' + (p.eliminated ? ' eliminated' : '');
    const tag = p.eliminated ? '💀 CAUGHT' : (p.has_voted ? '✅ VOTED' : '⏳ WAITING');
    d.innerHTML = `<span>${esc(p.name)}</span><span class="tag">${tag}</span>`;
    wl.appendChild(d);
  });
  $('voteChatHint').style.display = 'block';
  $('chatFab').style.display = 'flex';
}

function renderLastGuessOnline(s) {
  show('screen-last-guess');
  $('lastGuessClock').textContent = (s.last_guess_remaining ?? 0) + 's';
  $('lastGuessInfo').textContent = `${s.last_guess_imposter} was caught! One last shot to guess the Secret Word and steal the win!`;
  if (s.you_can_guess) {
    $('lastGuessInputWrap').style.display = 'block';
    $('lastGuessWaitMsg').style.display = 'none';
  } else {
    $('lastGuessInputWrap').style.display = 'none';
    $('lastGuessWaitMsg').style.display = 'block';
  }
  $('chatFab').style.display = 'flex';
}

async function submitImposterGuess() {
  if (local) return localSubmitImposterGuess();
  if (!session) return;
  const guess = $('lastGuessInput').value.trim();
  try { applyState(await api('imposter_guess', { ...session, guess })); }
  catch (e) { alert(e.message); }
}

function renderResult(s) {
  show('screen-result');
  const imposterNames = s.imposter_names || [];
  const banner = $('resultBanner');
  let title = '', cls = '';
  if (s.result_banner === 'crew') { title = '🎉 CREW WINS!'; cls = 'crew'; }
  else if (s.result_banner === 'imposter') { title = '😈 IMPOSTERS WIN!'; cls = 'imposter'; }
  else { title = '🤝 TIE'; cls = 'tie'; }
  banner.textContent = title;
  banner.className = 'banner ' + cls;

  let detail = '';
  if (s.result_reason) detail += `${esc(s.result_reason)}<br>`;
  else if (s.vote_tie) detail += `VOTE TIED.<br>`;
  else if (s.voted_out_name) detail += `VOTED OUT: <strong>${esc(s.voted_out_name)}</strong><br>`;
  if (s.imposter_guess_text) detail += `FINAL GUESS: <strong>${esc(s.imposter_guess_text)}</strong><br>`;
  detail += `LEVEL ${s.level} (${esc(s.level_info.name)}) • CATEGORY: <strong>${esc(s.word_category || s.category)}</strong><br>`;
  detail += `SECRET WORD: <strong>${esc(s.secret_word)}</strong>`;
  $('resultDetail').innerHTML = detail;

  const tally = s.vote_counts || {};
  const entries = Object.entries(tally).sort((a, b) => b[1] - a[1]);
  const topCount = entries.length ? entries[0][1] : 0;
  const box = $('voteSummary');
  box.innerHTML = '';
  entries.forEach(([name, count]) => {
    const row = document.createElement('div');
    row.className = 'vote-row' + (count === topCount && count > 0 && !s.vote_tie ? ' top' : '');
    row.innerHTML = `<span>${esc(name)}${imposterNames.includes(name) ? ' 🤫' : ''}</span>
                     <span class="count">${count} VOTE${count === 1 ? '' : 'S'}</span>`;
    box.appendChild(row);
  });

  $('imposterBox').innerHTML =
    `<div class="round-header">IMPOSTER${imposterNames.length > 1 ? 'S' : ''}</div>` +
    imposterNames.map(n => `<span class="imposter-pill">🕵️ ${esc(n)}</span>`).join(' ');

  const sortedPlayers = [...s.players].sort((a, b) => (b.score || 0) - (a.score || 0));
  const sb = $('scoreboard');
  sb.innerHTML = '<h4>LEADERBOARD &amp; RANKS</h4>' +
    sortedPlayers.map((p, idx) =>
      `<div class="score-row">
         <span>${idx === 0 && p.score > 0 ? '👑 ' : ''}${esc(p.name)}<span class="rank-tag">${esc(p.rank)}</span>${p.streak >= 2 ? `<span class="streak-tag">🔥${p.streak}x</span>` : ''}</span>
         <span class="pts">${p.score} PTS</span>
       </div>`
    ).join('');

  summaryRoundFilter = 'all';
  const rc = $('resultClues');
  renderClueHistoryInto(rc, s.clue_history || [], s.you ? s.you.name : null, false);

  const canLevelUp = s.is_host && (s.level || 1) < 5;
  $('nextLevelBtn').style.display = canLevelUp ? 'block' : 'none';
  if (canLevelUp) {
    const nxt = LEVELS_DATA[(s.level || 1) + 1];
    $('nextLevelBtn').textContent = `🚀 Advance to Level ${nxt.level} (${nxt.name}) →`;
  }
  $('playAgainBtn').style.display = s.is_host ? 'block' : 'none';
  $('resultProgress').textContent = s.is_host ? '' : 'WAITING FOR HOST...';
  $('chatFab').style.display = 'flex';
}

async function nextLevelPlay() {
  playSfx('click');
  if (local) {
    const nextLv = Math.min(5, (local.level || 1) + 1);
    localSelectedLevel = nextLv;
    startLocalGameWithScores(
      local.players.map(p => ({ score: p.score, wins: p.wins, streak: p.streak })),
      nextLv
    );
    return;
  }
  if (!session) return;
  try { applyState(await api('next_level', session)); }
  catch (e) { alert(e.message); }
}

async function playAgain() {
  playSfx('click');
  if (local) {
    startLocalGameWithScores(
      local.players.map(p => ({ score: p.score, wins: p.wins, streak: p.streak })),
      local.level || 1
    );
    return;
  }
  if (!session) return;
  try { applyState(await api('reset', session)); }
  catch (e) { alert(e.message); }
}

async function hostAdvance() {
  playSfx('click');
  if (local) return localAdvance();
  if (!session) return;
  try { applyState(await api('advance', session)); }
  catch (e) { alert(e.message); }
}

async function submitClue() {
  if (local) return localSubmitClue('text');
  if (!session) return;
  $('clueError').textContent = '';
  const text = $('clueInput').value.trim();
  if (!text) { $('clueError').textContent = 'ENTER A CLUE.'; return; }
  try {
    playSfx('click');
    applyState(await api('clue', { ...session, text }));
  } catch (e) {
    const m = { contains_word: '❌ CLUE CONTAINS SECRET WORD!' };
    $('clueError').textContent = m[e.message] || e.message;
  }
}

async function submitVoice() {
  if (local) return localSubmitClue('voice');
  if (!session || !recordedAudioDataUrl) return;
  $('clueError').textContent = '';
  try {
    playSfx('click');
    applyState(await api('audio', { ...session, audio: recordedAudioDataUrl }));
    clearRecording();
  } catch (e) {
    const m = { audio_too_large: 'AUDIO TOO LARGE.' };
    $('clueError').textContent = m[e.message] || e.message;
  }
}

async function submitVote() {
  if (local) return localSubmitVote();
  if (!session || !selectedVote) return;
  $('voteError').textContent = '';
  try {
    playSfx('click');
    const r = await api('vote', { ...session, target: selectedVote });
    selectedVote = null;
    applyState(r);
  } catch (e) { $('voteError').textContent = e.message; }
}
// ============================================================================
// LOCAL TERMINAL MODE (FULL 5 LEVELS + 7-SECOND HINT TIMER + LAST STAND)
// ============================================================================
function initLocalSetup() {
  $('localError').textContent = '';
  $('localNumPlayers').value = '4';
  $('localLang').value = 'en';
  $('localCustomToggle').checked = false;
  $('localCustomBox').style.display = 'none';
  $('localCustomWord').value = '';
  $('localCustomHint').value = '';
  populateCategorySelect('localCategory', 'All');
  selectLocalLevel(localSelectedLevel || 1);
  localNames = ['', '', '', ''];
  renderLocalNameInputs();
}

function selectLocalLevel(lv) {
  localSelectedLevel = lv;
  const cfg = LEVELS_DATA[lv] || LEVELS_DATA[1];
  renderLevelGrid('localLevelGrid', lv, selectLocalLevel, true);
  $('localLastGuess').checked = !!cfg.last_guess;
  updateLocalLevelDesc();
  setLevelBadge(lv);
}

function updateLocalLevelDesc() {
  const cfg = LEVELS_DATA[localSelectedLevel] || LEVELS_DATA[1];
  const lang = $('localLang').value;
  $('localLevelDesc').style.borderLeftColor = cfg.color;
  $('localLevelDesc').innerHTML =
    `<strong>LVL ${cfg.level} — ${cfg.name.toUpperCase()} (${cfg.tag})</strong><br>` +
    `${lang === 'hi' ? cfg.desc_hi : cfg.desc}<br>` +
    `<span style="color:var(--neon-amber);">⏱️ 7s Hint Timer when Hint is viewed • Crew +${cfg.crew_pts} / Imp +${cfg.imposter_pts} pts</span>`;
}

function renderLocalNameInputs() {
  const n = Math.max(3, Math.min(10, parseInt($('localNumPlayers').value, 10) || 4));
  while (localNames.length < n) localNames.push('');
  localNames = localNames.slice(0, n);
  const box = $('localNameInputs');
  box.innerHTML = '';
  for (let i = 0; i < n; i++) {
    const label = document.createElement('label');
    label.textContent = `Agent ${i + 1}`;
    const inp = document.createElement('input');
    inp.type = 'text'; inp.maxLength = 20;
    inp.value = localNames[i] || `Agent ${i + 1}`;
    inp.placeholder = 'ENTER NAME...';
    inp.oninput = () => { localNames[i] = inp.value; };
    localNames[i] = inp.value;
    box.appendChild(label);
    box.appendChild(inp);
  }
  const maxK = Math.max(1, Math.floor((n - 1) / 2));
  const sel = $('localNumImposters');
  const prev = parseInt(sel.value, 10) || 1;
  sel.innerHTML = '';
  for (let k = 1; k <= Math.min(3, maxK); k++) {
    const opt = document.createElement('option');
    opt.value = k; opt.textContent = k + ' Imposter' + (k > 1 ? 's' : '');
    sel.appendChild(opt);
  }
  sel.value = String(Math.min(prev, Math.min(3, maxK)));
  $('localImposterNote').textContent = `Max ${maxK} imposter${maxK > 1 ? 's' : ''} with ${n} agents.`;
}

$('localNumPlayers').addEventListener('input', renderLocalNameInputs);

async function ensureWordCache() {
  if (localWordCache) return localWordCache;
  try {
    const r = await apiGet('words');
    localWordCache = r.words;
    if (r.levels) {
      const normalized = {};
      Object.entries(r.levels).forEach(([k, v]) => { normalized[Number(k)] = v; });
      LEVELS_DATA = normalized;
    }
    if (r.categories) CATEGORIES_DATA = r.categories;
  } catch (e) {
    localWordCache = [
      { level: 1, category: 'Food', category_hi: 'खान-पान',
        en: { word: 'Pizza', imposter_hint: 'Round food cut into slices.', subtle_hint: 'Comes in a square box.' },
        hi: { word: 'पिज़्ज़ा', imposter_hint: 'गोल खाना जिसे टुकड़ों में काटते हैं।', subtle_hint: 'चौकोर डिब्बे में आता है।' } },
      { level: 2, category: 'Transport', category_hi: 'परिवहन',
        en: { word: 'Train', imposter_hint: 'Moves on tracks.', subtle_hint: 'Stops at platforms.' },
        hi: { word: 'ट्रेन', imposter_hint: 'पटरी पर चलती है।', subtle_hint: 'प्लेटफ़ॉर्म पर रुकती है।' } },
      { level: 3, category: 'Science', category_hi: 'विज्ञान',
        en: { word: 'Telescope', imposter_hint: 'Used to view stars.', subtle_hint: 'Brings night sky closer.' },
        hi: { word: 'दूरबीन', imposter_hint: 'तारे देखने के काम आती है।', subtle_hint: 'आसमान पास लाती है।' } },
    ];
  }
  return localWordCache;
}

function pickLocalWordEntry(bank, level, category) {
  let pool = bank.filter(w => w.level === level && (category === 'All' || w.category === category));
  if (!pool.length) pool = bank.filter(w => w.level === level);
  if (!pool.length) pool = bank;
  const fresh = pool.filter(w => !localUsedWords.includes(w.en.word));
  if (fresh.length) pool = fresh;
  const choice = pool[Math.floor(Math.random() * pool.length)];
  localUsedWords.push(choice.en.word);
  if (localUsedWords.length > 40) localUsedWords = localUsedWords.slice(-40);
  return choice;
}

function buildLocalHint(entry, lang, levelCfg) {
  const data = entry[lang];
  const cat = lang === 'hi' ? (entry.category_hi || entry.category) : entry.category;
  if (levelCfg.hint_style === 'full') return `[${cat}] ${data.imposter_hint}`;
  if (levelCfg.hint_style === 'subtle') return `[${cat}] ${data.subtle_hint || data.imposter_hint}`;
  if (levelCfg.hint_style === 'category') {
    return lang === 'hi' ? `केवल श्रेणी: ${cat} — ध्यान से सुराग सुनें!` : `Category Only: ${cat} — Read the room carefully!`;
  }
  const sub = data.subtle_hint || data.imposter_hint;
  return lang === 'hi' ? `गुप्त संकेत: ${sub}` : `Cryptic Intel: ${sub}`;
}

function buildLocalCrewHint(entry, lang) {
  const cat = lang === 'hi' ? (entry.category_hi || entry.category) : entry.category;
  return lang === 'hi'
    ? `श्रेणी: ${cat} • शब्द बोले बिना चतुराई से संकेत दें!`
    : `Category: ${cat} • Give a smart clue without being too obvious!`;
}

async function startLocalGame() {
  $('localError').textContent = '';
  const n = Math.max(3, Math.min(10, parseInt($('localNumPlayers').value, 10) || 4));
  const names = localNames.slice(0, n).map((s, i) => (s || '').trim() || `Agent ${i + 1}`);
  const lower = names.map(s => s.toLowerCase());
  if (new Set(lower).size !== lower.length) {
    $('localError').textContent = 'Agent names must be unique.';
    return;
  }
  const lang = $('localLang').value;
  const category = $('localCategory').value || 'All';
  const level = localSelectedLevel || 1;
  const lastGuessEnabled = $('localLastGuess').checked;
  const k = parseInt($('localNumImposters').value, 10) || 1;
  const maxK = Math.max(1, Math.floor((n - 1) / 2));
  const numImposters = Math.max(1, Math.min(k, maxK, 3));

  const customOn = $('localCustomToggle').checked;
  const customWord = customOn ? $('localCustomWord').value.trim() : '';
  const customHint = customOn ? $('localCustomHint').value.trim() : '';

  await launchLocalMatch({
    names, lang, category, level, numImposters, lastGuessEnabled,
    customWord, customHint,
    prevStats: names.map(() => ({ score: 0, wins: 0, streak: 0 })),
  });
}

async function startLocalGameWithScores(prevStats, level) {
  await launchLocalMatch({
    names: local.players.map(p => p.name),
    lang: local.lang,
    category: local.category || 'All',
    level: level || local.level || 1,
    numImposters: local.numImposters,
    lastGuessEnabled: (LEVELS_DATA[level || local.level || 1] || LEVELS_DATA[1]).last_guess,
    customWord: '',
    customHint: '',
    prevStats,
  });
}

async function launchLocalMatch(opts) {
  let bank;
  try { bank = await ensureWordCache(); }
  catch (e) { $('localError').textContent = 'Data link failed.'; return; }

  const levelCfg = LEVELS_DATA[opts.level] || LEVELS_DATA[1];
  let word, wordCategory, imposterHint, crewHint;
  if (opts.customWord) {
    word = opts.customWord;
    wordCategory = 'Custom';
    imposterHint = opts.customHint || 'No custom hint provided — blend in carefully!';
    crewHint = 'Custom Mission Word • Give smart clues without saying it!';
  } else {
    const entry = pickLocalWordEntry(bank, opts.level, opts.category);
    word = entry[opts.lang].word;
    wordCategory = opts.lang === 'hi' ? (entry.category_hi || entry.category) : entry.category;
    imposterHint = buildLocalHint(entry, opts.lang, levelCfg);
    crewHint = buildLocalCrewHint(entry, opts.lang);
  }

  const n = opts.names.length;
  const imposterIndices = new Set();
  while (imposterIndices.size < opts.numImposters) {
    imposterIndices.add(Math.floor(Math.random() * n));
  }

  stopHintTimerHud();
  if (lastGuessInterval) { clearInterval(lastGuessInterval); lastGuessInterval = null; }
  markedSuspects.clear();
  summaryRoundFilter = 'all';

  local = {
    lang: opts.lang,
    level: opts.level,
    levelCfg,
    category: opts.category,
    wordCategory,
    maxRounds: levelCfg.rounds,
    lastGuessEnabled: opts.lastGuessEnabled,
    word,
    imposterHint,
    crewHint,
    imposterIndices: [...imposterIndices].sort((a, b) => a - b),
    numImposters: opts.numImposters,
    players: opts.names.map((name, i) => ({
      name,
      isImposter: imposterIndices.has(i),
      clue: '', clueAudio: null, vote: null,
      score: (opts.prevStats[i] && opts.prevStats[i].score) || 0,
      wins: (opts.prevStats[i] && opts.prevStats[i].wins) || 0,
      streak: (opts.prevStats[i] && opts.prevStats[i].streak) || 0,
      eliminated: false,
      hintViewed: false,
      hintViewedAt: null,
      hintExpired: false,
    })),
    clueHistory: [],
    eliminationNotice: '',
    round: 1,
    phase: 'pass',
    passIndex: 0,
    clueIndex: 0,
    voteIndex: 0,
    selectedVote: null,
  };
  localResult = null;
  setLevelBadge(opts.level);
  $('rolePeekBtn').style.display = 'none';
  localRenderPass();
}

// ============================================================================
// LOCAL PASS, REVEAL & 7-SECOND HINT TIMER
// ============================================================================
function getLocalPlayerHintStatus(p) {
  if (!p || !p.hintViewed || !p.hintViewedAt) return { status: 'locked', remaining: HINT_TIMER_DURATION };
  const elapsed = (Date.now() - p.hintViewedAt) / 1000;
  const rem = Math.max(0, HINT_TIMER_DURATION - elapsed);
  if (rem <= 0 || p.hintExpired) {
    p.hintExpired = true;
    return { status: 'expired', remaining: 0 };
  }
  return { status: 'unlocked', remaining: rem };
}

function localRenderPass() {
  if (!local) return;
  stopHintTimerHud();
  const p = local.players[local.passIndex];
  $('passWho').textContent = p.name;
  $('passWhoInline').textContent = p.name;
  show('screen-pass');
}

function revealRole() {
  if (!local) return;
  stopHintTimerHud();
  const p = local.players[local.passIndex];
  const isImp = p.isImposter;
  playSfx(isImp ? 'imposter' : 'crew');
  const card = $('revealCard');
  card.className = 'role-card ' + (isImp ? 'imposter' : 'crew');
  $('revealLabel').textContent = isImp ? 'YOU ARE THE IMPOSTER' : 'YOUR SECRET WORD';
  $('revealWord').textContent = isImp ? '🤫 IMPOSTER' : (local.word || '—');

  const st = getLocalPlayerHintStatus(p);
  setHintVaultState('reveal', st.status, isImp ? local.imposterHint : local.crewHint);
  if (st.status === 'unlocked') startHintTimerHud(st.remaining, HINT_TIMER_DURATION);

  $('revealRound').textContent = `LEVEL ${local.level} (${local.levelCfg.name.toUpperCase()}) • ${local.numImposters} IMPOSTER${local.numImposters > 1 ? 'S' : ''}`;
  $('revealNextBtn').style.display = 'none';
  $('revealLocalBtn').style.display = 'block';
  $('revealProgress').textContent = `AGENT ${local.passIndex + 1} / ${local.players.length}`;
  show('screen-reveal');
}

function localTriggerSeeHint(fromModal = false) {
  if (!local) return;
  const p = $('screen-reveal').classList.contains('active')
    ? local.players[local.passIndex]
    : local.players[local.clueIndex];
  if (!p) return;
  if (!p.hintViewed) {
    p.hintViewed = true;
    p.hintViewedAt = Date.now();
    p.hintExpired = false;
  }
  const st = getLocalPlayerHintStatus(p);
  const hintText = p.isImposter ? local.imposterHint : local.crewHint;
  if (st.status === 'unlocked') {
    startHintTimerHud(st.remaining, HINT_TIMER_DURATION);
  }
  if (fromModal) {
    setHintVaultState('peek', st.status, hintText);
  } else {
    setHintVaultState('reveal', st.status, hintText);
  }
  updateHintTimerTick();
}

function localHideAndContinue() {
  if (!local) return;
  playSfx('click');
  stopHintTimerHud();
  local.passIndex++;
  if (local.passIndex < local.players.length) {
    localRenderPass();
  } else {
    local.phase = 'clue';
    local.round = 1;
    local.clueIndex = localNextActiveIndex(0);
    localRenderClue();
  }
}

function localNextActiveIndex(startIdx) {
  for (let i = startIdx; i < local.players.length; i++) {
    if (!local.players[i].eliminated) return i;
  }
  return -1;
}

// ============================================================================
// LOCAL CLUES & MULTI-ROUND SUMMARY
// ============================================================================
function localRenderClue() {
  if (!local) return;
  clearRecording();
  $('clueRoundHeader').textContent = `LEVEL ${local.level} • ROUND ${local.round} OF ${local.maxRounds} — CLUES`;
  const p = local.players[local.clueIndex];
  if (!p) return;
  $('cluePlayerName').textContent = p.name;
  $('cluePlayerName').className = 'badge local';
  $('clueSeeHintBtn').style.display = 'inline-block';

  $('clueInput').value = '';
  $('clueInput').disabled = false;
  $('clueSubmitBtn').disabled = false;
  $('clueSubmitBtn').textContent = 'Send Text';
  $('voiceSubmitBtn').style.display = 'none';
  $('clueError').textContent = '';

  const wl = $('clueWaitingList');
  wl.innerHTML = '';
  const activePlayers = local.players.filter(pl => !pl.eliminated);
  local.players.forEach((pl, i) => {
    const d = document.createElement('div');
    d.className = 'player-row' + (pl.eliminated ? ' eliminated' : '');
    let status = '⏳ WAITING';
    if (pl.eliminated) status = '💀 OUT';
    else if (pl.clue || pl.clueAudio) status = '✅ SENT';
    else if (i === local.clueIndex) status = '✏️ YOUR TURN';
    d.innerHTML = `<span>${esc(pl.name)}</span><span class="tag">${status}</span>`;
    wl.appendChild(d);
  });
  const done = activePlayers.filter(pl => pl.clue || pl.clueAudio).length;
  $('clueProgress').textContent = `STATUS: ${done} / ${activePlayers.length} TRANSMITTED`;
  $('chatFab').style.display = 'none';
  show('screen-clue');
  setTimeout(() => $('clueInput').focus(), 100);
}

function localSnapshotClues() {
  if (!local) return;
  if (local.clueHistory.some(h => h.round === local.round)) return;
  local.clueHistory.push({
    round: local.round,
    clues: local.players.filter(p => !p.eliminated).map(p => ({
      name: p.name, clue: p.clue, clue_audio: p.clueAudio
    }))
  });
}

function localSubmitClue(kind) {
  if (!local) return;
  const p = local.players[local.clueIndex];
  if (!p || p.clue || p.clueAudio) return;
  $('clueError').textContent = '';

  if (kind === 'text') {
    const text = ($('clueInput').value || '').trim();
    if (!text) { $('clueError').textContent = 'ENTER A CLUE.'; return; }
    const w = (local.word || '').toLowerCase();
    if (w && text.toLowerCase().includes(w)) {
      $('clueError').textContent = '❌ CLUE CONTAINS SECRET WORD!';
      return;
    }
    p.clue = text; p.clueAudio = null;
  } else {
    if (!recordedAudioDataUrl) { $('clueError').textContent = 'NO AUDIO DETECTED.'; return; }
    p.clue = ''; p.clueAudio = recordedAudioDataUrl;
    clearRecording();
  }
  playSfx('click');

  const nextIdx = localNextActiveIndex(local.clueIndex + 1);
  if (nextIdx !== -1) {
    local.clueIndex = nextIdx;
    localRenderClue();
  } else {
    localSnapshotClues();
    local.phase = 'summary';
    localRenderSummary();
  }
}

function localRenderSummary() {
  if (!local) return;
  $('summaryHeader').textContent = `ROUND ${local.round} OF ${local.maxRounds} COMPLETE`;
  renderRoundTabs($('summaryTabs'), local.clueHistory, localRenderSummary);
  renderClueHistoryInto($('summaryList'), local.clueHistory, null, true);
  $('summaryNextBtn').style.display = 'block';
  $('summaryNextBtn').textContent = local.round < local.maxRounds ? `Start Round ${local.round + 1} →` : 'Proceed to Voting →';
  $('summaryProgress').textContent = 'Analyze clues & mark suspects 🔍';
  show('screen-summary');
  $('chatFab').style.display = 'none';
}

function localAdvance() {
  if (!local) return;
  if (local.phase === 'summary') {
    if (local.round < local.maxRounds) {
      local.round++;
      local.players.forEach(p => { p.clue = ''; p.clueAudio = null; });
      local.clueIndex = localNextActiveIndex(0);
      local.phase = 'clue';
      localRenderClue();
    } else {
      local.phase = 'vote';
      local.eliminationNotice = '';
      local.players.forEach(p => { p.vote = null; });
      local.voteIndex = localNextActiveIndex(0);
      localRenderVote();
    }
  }
}

// ============================================================================
// LOCAL VOTE, MULTI-IMPOSTER ELIMINATION & LAST STAND
// ============================================================================
function localRenderVote() {
  if (!local) return;
  const voter = local.players[local.voteIndex];
  if (!voter) return;
  const notice = $('voteElimNotice');
  if (local.eliminationNotice) {
    notice.style.display = 'block';
    notice.textContent = local.eliminationNotice;
  } else notice.style.display = 'none';

  $('voteVoterName').textContent = voter.name;
  $('voteVoterName').className = 'badge local';
  local.selectedVote = null;
  $('voteSubmitBtn').disabled = true;
  $('voteSubmitBtn').textContent = 'LOCK VOTE';
  $('voteError').textContent = '';

  const list = $('voteList');
  list.innerHTML = '';
  local.players.forEach((p, i) => {
    if (i === local.voteIndex || p.eliminated) return;
    const isSus = markedSuspects.has(p.name);
    const btn = document.createElement('button');
    btn.className = 'vote-btn';
    btn.innerHTML = `<span>${esc(p.name)}</span><span>${isSus ? '🚩' : ''}</span>`;
    btn.onclick = () => {
      playSfx('click');
      local.selectedVote = p.name;
      document.querySelectorAll('.vote-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      $('voteSubmitBtn').disabled = false;
    };
    list.appendChild(btn);
  });

  const wl = $('voteWaitingList');
  wl.innerHTML = '';
  local.players.forEach((p, i) => {
    const d = document.createElement('div');
    d.className = 'player-row' + (p.eliminated ? ' eliminated' : '');
    let status = '⏳ WAITING';
    if (p.eliminated) status = '💀 CAUGHT';
    else if (p.vote) status = '✅ VOTED';
    else if (i === local.voteIndex) status = '✏️ YOUR TURN';
    d.innerHTML = `<span>${esc(p.name)}</span><span class="tag">${status}</span>`;
    wl.appendChild(d);
  });
  $('voteChatHint').style.display = 'none';
  $('chatFab').style.display = 'none';
  show('screen-vote');
}

function localSubmitVote() {
  if (!local || !local.selectedVote) return;
  playSfx('click');
  local.players[local.voteIndex].vote = local.selectedVote;
  const nextIdx = localNextActiveIndex(local.voteIndex + 1);
  if (nextIdx !== -1) {
    local.voteIndex = nextIdx;
    localRenderVote();
  } else {
    localResolveVotes(false);
  }
}

function localResolveVotes(timedOut = false) {
  const active = local.players.filter(p => !p.eliminated);
  const counts = {};
  active.forEach(p => counts[p.name] = 0);
  active.forEach(p => { if (p.vote in counts) counts[p.vote]++; });
  const vals = Object.values(counts);
  const top = vals.length ? Math.max(...vals) : 0;
  const leaders = Object.entries(counts).filter(([, c]) => c === top && c > 0).map(([n]) => n);
  const tie = leaders.length !== 1;
  const votedOut = tie ? null : leaders[0];
  const imposterNames = local.players.filter(p => p.isImposter).map(p => p.name);

  if (tie || !votedOut) {
    const reason = 'Vote tied — Imposters escaped!';
    localFinalizeResult('imposter', reason, counts, true, null, '');
    return;
  }

  const victim = local.players.find(p => p.name === votedOut);
  if (victim && victim.isImposter) {
    victim.eliminated = true;
    const remainingImps = local.players.filter(p => p.isImposter && !p.eliminated);
    if (remainingImps.length > 0) {
      local.eliminationNotice = `🎯 ${votedOut} WAS AN IMPOSTER! ${remainingImps.length} imposter still loose — vote again!`;
      local.players.forEach(p => { p.vote = null; });
      local.voteIndex = localNextActiveIndex(0);
      localRenderVote();
      return;
    }
    if (local.lastGuessEnabled) {
      localStartLastGuess(votedOut, counts);
    } else {
      localFinalizeResult('crew', `All Imposters caught! ${votedOut} was eliminated.`, counts, false, votedOut, '');
    }
  } else {
    localFinalizeResult('imposter', `${votedOut} was innocent Crew! Imposters win.`, counts, false, votedOut, '');
  }
}

function localStartLastGuess(imposterName, counts) {
  local.phase = 'last_guess';
  local.pendingLastGuess = { imposterName, counts, remaining: LAST_GUESS_DURATION };
  show('screen-last-guess');
  $('lastGuessInfo').textContent = `Pass to ${imposterName} (Caught Imposter)! Guess the exact Secret Word to steal the win!`;
  $('lastGuessInput').value = '';
  $('lastGuessInputWrap').style.display = 'block';
  $('lastGuessWaitMsg').style.display = 'none';
  $('lastGuessClock').textContent = LAST_GUESS_DURATION + 's';
  setTimeout(() => $('lastGuessInput').focus(), 100);

  if (lastGuessInterval) clearInterval(lastGuessInterval);
  lastGuessInterval = setInterval(() => {
    if (!local || local.phase !== 'last_guess') { clearInterval(lastGuessInterval); return; }
    local.pendingLastGuess.remaining--;
    $('lastGuessClock').textContent = Math.max(0, local.pendingLastGuess.remaining) + 's';
    if (local.pendingLastGuess.remaining <= 5 && local.pendingLastGuess.remaining > 0) playSfx('tick');
    if (local.pendingLastGuess.remaining <= 0) {
      clearInterval(lastGuessInterval);
      localSubmitImposterGuess(true);
    }
  }, 1000);
}

function localSubmitImposterGuess(timedOut = false) {
  if (!local || local.phase !== 'last_guess') return;
  if (lastGuessInterval) { clearInterval(lastGuessInterval); lastGuessInterval = null; }
  const { imposterName, counts } = local.pendingLastGuess;
  const guess = timedOut ? '' : $('lastGuessInput').value.trim();
  const secret = (local.word || '').trim().toLowerCase();
  if (!timedOut && guess && guess.toLowerCase() === secret) {
    localFinalizeResult('imposter', `🔥 CLUTCH STEAL! ${imposterName} guessed '${local.word}' correctly!`, counts, false, imposterName, guess);
  } else {
    const gLabel = timedOut ? '(Timed Out)' : (guess || '(Skipped)');
    localFinalizeResult('crew', `${imposterName} missed the final guess! Crew wins!`, counts, false, imposterName, gLabel);
  }
}

function localFinalizeResult(banner, reason, counts, tie, votedOut, guessText) {
  stopHintTimerHud();
  local.phase = 'result';
  const crewPts = local.levelCfg.crew_pts;
  const impPts = local.levelCfg.imposter_pts;
  local.players.forEach(p => {
    const won = (banner === 'crew' && !p.isImposter) || (banner === 'imposter' && p.isImposter);
    if (won) {
      p.streak = (p.streak || 0) + 1;
      p.score = (p.score || 0) + (banner === 'crew' ? crewPts : impPts) + (p.streak - 1) * 25;
      p.wins = (p.wins || 0) + 1;
    } else {
      p.streak = 0;
    }
  });
  playSfx(banner === 'crew' ? 'win' : 'lose');
  const imposterNames = local.players.filter(p => p.isImposter).map(p => p.name);
  localResult = { counts, tie, votedOut, imposterNames, banner, reason, guessText };
  localRenderResult();
}

function localRenderResult() {
  if (!local || !localResult) return;
  const { counts, tie, votedOut, imposterNames, banner, reason, guessText } = localResult;
  $('resultBanner').textContent = banner === 'crew' ? '🎉 CREW WINS!' : '😈 IMPOSTERS WIN!';
  $('resultBanner').className = 'banner ' + banner;

  let detail = `${esc(reason)}<br>`;
  if (guessText) detail += `FINAL GUESS: <strong>${esc(guessText)}</strong><br>`;
  detail += `LEVEL ${local.level} (${esc(local.levelCfg.name)}) • CATEGORY: <strong>${esc(local.wordCategory)}</strong><br>`;
  detail += `SECRET WORD: <strong>${esc(local.word)}</strong>`;
  $('resultDetail').innerHTML = detail;

  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const topCount = entries.length ? entries[0][1] : 0;
  $('voteSummary').innerHTML = entries.map(([n, c]) =>
    `<div class="vote-row ${c === topCount && c > 0 && !tie ? 'top' : ''}">
       <span>${esc(n)}${imposterNames.includes(n) ? ' 🤫' : ''}</span>
       <span class="count">${c} VOTE${c === 1 ? '' : 'S'}</span></div>`
  ).join('');

  $('imposterBox').innerHTML =
    `<div class="round-header">IMPOSTER${imposterNames.length > 1 ? 'S' : ''}</div>` +
    imposterNames.map(n => `<span class="imposter-pill">🕵️ ${esc(n)}</span>`).join(' ');

  const sorted = [...local.players].sort((a, b) => b.score - a.score);
  $('scoreboard').innerHTML = '<h4>LEADERBOARD &amp; RANKS</h4>' +
    sorted.map((p, idx) =>
      `<div class="score-row">
         <span>${idx === 0 && p.score > 0 ? '👑 ' : ''}${esc(p.name)}<span class="rank-tag">${getRank(p.score)}</span>${p.streak >= 2 ? `<span class="streak-tag">🔥${p.streak}x</span>` : ''}</span>
         <span class="pts">${p.score} PTS</span>
       </div>`
    ).join('');

  summaryRoundFilter = 'all';
  renderClueHistoryInto($('resultClues'), local.clueHistory, null, false);

  const canLevelUp = local.level < 5;
  $('nextLevelBtn').style.display = canLevelUp ? 'block' : 'none';
  if (canLevelUp) {
    const nxt = LEVELS_DATA[local.level + 1];
    $('nextLevelBtn').textContent = `🚀 Advance to Level ${nxt.level} (${nxt.name}) →`;
  }
  $('playAgainBtn').style.display = 'block';
  $('resultProgress').textContent = '';
  show('screen-result');
}

// ============================================================================
// VOICE RECORDER
// ============================================================================
function pickMimeType() {
  if (!window.MediaRecorder) return '';
  const candidates = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg'];
  for (const t of candidates) if (MediaRecorder.isTypeSupported(t)) return t;
  return '';
}

async function toggleRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') return stopRecording();
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    $('clueError').textContent = 'RECORDING UNSUPPORTED ON THIS DEVICE.';
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordedChunks = [];
    const mime = pickMimeType();
    mediaRecorder = new MediaRecorder(stream, mime ? { mimeType: mime } : {});
    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
    mediaRecorder.onstop = () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
      const reader = new FileReader();
      reader.onloadend = () => {
        recordedAudioDataUrl = reader.result;
        $('recPlayback').src = recordedAudioDataUrl;
        $('recPlayback').style.display = 'block';
        $('voiceSubmitBtn').style.display = 'block';
        $('recClearBtn').style.display = 'block';
      };
      reader.readAsDataURL(blob);
    };
    mediaRecorder.start();
    recordedAudioDataUrl = null;
    $('recPlayback').style.display = 'none';
    $('voiceSubmitBtn').style.display = 'none';
    $('recClearBtn').style.display = 'none';
    $('recBtn').classList.add('recording');
    $('recBtn').textContent = '⏹';
    recordSeconds = 0;
    $('recInfo').innerHTML = `Recording... <span class="rec-timer">0.0s</span> / 10s`;
    recordTimer = setInterval(() => {
      recordSeconds += 0.1;
      $('recInfo').innerHTML = `Recording... <span class="rec-timer">${recordSeconds.toFixed(1)}s</span> / 10s`;
      if (recordSeconds >= 10) stopRecording();
    }, 100);
  } catch (e) {
    $('clueError').textContent = 'MIC ACCESS DENIED.';
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') mediaRecorder.stop();
  clearInterval(recordTimer);
  $('recBtn').classList.remove('recording');
  $('recBtn').textContent = '🎙️';
  $('recInfo').innerHTML = 'Audio captured. Tap ▶ to preview.';
}

function clearRecording() {
  recordedAudioDataUrl = null;
  $('recPlayback').style.display = 'none';
  $('recPlayback').src = '';
  $('voiceSubmitBtn').style.display = 'none';
  $('recClearBtn').style.display = 'none';
  $('recInfo').innerHTML = 'Tap to record voice clue.<br>Max 10 seconds.';
}

// ============================================================================
// CHAT & MENU
// ============================================================================
function toggleChat() {
  chatOpen = !chatOpen;
  $('chatPanel').classList.toggle('open', chatOpen);
  if (chatOpen) {
    $('chatUnread').style.display = 'none';
    if (current) renderChat(current);
    setTimeout(() => $('chatInput').focus(), 100);
  }
}
function updateChatBadge(s) {
  if (!s.chat) return;
  const newCount = s.chat.length;
  if (newCount > lastChatCount && !chatOpen) {
    const badge = $('chatUnread');
    badge.textContent = newCount - lastChatCount;
    badge.style.display = 'flex';
  }
  lastChatCount = newCount;
}
function renderChat(s) {
  const box = $('chatMessages');
  if (!box) return;
  const atBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 80;
  box.innerHTML = '';
  (s.chat || []).forEach(m => {
    const d = document.createElement('div');
    const isSystem = m.name === 'System';
    const mine = s.you && m.name === s.you.name;
    d.className = 'chat-msg ' + (isSystem ? 'system' : (mine ? 'mine' : 'other'));
    if (isSystem) d.textContent = m.text;
    else d.innerHTML = `<div class="sender">${esc(m.name)}</div>${esc(m.text)}`;
    box.appendChild(d);
  });
  if (atBottom) box.scrollTop = box.scrollHeight;
  const locked = s.phase === 'clue' && !(s.you && (s.you.clue || s.you.clue_audio || s.you.eliminated));
  $('chatLocked').style.display = locked ? 'block' : 'none';
  $('chatInputRow').style.display = locked ? 'none' : 'flex';
}
async function sendChat() {
  if (!session || local) return;
  const input = $('chatInput');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  try {
    const r = await api('chat', { ...session, text });
    if (r && r.phase) applyState(r);
  } catch (e) {
    const m = { chat_locked: 'COMMS LOCKED.', chat_blocked_during_clue: 'SUBMIT CLUE FIRST!', empty: 'TYPE MESSAGE.' };
    alert(m[e.message] || e.message);
  }
}

function toggleMenu() { $('menuPanel').classList.toggle('open'); }
async function leaveGame() {
  if (!session) return;
  if (!confirm('Disconnect from lobby?')) return;
  try { await api('leave', session); } catch (e) {}
  saveSession(null); stopPolling(); backToMode();
}
async function endGame() {
  if (!session) return;
  if (!confirm('Terminate lobby for all agents?')) return;
  try { await api('end', session); } catch (e) {}
  saveSession(null); stopPolling(); backToMode();
}

// ============================================================================
// BOOT
// ============================================================================
(async function boot() {
  await ensureWordCache();
  if (session) {
    $('resumeHint').style.display = 'block';
    $('playerName').value = session.name || '';
    try { applyState(await api('state', session)); return; }
    catch (e) { saveSession(null); }
  }
  const params = new URLSearchParams(location.search);
  if (params.get('code')) {
    show('screen-home');
    showJoin();
  } else {
    show('screen-mode');
  }
})();

$('playerName').addEventListener('keydown', e => { if (e.key === 'Enter') $('joinCode').focus(); });
$('joinCode').addEventListener('keydown', e => { if (e.key === 'Enter') joinGame(); });
$('clueInput').addEventListener('keydown', e => { if (e.key === 'Enter') submitClue(); });
$('chatInput').addEventListener('keydown', e => { if (e.key === 'Enter') sendChat(); });
$('lastGuessInput').addEventListener('keydown', e => { if (e.key === 'Enter') submitImposterGuess(); });
</script>
</body>
</html>
"""


# ===========================================================================
# SERVER
# ===========================================================================
def open_browser():
    webbrowser.open(f"http://localhost:{PORT}/")


class ThreadingServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 50


def _graceful_shutdown(sig, frame):
    print("\n[SHUTDOWN]")
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, _graceful_shutdown)
    print(f"[BOOT] Imposter Protocol Advanced Edition | port={PORT} RENDER={os.environ.get('RENDER', 'no')}")
    with ThreadingServer(("0.0.0.0", PORT), GameHandler) as httpd:
        print(f"[BOOT] Listening on 0.0.0.0:{PORT}")
        if not os.environ.get("RENDER"):
            threading.Timer(1.0, open_browser).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


if __name__ == "__main__":
    main()
