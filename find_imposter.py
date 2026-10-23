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

# ===========================================================================
# WORD BANK
# ===========================================================================
WORD_BANK = [
    {"en": {"word": "Mobile Phone", "imposter_hint": "It is an electronic gadget used daily."},
     "hi": {"word": "मोबाइल फोन", "imposter_hint": "यह एक इलेक्ट्रॉनिक गैजेट है जिसका रोज़ इस्तेमाल होता है।"}},
    {"en": {"word": "Television", "imposter_hint": "It has a screen and people watch it at home."},
     "hi": {"word": "टेलीविज़न", "imposter_hint": "इसकी स्क्रीन होती है और लोग इसे घर पर देखते हैं।"}},
    {"en": {"word": "Refrigerator", "imposter_hint": "It keeps things cold in the kitchen."},
     "hi": {"word": "फ्रिज", "imposter_hint": "यह रसोई में चीज़ों को ठंडा रखता है।"}},
    {"en": {"word": "Washing Machine", "imposter_hint": "It cleans clothes automatically."},
     "hi": {"word": "वॉशिंग मशीन", "imposter_hint": "यह कपड़ों को अपने आप साफ करती है।"}},
    {"en": {"word": "Air Conditioner", "imposter_hint": "It makes a room cool in summer."},
     "hi": {"word": "एयर कंडीशनर", "imposter_hint": "यह गर्मियों में कमरे को ठंडा करता है।"}},
    {"en": {"word": "Fan", "imposter_hint": "It spins and moves air around."},
     "hi": {"word": "पंखा", "imposter_hint": "यह घूमता है और हवा को इधर-उधर करता है।"}},
    {"en": {"word": "Laptop", "imposter_hint": "It is portable and used for work or study."},
     "hi": {"word": "लैपटॉप", "imposter_hint": "यह पोर्टेबल है और काम या पढ़ाई के लिए उपयोग होता है।"}},
    {"en": {"word": "Clock", "imposter_hint": "It shows the time on a wall or table."},
     "hi": {"word": "घड़ी", "imposter_hint": "यह दीवार या मेज़ पर समय दिखाती है।"}},
    {"en": {"word": "Umbrella", "imposter_hint": "You carry it when it rains."},
     "hi": {"word": "छाता", "imposter_hint": "बारिश में इसे साथ ले जाते हैं।"}},
    {"en": {"word": "Chair", "imposter_hint": "It has legs and you sit on it."},
     "hi": {"word": "कुर्सी", "imposter_hint": "इसके पैर होते हैं और आप इस पर बैठते हैं।"}},
    {"en": {"word": "School", "imposter_hint": "It is a place where people go to learn."},
     "hi": {"word": "स्कूल", "imposter_hint": "यह एक ऐसी जगह है जहाँ लोग सीखने जाते हैं।"}},
    {"en": {"word": "Hospital", "imposter_hint": "People go here when they are very sick."},
     "hi": {"word": "अस्पताल", "imposter_hint": "बहुत बीमार होने पर लोग यहाँ जाते हैं।"}},
    {"en": {"word": "Library", "imposter_hint": "It is a quiet place full of shelves."},
     "hi": {"word": "पुस्तकालय", "imposter_hint": "यह एक शांत जगह है जहाँ बहुत सी अलमारियाँ होती हैं।"}},
    {"en": {"word": "Temple", "imposter_hint": "People go here to pray and find peace."},
     "hi": {"word": "मंदिर", "imposter_hint": "लोग यहाँ प्रार्थना करने और शांति पाने जाते हैं।"}},
    {"en": {"word": "Beach", "imposter_hint": "It has sand, water, and waves."},
     "hi": {"word": "समुद्र तट", "imposter_hint": "यहाँ रेत, पानी और लहरें होती हैं।"}},
    {"en": {"word": "Market", "imposter_hint": "People buy and sell things here."},
     "hi": {"word": "बाज़ार", "imposter_hint": "यहाँ लोग चीज़ें खरीदते और बेचते हैं।"}},
    {"en": {"word": "Airport", "imposter_hint": "It is where flights take off and land."},
     "hi": {"word": "हवाई अड्डा", "imposter_hint": "यहाँ से हवाई जहाज़ उड़ते और उतरते हैं।"}},
    {"en": {"word": "Park", "imposter_hint": "It is an open green space for relaxing."},
     "hi": {"word": "पार्क", "imposter_hint": "यह आराम करने के लिए खुली हरी जगह है।"}},
    {"en": {"word": "Restaurant", "imposter_hint": "People go here to eat food made by others."},
     "hi": {"word": "रेस्टोरेंट", "imposter_hint": "लोग यहाँ दूसरों के बनाए खाने के लिए जाते हैं।"}},
    {"en": {"word": "Gym", "imposter_hint": "People go here to exercise and get fit."},
     "hi": {"word": "जिम", "imposter_hint": "लोग यहाँ व्यायाम करने और फिट होने जाते हैं।"}},
    {"en": {"word": "Elephant", "imposter_hint": "It is a large animal with a long trunk."},
     "hi": {"word": "हाथी", "imposter_hint": "यह एक बड़ा जानवर है जिसकी लंबी सूंड होती है।"}},
    {"en": {"word": "Dog", "imposter_hint": "It is a loyal pet that barks."},
     "hi": {"word": "कुत्ता", "imposter_hint": "यह एक वफादार पालतू जानवर है जो भौंकता है।"}},
    {"en": {"word": "Cat", "imposter_hint": "It is a small pet that meows and purrs."},
     "hi": {"word": "बिल्ली", "imposter_hint": "यह एक छोटा पालतू जानवर है जो म्याऊं करता है।"}},
    {"en": {"word": "Lion", "imposter_hint": "It is called the king of the jungle."},
     "hi": {"word": "शेर", "imposter_hint": "इसे जंगल का राजा कहा जाता है।"}},
    {"en": {"word": "Peacock", "imposter_hint": "It is a colorful bird that spreads its feathers."},
     "hi": {"word": "मोर", "imposter_hint": "यह एक रंग-बिरंगा पक्षी है जो अपने पंख फैलाता है।"}},
    {"en": {"word": "Rain", "imposter_hint": "It falls from the sky and makes things wet."},
     "hi": {"word": "बारिश", "imposter_hint": "यह आसमान से गिरती है और चीज़ों को गीला करती है।"}},
    {"en": {"word": "Sun", "imposter_hint": "It is bright and rises every morning."},
     "hi": {"word": "सूरज", "imposter_hint": "यह चमकीला है और हर सुबह उगता है।"}},
    {"en": {"word": "Moon", "imposter_hint": "It glows at night in the sky."},
     "hi": {"word": "चाँद", "imposter_hint": "यह रात में आसमान में चमकता है।"}},
    {"en": {"word": "Mountain", "imposter_hint": "It is a very tall natural landform."},
     "hi": {"word": "पहाड़", "imposter_hint": "यह एक बहुत ऊँची प्राकृतिक भू-आकृति है।"}},
    {"en": {"word": "River", "imposter_hint": "Water flows along it toward the sea."},
     "hi": {"word": "नदी", "imposter_hint": "इसमें पानी बहकर समुद्र की ओर जाता है।"}},
    {"en": {"word": "Tea", "imposter_hint": "It is a hot drink people have in the morning."},
     "hi": {"word": "चाय", "imposter_hint": "यह एक गर्म पेय है जो लोग सुबह में पीते हैं।"}},
    {"en": {"word": "Pizza", "imposter_hint": "It is a round food cut into slices."},
     "hi": {"word": "पिज़्ज़ा", "imposter_hint": "यह एक गोल खाना है जिसे टुकड़ों में काटा जाता है।"}},
    {"en": {"word": "Mango", "imposter_hint": "It is a sweet yellow summer fruit."},
     "hi": {"word": "आम", "imposter_hint": "यह गर्मियों का एक मीठा पीला फल है।"}},
    {"en": {"word": "Ice Cream", "imposter_hint": "It is cold, sweet, and melts quickly."},
     "hi": {"word": "आइस क्रीम", "imposter_hint": "यह ठंडी, मीठी होती है और जल्दी पिघलती है।"}},
    {"en": {"word": "Bread", "imposter_hint": "It is baked and used to make sandwiches."},
     "hi": {"word": "ब्रेड", "imposter_hint": "इसे बेक किया जाता है और सैंडविच बनाने में उपयोग होता है।"}},
    {"en": {"word": "Coffee", "imposter_hint": "It is a dark, bitter drink that wakes you up."},
     "hi": {"word": "कॉफ़ी", "imposter_hint": "यह एक गहरा, कड़वा पेय है जो आपको जगाता है।"}},
    {"en": {"word": "Rice", "imposter_hint": "It is a small white grain eaten with curry."},
     "hi": {"word": "चावल", "imposter_hint": "यह छोटा सफेद दाना है जिसे करी के साथ खाते हैं।"}},
    {"en": {"word": "Chocolate", "imposter_hint": "It is a sweet brown treat people love."},
     "hi": {"word": "चॉकलेट", "imposter_hint": "यह एक मीठी भूरी चीज़ है जो लोगों को बहुत पसंद है।"}},
    {"en": {"word": "Banana", "imposter_hint": "It is a long yellow fruit you peel."},
     "hi": {"word": "केला", "imposter_hint": "यह एक लंबा पीला फल है जिसे छीलकर खाते हैं।"}},
    {"en": {"word": "Water", "imposter_hint": "It is clear, tasteless, and essential for life."},
     "hi": {"word": "पानी", "imposter_hint": "यह साफ, बेस्वाद और जीवन के लिए ज़रूरी है।"}},
    {"en": {"word": "Car", "imposter_hint": "It is a mode of transport with four wheels."},
     "hi": {"word": "कार", "imposter_hint": "यह चार पहियों वाला परिवहन का एक साधन है।"}},
    {"en": {"word": "Train", "imposter_hint": "It moves on tracks and carries many people."},
     "hi": {"word": "ट्रेन", "imposter_hint": "यह पटरी पर चलती है और बहुत से लोगों को ले जाती है।"}},
    {"en": {"word": "Airplane", "imposter_hint": "It flies high in the sky across countries."},
     "hi": {"word": "हवाई जहाज़", "imposter_hint": "यह आसमान में ऊँचा उड़कर देशों के पार जाता है।"}},
    {"en": {"word": "Bicycle", "imposter_hint": "It has two wheels and you pedal it."},
     "hi": {"word": "साइकिल", "imposter_hint": "इसके दो पहिये होते हैं और आप इसे पैडल से चलाते हैं।"}},
    {"en": {"word": "Cricket", "imposter_hint": "It is a popular sport played with a bat and ball."},
     "hi": {"word": "क्रिकेट", "imposter_hint": "यह बल्ले और गेंद से खेला जाने वाला लोकप्रिय खेल है।"}},
    {"en": {"word": "Football", "imposter_hint": "It is a sport played with a round ball and goals."},
     "hi": {"word": "फुटबॉल", "imposter_hint": "यह गोल गेंद और गोल पोस्ट के साथ खेला जाने वाला खेल है।"}},
    {"en": {"word": "Doctor", "imposter_hint": "This person helps people when they are unwell."},
     "hi": {"word": "डॉक्टर", "imposter_hint": "यह व्यक्ति बीमार होने पर लोगों की मदद करता है।"}},
    {"en": {"word": "Teacher", "imposter_hint": "This person explains lessons to students."},
     "hi": {"word": "शिक्षक", "imposter_hint": "यह व्यक्ति छात्रों को पाठ समझाता है।"}},
    {"en": {"word": "Police", "imposter_hint": "They enforce law and keep people safe."},
     "hi": {"word": "पुलिस", "imposter_hint": "वे कानून लागू करते हैं और लोगों को सुरक्षित रखते हैं।"}},
    {"en": {"word": "Wedding", "imposter_hint": "It is a joyful ceremony where two people marry."},
     "hi": {"word": "शादी", "imposter_hint": "यह एक खुशी का समारोह है जहाँ दो लोग विवाह करते हैं।"}},
]

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
        "score": 0,
    }

def _tally_votes(game):
    counts = {p["name"]: 0 for p in game["players"]}
    for p in game["players"]:
        if p["vote"] in counts:
            counts[p["vote"]] += 1
    top = max(counts.values()) if counts else 0
    leaders = [n for n, c in counts.items() if c == top and c > 0]
    if len(leaders) == 1:
        return leaders[0], False, counts
    return None, True, counts

def _public_state(game, token):
    players = []
    for p in game["players"]:
        voice_out = None
        if p.get("clue_audio") and game["phase"] in ("summary", "vote", "result"):
            voice_out = p["clue_audio"]
        players.append({
            "name": p["name"],
            "ready": p["ready"],
            "has_clue": bool(p["clue"] or p.get("clue_audio")),
            "clue": p["clue"] if game["phase"] in ("summary", "vote", "result") else "",
            "clue_audio": voice_out,
            "has_voted": p["vote"] is not None,
            "score": p.get("score", 0),
        })
    me = next((p for p in game["players"] if p["token"] == token), None)
    host = next((p for p in game["players"] if p["token"] == game["host_token"]), None)
    state = {
        "code": game["code"], "phase": game["phase"], "lang": game["lang"],
        "round": game["round"], "players": players,
        "is_host": bool(me and me["token"] == game["host_token"]),
        "host_name": host["name"] if host else "",
        "imposter_count": game["imposter_count"],
        "chat": game.get("chat", [])[-60:],
        "chat_open": game.get("chat_open", True),
        "reactions": game.get("reactions", []), # LIVE REACTIONS
        "you": None,
    }
    if me:
        state["you"] = {
            "name": me["name"], "ready": me["ready"],
            "clue": me["clue"], "clue_audio": me.get("clue_audio"),
            "has_voted": me["vote"] is not None,
            "score": me.get("score", 0),
        }
        if game["phase"] in ("reveal", "clue", "summary", "vote", "result"):
            state["your_word"] = me["role_word"]
            state["your_hint"] = me["role_hint"]
            state["you_are_imposter"] = me["is_imposter"]
    if game["phase"] == "result":
        state["imposter_names"] = game["imposter_names"]
        state["secret_word"] = game["word"]
        state["result_banner"] = game["result_banner"]
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
            self._json(200, {"words": WORD_BANK})
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
            "/api/start": self._handle_start,
            "/api/clue": self._handle_clue,
            "/api/audio": self._handle_audio,
            "/api/advance": self._handle_advance,
            "/api/vote": self._handle_vote,
            "/api/reset": self._handle_reset,
            "/api/chat": self._handle_chat,
            "/api/react": self._handle_react, # NEW
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
            return fn(game, token, payload)

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
                "word": "", "imposter_hint": "", "imposter_index": 0,
                "imposter_count": 1, "imposter_names": [],
                "result_banner": "", "vote_counts": {},
                "voted_out_name": None, "vote_tie": False,
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

    def _handle_start(self):
        payload = self._read_json() or {}
        num_imposters = payload.get("num_imposters", 1)
        def run(game, token, payload):
            if token != game["host_token"]:
                return self._json(403, {"error": "host_only"})
            if game["phase"] != "lobby":
                return self._json(409, {"error": "already_started"})
            n = len(game["players"])
            if n < 3:
                return self._json(400, {"error": "need_3_players"})
            try:
                k = int(num_imposters)
            except (TypeError, ValueError):
                k = 1
            max_k = max(1, (n - 1) // 2)
            k = max(1, min(k, max_k))
            entry = random.choice(WORD_BANK)[game["lang"]]
            game["word"] = entry["word"]
            game["imposter_hint"] = entry["imposter_hint"]
            game["imposter_count"] = k
            imposter_indices = set(random.sample(range(n), k))
            game["imposter_index"] = next(iter(imposter_indices))
            game["imposter_names"] = [game["players"][i]["name"] for i in sorted(imposter_indices)]
            for i, p in enumerate(game["players"]):
                p["is_imposter"] = i in imposter_indices
                if p["is_imposter"]:
                    p["role_word"] = ""
                    p["role_hint"] = game["imposter_hint"]
                else:
                    p["role_word"] = game["word"]
                    p["role_hint"] = ""
                p["clue"] = ""
                p["clue_audio"] = None
                p["vote"] = None
            game["phase"] = "reveal"
            game["round"] = 1
            game["result_banner"] = ""
            game["vote_counts"] = {}
            game["voted_out_name"] = None
            game["vote_tie"] = False
            game["reactions"] = [] # Clear reactions
            self._add_chat(game, "System", "Game started! Check your secret role.")
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_clue(self):
        payload = self._read_json() or {}
        text = (payload.get("text") or "").strip()[:80]
        def run(game, token, payload):
            if game["phase"] != "clue":
                return self._json(409, {"error": "not_clue_phase"})
            me = self._find_player(game, token)
            if not text:
                return self._json(400, {"error": "empty_clue"})
            if me["clue"] or me.get("clue_audio"):
                return self._json(409, {"error": "already_submitted"})
            if game["word"] and game["word"].lower() in text.lower():
                return self._json(400, {"error": "contains_word"})
            me["clue"] = text
            if all(p["clue"] or p.get("clue_audio") for p in game["players"]):
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
            if me["clue"] or me.get("clue_audio"):
                return self._json(409, {"error": "already_submitted"})
            if not data.startswith("data:audio/"):
                return self._json(400, {"error": "bad_audio_format"})
            if len(data) > MAX_VOICE_BYTES:
                return self._json(413, {"error": "audio_too_large"})
            me["clue_audio"] = data
            me["clue"] = ""
            if all(p["clue"] or p.get("clue_audio") for p in game["players"]):
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
                if game["round"] == 1:
                    game["round"] = 2
                    game["phase"] = "clue"
                    for p in game["players"]:
                        p["clue"] = ""
                        p["clue_audio"] = None
                else:
                    game["phase"] = "vote"
                    for p in game["players"]:
                        p["vote"] = None
            game["reactions"] = [] # Clear reactions on phase change
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_vote(self):
        payload = self._read_json() or {}
        target = payload.get("target")
        def run(game, token, payload):
            if game["phase"] != "vote":
                return self._json(409, {"error": "not_vote_phase"})
            me = self._find_player(game, token)
            names = [p["name"] for p in game["players"]]
            if target not in names:
                return self._json(400, {"error": "bad_target"})
            if target == me["name"]:
                return self._json(400, {"error": "cannot_vote_self"})
            me["vote"] = target
            if all(p["vote"] for p in game["players"]):
                game["phase"] = "result"
                top_name, is_tie, counts = _tally_votes(game)
                game["vote_counts"] = counts
                game["vote_tie"] = is_tie
                game["voted_out_name"] = top_name
                imposter_names = set(game["imposter_names"])
                if is_tie:
                    game["result_banner"] = "imposter"
                elif top_name in imposter_names:
                    game["result_banner"] = "crew" if len(imposter_names) == 1 else "imposter"
                else:
                    game["result_banner"] = "imposter"
                if game["result_banner"] == "crew":
                    for p in game["players"]:
                        if not p["is_imposter"]:
                            p["score"] = p.get("score", 0) + 1
                else:
                    for p in game["players"]:
                        if p["is_imposter"]:
                            p["score"] = p.get("score", 0) + 1
                self._add_chat(game, "System",
                    "Crew wins!" if game["result_banner"] == "crew" else "Imposters win!")
            self._json(200, _public_state(game, token))
        self._with_game(payload, run)

    def _handle_reset(self):
        payload = self._read_json() or {}
        def run(game, token, payload):
            if token != game["host_token"]:
                return self._json(403, {"error": "host_only"})
            game["phase"] = "lobby"
            game["round"] = 1
            game["word"] = ""
            game["imposter_hint"] = ""
            game["imposter_count"] = 1
            game["imposter_names"] = []
            game["result_banner"] = ""
            game["vote_counts"] = {}
            game["voted_out_name"] = None
            game["vote_tie"] = False
            game["chat_open"] = True
            game["reactions"] = []
            for p in game["players"]:
                p["clue"] = ""
                p["clue_audio"] = None
                p["vote"] = None
                p["ready"] = False
                p["is_imposter"] = False
                p["role_word"] = ""
                p["role_hint"] = ""
            self._add_chat(game, "System", "New game ready — everyone, please ready up.")
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
            if game["phase"] == "clue" and not (me["clue"] or me.get("clue_audio")):
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
                # Limit reaction list size and add timestamp
                game.setdefault("reactions", []).append({
                    "emoji": emoji,
                    "name": me["name"],
                    "ts": time.time()
                })
                # Keep only reactions from the last 3 seconds to prevent spam
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
                self._add_chat(game, "System",
                    f"{game['players'][0]['name']} is now the host")
            if not game["players"]:
                del GAMES[code]
            elif len(game["players"]) < 3 and game["phase"] != "lobby":
                game["phase"] = "lobby"
                for p in game["players"]:
                    p["ready"] = False
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
# HTML (GAME ARENA THEME + TUTORIAL + REACTIONS)
# ===========================================================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Imposter Protocol</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&display=swap');

  :root {
    --bg-base: #05050f;
    --bg-card: rgba(15, 17, 30, 0.85);
    --neon-cyan: #00f3ff;
    --neon-purple: #b026ff;
    --neon-red: #ff003c;
    --neon-green: #00ff66;
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
      linear-gradient(rgba(0, 243, 255, 0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 243, 255, 0.05) 1px, transparent 1px);
    background-size: 30px 30px;
    color: var(--text-main); 
    min-height: 100vh;
    display: flex; align-items: flex-start; justify-content: center; 
    padding: 16px;
    padding-bottom: 90px;
    overflow-x: hidden;
  }

  /* Scanline effect */
  body::after {
    content: " ";
    display: block;
    position: fixed;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    z-index: 2;
    background-size: 100% 2px, 3px 100%;
    pointer-events: none;
  }

  .app {
    width: 100%; max-width: 540px;
    background: var(--bg-card);
    border: 1px solid rgba(0, 243, 255, 0.3);
    border-radius: 16px; padding: 28px 24px;
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.1), inset 0 0 20px rgba(0, 243, 255, 0.05);
    backdrop-filter: blur(10px);
    margin: auto;
    position: relative;
    z-index: 5;
  }

  .app::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px; bottom: -1px;
    border-radius: 16px;
    pointer-events: none;
    border: 1px solid transparent;
    background: linear-gradient(135deg, var(--neon-cyan) 0%, transparent 40%, transparent 60%, var(--neon-purple) 100%) border-box;
    -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: destination-out;
    mask-composite: exclude;
  }

  h1 { 
    font-size: 2rem; text-align: center; margin-bottom: 4px; 
    text-transform: uppercase; letter-spacing: 2px;
    color: #fff;
    text-shadow: 0 0 10px var(--neon-cyan), 0 0 20px var(--neon-cyan);
  }
  h2 { 
    font-size: 1.3rem; text-align: center; margin-bottom: 8px; 
    text-transform: uppercase; letter-spacing: 1px; color: var(--neon-cyan);
  }
  .subtitle { text-align: center; color: var(--text-muted); font-size: 0.95rem; margin-bottom: 20px; font-family: var(--font-mono); }
  
  .screen { display: none; }
  .screen.active { display: block; animation: glitch-in 0.3s ease; }
  @keyframes glitch-in { 
    0% { opacity: 0; transform: translateY(10px) scale(0.98); filter: blur(4px); } 
    100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); } 
  }

  label { display: block; font-size: 0.9rem; color: var(--neon-cyan); margin-bottom: 6px; margin-top: 16px; text-transform: uppercase; letter-spacing: 1px; }
  
  select, input[type="text"] {
    width: 100%; padding: 14px; border-radius: 8px;
    border: 1px solid rgba(0, 243, 255, 0.4); 
    background: rgba(0, 0, 0, 0.5); 
    color: var(--text-main); font-size: 1.1rem; font-family: var(--font-mono);
    transition: all 0.2s;
  }
  input[type="text"]:focus, select:focus { 
    outline: none; border-color: var(--neon-cyan);
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
  }

  button {
    width: 100%; padding: 16px; margin-top: 16px; border: none;
    border-radius: 8px; 
    background: rgba(0, 243, 255, 0.1);
    border: 1px solid var(--neon-cyan);
    color: var(--neon-cyan); 
    font-family: var(--font-ui); font-size: 1.1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 0 10px rgba(0, 243, 255, 0.1);
  }
  button:hover:not(:disabled) { 
    background: rgba(0, 243, 255, 0.2); 
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.4);
    transform: translateY(-2px);
  }
  button:active:not(:disabled) { transform: translateY(0); }
  button:disabled { opacity: 0.3; cursor: not-allowed; border-color: var(--text-muted); color: var(--text-muted); box-shadow: none; }
  
  button.secondary { border-color: var(--text-muted); color: var(--text-muted); background: rgba(148, 163, 184, 0.1); }
  button.secondary:hover:not(:disabled) { border-color: #fff; color: #fff; box-shadow: 0 0 15px rgba(255, 255, 255, 0.2); }
  button.danger { border-color: var(--neon-red); color: var(--neon-red); background: rgba(255, 0, 60, 0.1); }
  button.danger:hover:not(:disabled) { background: rgba(255, 0, 60, 0.2); box-shadow: 0 0 20px rgba(255, 0, 60, 0.4); }
  button.big { padding: 24px 16px; font-size: 1.2rem; }

  .mode-grid { display: grid; gap: 16px; margin-top: 24px; }
  .mode-card {
    background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(176, 38, 255, 0.4);
    border-radius: 12px; padding: 20px; cursor: pointer; text-align: left;
    transition: all 0.2s; color: var(--text-main);
    position: relative; overflow: hidden;
  }
  .mode-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
    background: var(--neon-purple); transition: width 0.2s;
  }
  .mode-card:hover { 
    border-color: var(--neon-purple); 
    box-shadow: 0 0 15px rgba(176, 38, 255, 0.2);
    transform: translateX(4px);
  }
  .mode-card:hover::before { width: 100%; opacity: 0.1; }
  .mode-card .icon { font-size: 2rem; margin-bottom: 8px; }
  .mode-card .title { font-size: 1.2rem; font-weight: 700; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px; color: #fff; }
  .mode-card .desc { font-size: 0.9rem; color: var(--text-muted); line-height: 1.4; }

  .role-card { 
    text-align: center; padding: 32px 20px; border-radius: 12px; margin-top: 16px; 
    position: relative; border: 1px solid;
  }
  .role-card.crew { border-color: var(--neon-green); background: rgba(0, 255, 102, 0.05); box-shadow: inset 0 0 30px rgba(0, 255, 102, 0.1); }
  .role-card.imposter { border-color: var(--neon-red); background: rgba(255, 0, 60, 0.05); box-shadow: inset 0 0 30px rgba(255, 0, 60, 0.1); }
  .role-label { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 2px; color: var(--text-muted); font-family: var(--font-mono); }
  .role-word { font-size: 2.2rem; font-weight: 700; margin: 16px 0; word-break: break-word; text-transform: uppercase; letter-spacing: 2px; }
  .role-card.crew .role-word { color: var(--neon-green); text-shadow: 0 0 15px rgba(0, 255, 102, 0.5); }
  .role-card.imposter .role-word { color: var(--neon-red); text-shadow: 0 0 15px rgba(255, 0, 60, 0.5); }
  .role-hint { font-size: 0.95rem; color: var(--text-main); line-height: 1.5; white-space: pre-line; font-family: var(--font-mono); }

  .progress { text-align: center; font-size: 0.85rem; color: var(--neon-purple); margin-top: 16px; font-family: var(--font-mono); letter-spacing: 1px; }
  
  .vote-list { display: grid; gap: 12px; margin-top: 16px; }
  .vote-btn { 
    margin-top: 0; background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(0, 243, 255, 0.3); 
    color: var(--text-main); text-align: left; padding: 16px; border-radius: 8px;
    font-family: var(--font-mono); font-size: 1rem; text-transform: uppercase;
  }
  .vote-btn:hover:not(:disabled) { border-color: var(--neon-cyan); background: rgba(0, 243, 255, 0.1); color: var(--neon-cyan); }
  .vote-btn.selected { border-color: var(--neon-cyan); background: rgba(0, 243, 255, 0.15); color: #fff; box-shadow: 0 0 15px rgba(0, 243, 255, 0.3); }
  .vote-btn.done { opacity: 0.5; border-style: dashed; }

  .result-detail { text-align: center; color: var(--text-main); font-size: 1rem; line-height: 1.8; margin-top: 16px; font-family: var(--font-mono); }
  .result-detail strong { color: #fff; text-shadow: 0 0 5px rgba(255,255,255,0.5); }
  
  .clue-item { padding: 12px 16px; background: rgba(0, 0, 0, 0.4); border-radius: 8px; font-size: 0.95rem; color: var(--text-main); line-height: 1.5; border-left: 2px solid var(--neon-purple); font-family: var(--font-mono); }
  .clue-item .name { color: var(--neon-purple); font-weight: 600; text-transform: uppercase; }
  .clue-item.mine { border-left-color: var(--neon-cyan); }
  .clue-item .play-btn { margin-top: 8px; padding: 6px 12px; font-size: 0.8rem; width: auto; background: rgba(0, 243, 255, 0.1); border: 1px solid var(--neon-cyan); color: var(--neon-cyan); }

  .round-header { text-align: center; margin: 8px 0 12px; font-size: 0.9rem; color: var(--neon-cyan); font-weight: 600; letter-spacing: 2px; text-transform: uppercase; font-family: var(--font-mono); }
  .error { color: var(--neon-red); text-align: center; font-size: 0.9rem; margin-top: 12px; min-height: 1em; font-family: var(--font-mono); text-shadow: 0 0 5px rgba(255, 0, 60, 0.5); }
  
  .vote-summary { margin-top: 16px; display: grid; gap: 8px; }
  .vote-row { display: flex; justify-content: space-between; padding: 10px 16px; background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; font-size: 0.95rem; color: var(--text-main); font-family: var(--font-mono); }
  .vote-row .count { color: var(--neon-cyan); font-weight: 600; }
  .vote-row.top { border-color: var(--neon-cyan); box-shadow: 0 0 10px rgba(0, 243, 255, 0.1); }
  
  .code-box { 
    text-align: center; font-size: 2.5rem; font-weight: 800; letter-spacing: 8px; font-family: var(--font-mono);
    color: #fff; background: rgba(0, 0, 0, 0.6); padding: 16px; border-radius: 12px;
    border: 1px solid var(--neon-cyan); box-shadow: 0 0 20px rgba(0, 243, 255, 0.2), inset 0 0 15px rgba(0, 243, 255, 0.1);
    margin: 16px 0; user-select: all; text-shadow: 0 0 10px var(--neon-cyan);
  }
  
  .players-list { display: grid; gap: 8px; margin-top: 16px; }
  .player-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: rgba(0, 0, 0, 0.4); border-radius: 8px; font-size: 0.95rem; font-family: var(--font-mono); border: 1px solid rgba(148,163,184,0.1); }
  .player-row .tag { font-size: 0.8rem; color: var(--text-muted); }
  .player-row.ready { border-color: var(--neon-green); background: rgba(0, 255, 102, 0.05); }
  .player-row.ready .tag { color: var(--neon-green); }

  .tabs { display: flex; gap: 12px; margin-top: 16px; }
  .tabs button { margin-top: 0; }
  .small { font-size: 0.8rem; color: var(--text-muted); text-align:center; margin-top: 12px; font-family: var(--font-mono); }
  
  .qr-wrap { text-align: center; margin: 16px 0; }
  .qr-wrap img { width: 180px; height: 180px; border-radius: 12px; background: white; padding: 10px; box-shadow: 0 0 20px rgba(0, 243, 255, 0.3); }
  
  .imposter-pill { display:inline-block; background: rgba(255, 0, 60, 0.1); color:var(--neon-red); border: 1px solid var(--neon-red); border-radius: 4px; padding:4px 12px; font-size:0.85rem; margin: 4px; text-transform: uppercase; font-family: var(--font-mono); box-shadow: 0 0 8px rgba(255,0,60,0.2); }
  
  .banner { text-align:center; padding: 20px 16px; border-radius: 12px; margin-top: 12px; font-size: 1.4rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; border: 1px solid; }
  .banner.crew { border-color: var(--neon-green); background: rgba(0, 255, 102, 0.1); color: #fff; text-shadow: 0 0 10px var(--neon-green); box-shadow: 0 0 20px rgba(0, 255, 102, 0.2); }
  .banner.imposter { border-color: var(--neon-red); background: rgba(255, 0, 60, 0.1); color: #fff; text-shadow: 0 0 10px var(--neon-red); box-shadow: 0 0 20px rgba(255, 0, 60, 0.2); }
  .banner.tie { border-color: #fde68a; background: rgba(253, 224, 71, 0.1); color: #fff; text-shadow: 0 0 10px #fde68a; box-shadow: 0 0 20px rgba(253, 224, 71, 0.2); }

  .pass-banner { text-align: center; padding: 32px 20px; background: rgba(0, 243, 255, 0.05); border: 1px dashed var(--neon-cyan); border-radius: 12px; margin-bottom: 16px; }
  .pass-banner .who { font-size: 1.6rem; font-weight: 700; color: #fff; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
  .pass-banner .msg { font-size: 0.95rem; color: var(--text-muted); line-height: 1.5; font-family: var(--font-mono); }

  .recorder { display: flex; align-items: center; gap: 16px; background: rgba(0,0,0,0.4); border: 1px solid rgba(255, 0, 60, 0.3); border-radius: 12px; padding: 16px; margin-top: 12px; }
  .rec-btn { width: 64px; height: 64px; border-radius: 50%; background: rgba(255, 0, 60, 0.1); border: 2px solid var(--neon-red); color: var(--neon-red); font-size: 1.6rem; padding: 0; margin: 0; flex-shrink: 0; cursor: pointer; transition: all 0.2s; box-shadow: 0 0 10px rgba(255, 0, 60, 0.2); }
  .rec-btn:hover { background: rgba(255, 0, 60, 0.2); box-shadow: 0 0 20px rgba(255, 0, 60, 0.4); }
  .rec-btn:active { transform: scale(0.92); }
  .rec-btn.recording { background: var(--neon-red); color: #fff; animation: pulse-red 1s infinite; }
  @keyframes pulse-red { 0%, 100% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0.7); } 50% { box-shadow: 0 0 0 15px rgba(255, 0, 60, 0); } }
  .rec-info { flex: 1; font-size: 0.9rem; color: var(--text-main); line-height: 1.4; font-family: var(--font-mono); }
  .rec-timer { color: var(--neon-red); font-weight: 700; font-size: 1.1rem; }
  .rec-clear { padding: 8px 16px; font-size: 0.85rem; width: auto; margin: 0; background: transparent; border: 1px solid var(--text-muted); color: var(--text-muted); }

  .chat-fab { position: fixed; bottom: 24px; right: 24px; width: 60px; height: 60px; border-radius: 50%; background: var(--bg-card); border: 1px solid var(--neon-cyan); box-shadow: 0 0 20px rgba(0, 243, 255, 0.3); color: var(--neon-cyan); font-size: 1.5rem; padding: 0; margin: 0; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 100; transition: all 0.2s; }
  .chat-fab:hover { transform: scale(1.1); box-shadow: 0 0 30px rgba(0, 243, 255, 0.5); }
  .chat-fab .unread { position: absolute; top: 0; right: 0; background: var(--neon-red); color: #fff; font-size: 0.75rem; font-family: var(--font-mono); min-width: 20px; height: 20px; border-radius: 10px; display: flex; align-items: center; justify-content: center; padding: 0 4px; font-weight: 700; box-shadow: 0 0 10px var(--neon-red); }

  .chat-panel { position: fixed; bottom: 0; left: 0; right: 0; top: 0; background: rgba(5, 5, 15, 0.95); backdrop-filter: blur(10px); z-index: 200; display: none; flex-direction: column; }
  .chat-panel.open { display: flex; }
  .chat-header { padding: 20px; border-bottom: 1px solid rgba(0, 243, 255, 0.3); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.5); }
  .chat-header h3 { font-size: 1.2rem; text-transform: uppercase; letter-spacing: 2px; color: var(--neon-cyan); }
  .chat-close { background: transparent; border: none; color: var(--text-muted); font-size: 2rem; width: auto; padding: 0 8px; margin: 0; cursor: pointer; }
  .chat-close:hover { color: #fff; }
  .chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
  .chat-msg { max-width: 85%; padding: 10px 16px; border-radius: 8px; font-size: 0.95rem; line-height: 1.4; font-family: var(--font-mono); word-wrap: break-word; }
  .chat-msg.mine { align-self: flex-end; background: rgba(0, 243, 255, 0.1); border: 1px solid var(--neon-cyan); color: #fff; border-bottom-right-radius: 0; }
  .chat-msg.other { align-self: flex-start; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-main); border-bottom-left-radius: 0; }
  .chat-msg.system { align-self: center; background: transparent; color: var(--neon-purple); font-size: 0.8rem; font-style: italic; text-align: center; padding: 8px; }
  .chat-msg .sender { font-size: 0.75rem; opacity: 0.8; margin-bottom: 4px; font-weight: 700; text-transform: uppercase; color: var(--neon-purple); }
  .chat-input-row { padding: 16px 20px 30px; border-top: 1px solid rgba(0, 243, 255, 0.3); display: flex; gap: 12px; background: rgba(0,0,0,0.5); }
  .chat-input-row input { flex: 1; margin: 0; }
  .chat-input-row button { width: auto; padding: 12px 24px; margin: 0; }
  .chat-locked { padding: 16px; text-align: center; color: var(--neon-red); font-size: 0.9rem; font-family: var(--font-mono); background: rgba(255, 0, 60, 0.1); border-top: 1px solid rgba(255, 0, 60, 0.3); }

  .menu-fab { position: fixed; bottom: 24px; left: 24px; width: 50px; height: 50px; border-radius: 50%; background: var(--bg-card); border: 1px solid rgba(255, 255, 255, 0.2); color: #fff; font-size: 1.4rem; padding: 0; margin: 0; z-index: 100; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 15px rgba(0,0,0,0.5); transition: all 0.2s; }
  .menu-fab:hover { background: rgba(255,255,255,0.1); border-color: #fff; }
  
  .menu-panel { position: fixed; inset: 0; background: rgba(5, 5, 15, 0.8); backdrop-filter: blur(5px); z-index: 300; display: none; align-items: center; justify-content: center; padding: 20px; }
  .menu-panel.open { display: flex; }
  .menu-card { background: var(--bg-card); border: 1px solid var(--neon-cyan); border-radius: 16px; padding: 28px; max-width: 400px; width: 100%; box-shadow: 0 0 30px rgba(0, 243, 255, 0.2); }
  .menu-card h3 { margin-bottom: 20px; text-align: center; font-size: 1.4rem; text-transform: uppercase; letter-spacing: 2px; color: #fff; text-shadow: 0 0 10px var(--neon-cyan); }
  .menu-card button { margin-top: 12px; }
  .menu-card .small { margin-bottom: 20px; font-size: 0.9rem; }

  .scoreboard { background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(176, 38, 255, 0.3); border-radius: 12px; padding: 16px; margin-top: 16px; box-shadow: inset 0 0 15px rgba(176, 38, 255, 0.05); }
  .scoreboard h4 { font-size: 0.9rem; color: var(--neon-purple); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 2px; text-align: center; }
  .score-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 0.95rem; font-family: var(--font-mono); border-bottom: 1px solid rgba(255,255,255,0.05); }
  .score-row:last-child { border-bottom: none; }
  .score-row .pts { color: var(--neon-cyan); font-weight: 700; text-shadow: 0 0 5px var(--neon-cyan); }
  
  .badge { display:inline-block; background: rgba(0, 243, 255, 0.1); border: 1px solid var(--neon-cyan); color: var(--neon-cyan); padding: 4px 12px; border-radius: 4px; font-size:0.8rem; font-weight:600; text-transform: uppercase; font-family: var(--font-mono); letter-spacing: 1px; }
  .badge.local { background: rgba(0, 255, 102, 0.1); border-color: var(--neon-green); color: var(--neon-green); }

  /* ================= TUTORIAL MODAL ================= */
  .tutorial-modal {
    position: fixed; inset: 0; background: rgba(5, 5, 15, 0.9); backdrop-filter: blur(8px);
    z-index: 500; display: none; align-items: center; justify-content: center; padding: 20px;
  }
  .tutorial-modal.open { display: flex; }
  .tutorial-card {
    background: #0f172a; border: 1px solid var(--neon-purple); border-radius: 16px;
    padding: 24px; max-width: 500px; width: 100%; max-height: 85vh; overflow-y: auto;
    box-shadow: 0 0 30px rgba(176, 38, 255, 0.2);
  }
  .tutorial-card h2 { color: var(--neon-purple); text-shadow: 0 0 10px rgba(176,38,255,0.5); margin-bottom: 16px; }
  .tutorial-step { margin-bottom: 20px; padding-left: 16px; border-left: 2px solid var(--neon-cyan); }
  .tutorial-step h4 { color: #fff; font-size: 1.1rem; margin-bottom: 4px; text-transform: uppercase; }
  .tutorial-step p { color: var(--text-muted); font-size: 0.9rem; line-height: 1.5; font-family: var(--font-mono); }
  .tutorial-card button { border-color: var(--neon-purple); color: var(--neon-purple); background: rgba(176,38,255,0.1); }
  .tutorial-card button:hover { background: rgba(176,38,255,0.2); box-shadow: 0 0 20px rgba(176,38,255,0.4); }

  /* ================= LIVE REACTIONS ================= */
  .reaction-bar {
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    display: none; gap: 8px; background: rgba(15, 23, 42, 0.8); border: 1px solid var(--neon-cyan);
    padding: 8px 12px; border-radius: 30px; box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
    z-index: 150; backdrop-filter: blur(4px);
  }
  .reaction-bar.active { display: flex; }
  .reaction-btn {
    background: transparent; border: none; font-size: 1.5rem; padding: 4px; margin: 0;
    cursor: pointer; transition: transform 0.1s; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;
  }
  .reaction-btn:hover { transform: scale(1.2); }
  .reaction-btn:active { transform: scale(0.9); }

  .floating-reaction {
    position: fixed; bottom: 80px; font-size: 3rem; pointer-events: none; z-index: 9999;
    animation: floatUp 2s ease-out forwards;
  }
  @keyframes floatUp {
    0% { opacity: 1; transform: translateY(0) scale(0.5); }
    20% { transform: translateY(-20px) scale(1.2); }
    100% { opacity: 0; transform: translateY(-150px) scale(1); }
  }
</style>
</head>
<body>
<div class="app">
  <div style="position: absolute; top: 16px; right: 16px; z-index: 10;">
    <button onclick="toggleTutorial()" style="width: 36px; height: 36px; padding: 0; border-radius: 50%; border-color: var(--neon-purple); color: var(--neon-purple); background: transparent; font-size: 1.2rem; margin: 0;">?</button>
  </div>

  <h1>Imposter Protocol <span id="modeBadge" class="badge" style="display:none;"></span></h1>
  <p class="subtitle">Find the traitor. Trust no one.</p>

  <div id="screen-mode" class="screen active">
    <div class="mode-grid">
      <div class="mode-card" onclick="pickMode('online')">
        <div class="icon">🌐</div>
        <div class="title">Network Link</div>
        <div class="desc">Play online with multiple devices. Create a lobby or join a secure channel.</div>
      </div>
      <div class="mode-card" onclick="pickMode('local')">
        <div class="icon">📱</div>
        <div class="title">Local Terminal</div>
        <div class="desc">Pass one device around. Secure role reveal and local voting.</div>
      </div>
    </div>
    <div class="small" id="resumeHint" style="display:none; margin-top:24px;">
      <button class="secondary" onclick="resumeSession()">Resume Active Link</button>
    </div>
  </div>

  <div id="screen-home" class="screen">
    <button class="secondary" onclick="backToMode()" style="width:auto;padding:8px 16px;font-size:0.9rem;margin:0 0 16px;">← Disconnect</button>
    <label for="playerName">Agent Name</label>
    <input type="text" id="playerName" maxlength="20" placeholder="ENTER ID..." autocomplete="off">
    <div class="tabs">
      <button onclick="createGame()">Host Game</button>
      <button class="secondary" onclick="showJoin()">Join Game</button>
    </div>
    <div id="joinBox" style="display:none; margin-top:16px;">
      <label for="joinCode">Lobby Code</label>
      <input type="text" id="joinCode" maxlength="6" placeholder="XK4P2Q"
             style="text-transform:uppercase;letter-spacing:6px;text-align:center;font-size:1.5rem;"
             autocomplete="off">
      <button onclick="joinGame()">Establish Connection</button>
    </div>
    <label for="lang" style="margin-top:24px;">Language / भाषा</label>
    <select id="lang">
      <option value="en">English</option>
      <option value="hi">हिन्दी (Hindi)</option>
    </select>
    <div id="homeError" class="error"></div>
  </div>

  <div id="screen-local-setup" class="screen">
    <button class="secondary" onclick="backToMode()" style="width:auto;padding:8px 16px;font-size:0.9rem;margin:0 0 16px;">← Disconnect</button>
    <h2>Local Terminal</h2>
    <p class="subtitle">Configure agents for this terminal.</p>
    <label for="localLang">Language / भाषा</label>
    <select id="localLang">
      <option value="en">English</option>
      <option value="hi">हिन्दी (Hindi)</option>
    </select>
    <label for="localNumPlayers">Number of Agents (3–10)</label>
    <input type="text" id="localNumPlayers" value="4" inputmode="numeric" style="text-align:center;font-size:1.3rem;">
    <div id="localNameInputs" style="margin-top:16px;"></div>
    <div id="localImposterBox">
      <label for="localNumImposters">Number of Imposters</label>
      <select id="localNumImposters">
        <option value="1">1 Imposter</option>
        <option value="2">2 Imposters</option>
        <option value="3">3 Imposters</option>
      </select>
      <div class="small" id="localImposterNote"></div>
    </div>
    <button onclick="startLocalGame()" style="margin-top:24px;">Initialize Protocol</button>
    <div id="localError" class="error"></div>
  </div>

  <div id="screen-lobby" class="screen">
    <h2>Waiting Room</h2>
    <p class="subtitle">Scan QR or share Lobby Code</p>
    <div class="code-box" id="lobbyCode">------</div>
    <div class="qr-wrap" id="qrWrap"></div>
    <div class="players-list" id="lobbyPlayers"></div>
    <div class="progress" id="lobbyProgress"></div>
    <div id="hostImposterBox" style="display:none; margin-top:16px;">
      <label for="numImposters">Imposter Count</label>
      <select id="numImposters">
        <option value="1">1 Imposter</option>
        <option value="2">2 Imposters</option>
        <option value="3">3 Imposters</option>
      </select>
      <div class="small" id="imposterNote"></div>
    </div>
    <button id="lobbyReadyBtn" onclick="toggleReady()" style="margin-top:24px;">Ready Up</button>
    <button id="lobbyStartBtn" onclick="startGame()" style="display:none; margin-top:16px; border-color: var(--neon-green); color: var(--neon-green); background: rgba(0,255,102,0.1);">Start Protocol</button>
    <div class="error" id="lobbyError"></div>
    <div class="small">Syncing data...</div>
  </div>

  <div id="screen-pass" class="screen">
    <div class="pass-banner">
      <div class="who">Pass Terminal to <span id="passWho">Agent 1</span></div>
      <div class="msg">Ensure no other agents are observing the screen.</div>
    </div>
    <button class="big" onclick="revealRole()">I am <span id="passWhoInline">Agent 1</span> — Show Role</button>
  </div>

  <div id="screen-reveal" class="screen">
    <div class="round-header" id="revealRound">ROLE REVEAL</div>
    <h2>Your Secret Role</h2>
    <p class="subtitle">Memorize this. Do not share.</p>
    <div id="revealCard" class="role-card">
      <div class="role-label" id="revealLabel">—</div>
      <div class="role-word" id="revealWord">—</div>
      <div class="role-hint" id="revealHint"></div>
    </div>
    <button onclick="hostAdvance()" id="revealNextBtn" style="display:none; border-color: var(--neon-green); color: var(--neon-green); background: rgba(0,255,102,0.1);">Proceed to Clues →</button>
    <button class="secondary" onclick="localHideAndContinue()" id="revealLocalBtn" style="display:none;">Hide &amp; Continue</button>
    <div class="progress" id="revealProgress">Waiting for host...</div>
  </div>

  <div id="screen-clue" class="screen">
    <div class="round-header" id="clueRoundHeader">ROUND 1 — CLUES</div>
    <h2>Transmit Clue</h2>
    <p class="subtitle">Provide a clue. Do not say the word.</p>
    <div style="text-align:center; margin-bottom:16px;"><span class="badge" id="cluePlayerName">—</span></div>
    <label for="clueInput">Text Transmission</label>
    <input type="text" id="clueInput" maxlength="80" placeholder="ENTER CLUE..." autocomplete="off">
    <button id="clueSubmitBtn" onclick="submitClue()">Send Text</button>
    <div style="text-align:center;color:var(--neon-cyan);font-size:0.9rem;margin:20px 0 10px; font-family: var(--font-mono);">— OR —</div>
    <div class="recorder" id="recorderBox">
      <button class="rec-btn" id="recBtn" onclick="toggleRecording()">🎙️</button>
      <div class="rec-info" id="recInfo">Tap to record voice transmission.<br>Max 10 seconds.</div>
      <button class="rec-clear" id="recClearBtn" onclick="clearRecording()" style="display:none;">Clear</button>
    </div>
    <audio id="recPlayback" controls style="width:100%;margin-top:12px;display:none; border-radius:8px; border:1px solid var(--neon-cyan);"></audio>
    <button id="voiceSubmitBtn" onclick="submitVoice()" style="display:none; border-color: var(--neon-cyan); color: var(--neon-cyan);">Send Audio</button>
    <div class="error" id="clueError"></div>
    <div class="players-list" id="clueWaitingList"></div>
    <div class="progress" id="clueProgress"></div>
  </div>

  <div id="screen-summary" class="screen">
    <div class="round-header" id="summaryHeader">ROUND 1 COMPLETE</div>
    <h2>Data Log</h2>
    <p class="subtitle">Analyze the clues. Tap ▶ to play audio.</p>
    <div id="summaryList" style="display:grid;gap:10px;margin-top:16px;"></div>
    <button onclick="hostAdvance()" id="summaryNextBtn" style="display:none; border-color: var(--neon-green); color: var(--neon-green); background: rgba(0,255,102,0.1);">Next Round →</button>
    <div class="progress" id="summaryProgress">Waiting for host...</div>
  </div>

  <div id="screen-vote" class="screen">
    <h2>Voting Phase</h2>
    <p class="subtitle">Identify the imposter.</p>
    <div style="text-align:center; margin-bottom:16px;"><span class="badge" id="voteVoterName">—</span></div>
    <label>Select Target</label>
    <div id="voteList" class="vote-list"></div>
    <button id="voteSubmitBtn" onclick="submitVote()" disabled style="border-color: var(--neon-red); color: var(--neon-red); background: rgba(255,0,60,0.1);">Lock Vote</button>
    <div class="error" id="voteError"></div>
    <div class="players-list" id="voteWaitingList"></div>
    <div class="small" id="voteChatHint">💬 Use comms link to discuss.</div>
  </div>

  <div id="screen-result" class="screen">
    <div id="resultBanner" class="banner">—</div>
    <div class="result-detail" id="resultDetail"></div>
    <div id="voteSummaryBox" style="margin-top:20px;">
      <div class="round-header">VOTE TALLY</div>
      <div id="voteSummary" class="vote-summary"></div>
    </div>
    <div id="imposterBox" style="margin-top:20px;text-align:center;"></div>
    <div class="scoreboard" id="scoreboard"></div>
    <div id="resultClues" style="margin-top:20px;"></div>
    <button onclick="playAgain()" id="playAgainBtn" style="display:none; border-color: var(--neon-cyan); color: var(--neon-cyan); background: rgba(0,243,255,0.1);">Restart Protocol</button>
    <button class="secondary" onclick="backToMode()" style="margin-top:16px;">Disconnect</button>
    <div class="progress" id="resultProgress"></div>
  </div>
</div>

<!-- LIVE REACTION BAR -->
<div class="reaction-bar" id="reactionBar">
  <button class="reaction-btn" onclick="sendReaction('😂')">😂</button>
  <button class="reaction-btn" onclick="sendReaction('😱')">😱</button>
  <button class="reaction-btn" onclick="sendReaction('😡')">😡</button>
  <button class="reaction-btn" onclick="sendReaction('🤬')">🤬</button>
  <button class="reaction-btn" onclick="sendReaction('🕵️')">🕵️</button>
</div>

<!-- TUTORIAL MODAL -->
<div class="tutorial-modal" id="tutorialModal">
  <div class="tutorial-card">
    <h2>How to Play</h2>
    <div class="tutorial-step">
      <h4>1. The Roles</h4>
      <p>Everyone receives a secret word except for the <strong>Imposter(s)</strong>. The Imposter gets a vague hint instead. The crew must describe the word without saying it. The Imposter must blend in.</p>
    </div>
    <div class="tutorial-step">
      <h4>2. The Clues</h4>
      <p>Players take turns providing a clue (either by typing or recording a voice note). The clue must relate to the secret word, but be vague enough that the Imposter doesn't guess the word.</p>
    </div>
    <div class="tutorial-step">
      <h4>3. Discussion</h4>
      <p>After two rounds of clues, use the Secure Comms (chat) to discuss. Who sounds suspicious? Who is being too vague?</p>
    </div>
    <div class="tutorial-step">
      <h4>4. Voting</h4>
      <p>Everyone votes for who they think the Imposter is. The player with the most votes is eliminated.</p>
    </div>
    <div class="tutorial-step">
      <h4>5. Win Condition</h4>
      <p><strong>Crew Wins</strong> if they vote out an Imposter. <strong>Imposters Win</strong> if they survive the vote or if a Crew member is voted out.</p>
    </div>
    <button onclick="toggleTutorial()">Understood</button>
  </div>
</div>

<button class="chat-fab" id="chatFab" onclick="toggleChat()" style="display:none;">
  💬<span class="unread" id="chatUnread" style="display:none;">0</span>
</button>

<div class="chat-panel" id="chatPanel">
  <div class="chat-header">
    <h3>Secure Comms</h3>
    <button class="chat-close" onclick="toggleChat()">×</button>
  </div>
  <div class="chat-messages" id="chatMessages"></div>
  <div class="chat-locked" id="chatLocked" style="display:none;">Comms locked during this phase.</div>
  <div class="chat-input-row" id="chatInputRow">
    <input type="text" id="chatInput" maxlength="200" placeholder="Transmit message..." autocomplete="off">
    <button onclick="sendChat()">Send</button>
  </div>
</div>

<button class="menu-fab" id="menuFab" onclick="toggleMenu()" style="display:none;">☰</button>

<div class="menu-panel" id="menuPanel">
  <div class="menu-card">
    <h3>System Menu</h3>
    <div class="small" style="margin-bottom:20px;">
      Lobby: <strong id="menuRoomCode">------</strong><br>
      Agent: <strong id="menuYouName">—</strong>
    </div>
    <button class="secondary" onclick="leaveGame()">🚪 Disconnect</button>
    <button class="danger" id="menuEndBtn" onclick="endGame()" style="display:none;">🛑 Terminate Lobby</button>
    <button class="secondary" onclick="toggleMenu()">Cancel</button>
  </div>
</div>

<script>
const STORAGE_KEY = 'imposter_session_v9';
let session = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
let current = null;
let pollTimer = null;
let selectedVote = null;
let chatOpen = false;
let lastChatCount = 0;
let activeReactionTimers = {};

let mediaRecorder = null;
let recordedChunks = [];
let recordedAudioDataUrl = null;
let recordTimer = null;
let recordSeconds = 0;

let local = null;
let localResult = null;
let localNames = ['', '', '', ''];
let localWordCache = null;

const $ = id => document.getElementById(id);
const show = id => {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  $(id).classList.add('active');
};
const esc = s => String(s ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

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

// ============================================================================
// MODE & TUTORIAL
// ============================================================================
function pickMode(mode) {
  if (mode === 'online') {
    $('modeBadge').style.display = 'none';
    show('screen-home');
  } else {
    $('modeBadge').style.display = 'inline-block';
    $('modeBadge').textContent = 'LOCAL';
    $('modeBadge').className = 'badge local';
    initLocalSetup();
    show('screen-local-setup');
  }
}
function backToMode() {
  stopPolling();
  $('chatFab').style.display = 'none';
  $('menuFab').style.display = 'none';
  $('reactionBar').classList.remove('active');
  $('menuPanel').classList.remove('open');
  $('chatPanel').classList.remove('open');
  $('modeBadge').style.display = 'none';
  $('resumeHint').style.display = session ? 'block' : 'none';
  show('screen-mode');
}
function toggleTutorial() {
  $('tutorialModal').classList.toggle('open');
}

// ============================================================================
// LIVE REACTIONS
// ============================================================================
async function sendReaction(emoji) {
  if (!session || local) return;
  // Optimistic UI
  spawnFloatingEmoji(emoji);
  try { await api('react', { ...session, emoji }); } catch(e) {}
}

function spawnFloatingEmoji(emoji) {
  const el = document.createElement('div');
  el.className = 'floating-reaction';
  el.textContent = emoji;
  // random horizontal position
  el.style.left = (20 + Math.random() * 60) + '%';
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2000);
}

function checkReactions(s) {
  if (!s.reactions || s.reactions.length === 0) return;
  const now = Date.now() / 1000;
  s.reactions.forEach(r => {
    // Use a unique key based on timestamp and name to avoid double-rendering
    const key = r.ts + '_' + r.name;
    if (!activeReactionTimers[key] && (now - r.ts < 2.5)) {
      activeReactionTimers[key] = true;
      spawnFloatingEmoji(r.emoji);
      // Cleanup after 2.5s
      setTimeout(() => { delete activeReactionTimers[key]; }, 2500);
    }
  });
}

// ============================================================================
// ONLINE HOME
// ============================================================================
function showJoin() {
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
    const r = await api('create', { name, lang });
    saveSession({ code: r.code, token: r.token, name });
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
    const r = await api('join', { name, code });
    saveSession({ code: r.code, token: r.token, name });
    applyState(r.state);
  } catch (e) {
    const m = { game_not_found: 'Lobby not found', game_in_progress: 'Lobby already started',
                game_full: 'Lobby full (10 max)', name_taken: 'Name taken in this lobby' };
    err(m[e.message] || e.message);
  }
}
async function resumeSession() {
  if (!session) return;
  try { applyState(await api('state', session)); }
  catch (e) { saveSession(null); $('resumeHint').style.display = 'none'; alert('Lobby expired.'); }
}

// ============================================================================
// ONLINE POLLING
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

function applyState(s) {
  current = s;
  $('modeBadge').style.display = 'none';
  const p = s.phase;
  if (p === 'lobby')        renderLobby(s);
  else if (p === 'reveal')  renderRevealOnline(s);
  else if (p === 'clue')    renderClue(s);
  else if (p === 'summary') renderSummary(s);
  else if (p === 'vote')    renderVoteOnline(s);
  else if (p === 'result')  renderResult(s);
  
  updateChatBadge(s);
  checkReactions(s); // LIVE REACTIONS
  
  if (chatOpen) renderChat(s);
  $('menuFab').style.display = 'flex';
  $('reactionBar').classList.add('active'); // SHOW REACTIONS
  
  $('menuRoomCode').textContent = s.code;
  $('menuYouName').textContent = s.you ? s.you.name : '—';
  $('menuEndBtn').style.display = s.is_host ? 'block' : 'none';
  startPolling();
}

// ============================================================================
// ONLINE LOBBY
// ============================================================================
function renderLobby(s) {
  show('screen-lobby');
  $('lobbyCode').textContent = s.code;
  const joinUrl = location.origin + '/join?code=' + s.code;
  $('qrWrap').innerHTML = `<img alt="QR" src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&color=0f172a&bgcolor=ffffff&data=${encodeURIComponent(joinUrl)}">`;
  const list = $('lobbyPlayers');
  list.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'player-row' + (p.ready ? ' ready' : '');
    const mine = p.name === s.you.name;
    const kick = s.is_host && !mine && s.phase === 'lobby'
      ? ` <button class="rec-clear" style="padding:4px 10px;font-size:0.75rem;border-color:var(--neon-red);color:var(--neon-red);" onclick="kickPlayer('${esc(p.name)}')">✕</button>` : '';
    d.innerHTML = `<span>${esc(p.name)}${mine ? ' (YOU)' : ''}${p.name === s.host_name ? ' 👑' : ''}</span>
                   <span class="tag">${p.ready ? '✅ READY' : '⏳ WAIT'}${kick}</span>`;
    list.appendChild(d);
  });
  $('lobbyProgress').textContent = `AGENTS: ${s.players.length} / 10 — MIN 3`;
  $('lobbyReadyBtn').textContent = s.you.ready ? 'Stand Down' : "Ready Up";
  $('lobbyReadyBtn').className = s.you.ready ? 'secondary' : '';
  const n = s.players.length;
  const maxK = Math.max(1, Math.floor((n - 1) / 2));
  const box = $('hostImposterBox');
  if (s.is_host) {
    box.style.display = 'block';
    const sel = $('numImposters');
    sel.innerHTML = '';
    for (let k = 1; k <= Math.min(3, maxK); k++) {
      const opt = document.createElement('option');
      opt.value = k; opt.textContent = k + ' Imposter' + (k > 1 ? 's' : '');
      sel.appendChild(opt);
    }
    sel.value = String(Math.min(s.imposter_count, Math.min(3, maxK)));
    $('imposterNote').textContent = `Max ${maxK} with ${n} agents.`;
  } else box.style.display = 'none';
  if (s.is_host) {
    $('lobbyStartBtn').style.display = 'block';
    const allReady = s.players.every(p => p.ready);
    $('lobbyStartBtn').disabled = !(n >= 3 && allReady);
    $('lobbyStartBtn').textContent = n < 3
      ? `Need ${3 - n} more agents`
      : (allReady ? '▶ START PROTOCOL' : 'Waiting for ready status');
  } else $('lobbyStartBtn').style.display = 'none';
  $('chatFab').style.display = 'flex';
}
async function toggleReady() {
  if (!session) return;
  try { applyState(await api('ready', { ...session, ready: !current.you.ready })); }
  catch (e) { $('lobbyError').textContent = e.message; }
}
async function startGame() {
  if (!session) return;
  $('lobbyError').textContent = '';
  const k = parseInt($('numImposters').value, 10) || 1;
  try { applyState(await api('start', { ...session, num_imposters: k })); }
  catch (e) { $('lobbyError').textContent = e.message; }
}
async function kickPlayer(name) {
  if (!session) return;
  if (!confirm(`Remove ${name}?`)) return;
  try { applyState(await api('kick', { ...session, target: name })); }
  catch (e) { alert(e.message); }
}

// ============================================================================
// ONLINE SCREENS
// ============================================================================
function renderRevealOnline(s) {
  show('screen-reveal');
  const card = $('revealCard');
  const isImp = !!s.you_are_imposter;
  card.className = 'role-card ' + (isImp ? 'imposter' : 'crew');
  $('revealLabel').textContent = isImp ? 'YOU ARE THE IMPOSTER' : 'YOUR SECRET WORD';
  $('revealWord').textContent = isImp ? '🤫' : (s.your_word || '—');
  $('revealHint').textContent = isImp
    ? 'HINT: ' + (s.your_hint || '') + '\nBLEND IN. DO NOT GET CAUGHT.'
    : 'DESCRIBE IT WITHOUT SAYING THE WORD.';
  $('revealRound').textContent = `ROLE REVEAL — ${s.imposter_count} IMPOSTER${s.imposter_count>1?'S':''} DETECTED`;
  $('revealNextBtn').style.display = s.is_host ? 'block' : 'none';
  $('revealLocalBtn').style.display = 'none';
  $('chatFab').style.display = 'flex';
}

function renderClue(s) {
  show('screen-clue');
  $('clueRoundHeader').textContent = `ROUND ${s.round} OF 2 — CLUES`;
  $('cluePlayerName').textContent = s.you ? s.you.name : '—';
  $('cluePlayerName').className = 'badge';
  
  // FIX: Explicitly clear the text field if the player has not submitted a clue yet.
  // This guarantees round 2 inputs are blank.
  const submitted = s.you.clue || s.you.clue_audio;
  if (!submitted) {
    if (!$('clueInput').disabled) {
       // only clear if it's currently active, to avoid wiping what they are typing on a poll tick
    } else {
       $('clueInput').value = ''; // was disabled, now active
    }
  }
  
  $('clueInput').disabled = !!submitted;
  $('clueSubmitBtn').disabled = !!submitted;
  $('clueSubmitBtn').textContent = submitted ? 'Transmitted ✅' : 'Send Text';
  if (submitted && s.you.clue) $('clueInput').value = s.you.clue;
  
  $('voiceSubmitBtn').style.display = recordedAudioDataUrl && !submitted ? 'block' : 'none';
  $('voiceSubmitBtn').disabled = !!submitted;
  const wl = $('clueWaitingList');
  wl.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'player-row';
    d.innerHTML = `<span>${esc(p.name)}</span><span class="tag">${p.has_clue ? '✅ SENT' : '✏️ INPUTTING...'}</span>`;
    wl.appendChild(d);
  });
  const done = s.players.filter(p => p.has_clue).length;
  $('clueProgress').textContent = `STATUS: ${done} / ${s.players.length} TRANSMITTED`;
  $('chatFab').style.display = submitted ? 'flex' : 'none';
  if (chatOpen && submitted) renderChat(s);
}

function renderSummary(s) {
  show('screen-summary');
  $('summaryHeader').textContent = `ROUND ${s.round} COMPLETE`;
  const list = $('summaryList');
  list.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'clue-item' + (p.name === s.you.name ? ' mine' : '');
    if (p.clue) d.innerHTML = `<span class="name">${esc(p.name)}:</span> ${esc(p.clue)}`;
    else if (p.clue_audio) d.innerHTML = `<span class="name">${esc(p.name)}:</span> 🎙️ VOICE
      <button class="play-btn" onclick="playAudio('${p.clue_audio}')">▶ Play</button>`;
    else d.innerHTML = `<span class="name">${esc(p.name)}:</span> —`;
    list.appendChild(d);
  });
  const btn = $('summaryNextBtn');
  if (s.is_host) {
    btn.style.display = 'block';
    btn.textContent = s.round === 1 ? 'Start Round 2 →' : 'Proceed to Voting →';
  } else btn.style.display = 'none';
  $('chatFab').style.display = 'flex';
}

function renderVoteOnline(s) {
  show('screen-vote');
  $('voteVoterName').textContent = s.you ? s.you.name : '—';
  const voted = s.you.has_voted;
  if (voted) selectedVote = null;
  $('voteSubmitBtn').disabled = !selectedVote || voted;
  $('voteSubmitBtn').textContent = voted ? 'VOTE LOCKED ✅' : 'LOCK VOTE';
  const list = $('voteList');
  list.innerHTML = '';
  s.players.forEach(p => {
    const btn = document.createElement('button');
    btn.className = 'vote-btn' + (p.name === selectedVote ? ' selected' : '') + (voted ? ' done' : '');
    btn.textContent = p.name + (p.name === s.you.name ? ' (YOU)' : '');
    if (p.name === s.you.name) btn.disabled = true;
    else if (!voted) {
      btn.onclick = () => {
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
    d.className = 'player-row';
    d.innerHTML = `<span>${esc(p.name)}</span><span class="tag">${p.has_voted ? '✅ VOTED' : '⏳ WAITING'}</span>`;
    wl.appendChild(d);
  });
  $('voteChatHint').style.display = 'block';
  $('chatFab').style.display = 'flex';
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
  if (s.vote_tie) detail += `VOTE TIED.<br>`;
  else if (s.voted_out_name) detail += `VOTED OUT: <strong>${esc(s.voted_out_name)}</strong><br>`;
  detail += `IMPOSTER${imposterNames.length>1?'S':''}: ` +
            imposterNames.map(n => `<strong>${esc(n)}</strong>`).join(', ') +
            `<br>WORD: <strong>${esc(s.secret_word)}</strong>`;
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
    `<div class="round-header">IMPOSTER${imposterNames.length>1?'S':''}</div>` +
    imposterNames.map(n => `<span class="imposter-pill">🕵️ ${esc(n)}</span>`).join(' ');
  const scores = s.scores || {};
  const sortedScores = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  const sb = $('scoreboard');
  if (sortedScores.length) {
    sb.innerHTML = '<h4>SESSION SCORES</h4>' +
      sortedScores.map(([n, v]) => `<div class="score-row"><span>${esc(n)}</span><span class="pts">${v} WIN${v===1?'':'S'}</span></div>`).join('');
  } else sb.innerHTML = '';
  const rc = $('resultClues');
  rc.innerHTML = '<div class="round-header">ROUND 2 DATA</div>';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'clue-item' + (p.name === s.you.name ? ' mine' : '');
    if (p.clue) d.innerHTML = `<span class="name">${esc(p.name)}:</span> ${esc(p.clue)}`;
    else if (p.clue_audio) d.innerHTML = `<span class="name">${esc(p.name)}:</span> 🎙️ VOICE
      <button class="play-btn" onclick="playAudio('${p.clue_audio}')">▶ Play</button>`;
    else d.innerHTML = `<span class="name">${esc(p.name)}:</span> —`;
    rc.appendChild(d);
  });
  $('playAgainBtn').style.display = s.is_host ? 'block' : 'none';
  $('resultProgress').textContent = s.is_host ? '' : 'WAITING FOR HOST...';
  $('chatFab').style.display = 'flex';
}

async function playAgain() {
  if (local) {
    const scores = local.players.map(p => p.score || 0);
    const names = local.players.map(p => p.name);
    localNames = names;
    startLocalGameWithScores(scores);
    return;
  }
  if (!session) return;
  try { applyState(await api('reset', session)); }
  catch (e) { alert(e.message); }
}

async function hostAdvance() {
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
  try { applyState(await api('clue', { ...session, text })); }
  catch (e) {
    const m = { contains_word: '❌ CLUE CONTAINS SECRET WORD!' };
    $('clueError').textContent = m[e.message] || e.message;
  }
}
async function submitVoice() {
  if (local) return localSubmitClue('voice');
  if (!session || !recordedAudioDataUrl) return;
  $('clueError').textContent = '';
  try {
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
    const r = await api('vote', { ...session, target: selectedVote });
    selectedVote = null;
    applyState(r);
  } catch (e) { $('voteError').textContent = e.message; }
}

function playAudio(dataUrl) {
  const a = new Audio(dataUrl);
  a.play().catch(() => alert('Tap again to play'));
}

// ============================================================================
// LOCAL SETUP
// ============================================================================
function initLocalSetup() {
  $('localError').textContent = '';
  $('localNumPlayers').value = '4';
  $('localLang').value = 'en';
  $('localNumImposters').value = '1';
  localNames = ['', '', '', ''];
  renderLocalNameInputs();
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
    inp.type = 'text';
    inp.maxLength = 20;
    inp.value = localNames[i] || `Agent ${i + 1}`;
    inp.placeholder = `ENTER NAME...`;
    inp.oninput = () => { localNames[i] = inp.value; };
    localNames[i] = inp.value;
    box.appendChild(label);
    box.appendChild(inp);
  }
  const maxK = Math.max(1, Math.floor((n - 1) / 2));
  const sel = $('localNumImposters');
  sel.innerHTML = '';
  for (let k = 1; k <= Math.min(3, maxK); k++) {
    const opt = document.createElement('option');
    opt.value = k; opt.textContent = k + ' Imposter' + (k > 1 ? 's' : '');
    sel.appendChild(opt);
  }
  sel.value = String(Math.min(parseInt(sel.value, 10) || 1, Math.min(3, maxK)));
  $('localImposterNote').textContent = `Max ${maxK} with ${n} agents.`;
}

$('localNumPlayers').addEventListener('input', renderLocalNameInputs);

async function ensureWordCache() {
  if (localWordCache) return localWordCache;
  try {
    const r = await apiGet('words');
    localWordCache = r.words;
  } catch (e) {
    localWordCache = [
      {"en": {"word": "Pizza", "imposter_hint": "Round food cut into slices."},
       "hi": {"word": "पिज़्ज़ा", "imposter_hint": "गोल खाना।"}},
      {"en": {"word": "Car", "imposter_hint": "Four wheels."},
       "hi": {"word": "कार", "imposter_hint": "चार पहिये।"}},
      {"en": {"word": "Dog", "imposter_hint": "A loyal pet."},
       "hi": {"word": "कुत्ता", "imposter_hint": "वफादार पालतू।"}},
    ];
  }
  return localWordCache;
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
  const k = parseInt($('localNumImposters').value, 10) || 1;
  const maxK = Math.max(1, Math.floor((n - 1) / 2));
  const numImposters = Math.max(1, Math.min(k, maxK));

  let bank;
  try { bank = await ensureWordCache(); }
  catch (e) { $('localError').textContent = 'Data link failed.'; return; }

  const entry = bank[Math.floor(Math.random() * bank.length)][lang];
  const imposterIndices = new Set();
  while (imposterIndices.size < numImposters) {
    imposterIndices.add(Math.floor(Math.random() * n));
  }

  local = {
    lang,
    word: entry.word,
    imposterHint: entry.imposter_hint,
    imposterIndices: [...imposterIndices].sort((a,b)=>a-b),
    numImposters,
    players: names.map((name, i) => ({
      name,
      isImposter: imposterIndices.has(i),
      clue: '', clueAudio: null, vote: null, score: 0,
    })),
    round: 1,
    phase: 'pass',
    passIndex: 0,
    clueIndex: 0,
    voteIndex: 0,
    selectedVote: null,
  };
  localResult = null;
  localRenderPass();
}

// ============================================================================
// LOCAL PASS + REVEAL
// ============================================================================
function localRenderPass() {
  if (!local) return;
  const p = local.players[local.passIndex];
  $('passWho').textContent = p.name;
  $('passWhoInline').textContent = p.name;
  show('screen-pass');
}

function revealRole() {
  if (!local) return;
  const p = local.players[local.passIndex];
  const isImp = p.isImposter;
  const card = $('revealCard');
  card.className = 'role-card ' + (isImp ? 'imposter' : 'crew');
  $('revealLabel').textContent = isImp ? 'YOU ARE THE IMPOSTER' : 'YOUR SECRET WORD';
  $('revealWord').textContent = isImp ? '🤫' : (local.word || '—');
  $('revealHint').textContent = isImp
    ? 'HINT: ' + (local.imposterHint || '') + '\nBLEND IN. DO NOT GET CAUGHT.'
    : 'DESCRIBE IT WITHOUT SAYING THE WORD.';
  $('revealRound').textContent = `ROLE REVEAL — ${local.numImposters} IMPOSTER${local.numImposters>1?'S':''} DETECTED`;
  $('revealNextBtn').style.display = 'none';
  $('revealLocalBtn').style.display = 'block';
  $('revealProgress').textContent = `AGENT ${local.passIndex + 1} / ${local.players.length}`;
  show('screen-reveal');
}

function localHideAndContinue() {
  if (!local) return;
  local.passIndex++;
  if (local.passIndex < local.players.length) {
    localRenderPass();
  } else {
    local.phase = 'clue';
    local.round = 1;
    local.clueIndex = 0;
    localRenderClue();
  }
}

// ============================================================================
// LOCAL CLUES
// ============================================================================
function localRenderClue() {
  if (!local) return;
  clearRecording();
  $('clueRoundHeader').textContent = `ROUND ${local.round} OF 2 — CLUES`;
  const p = local.players[local.clueIndex];
  if (!p) return;
  $('cluePlayerName').textContent = p.name;
  $('cluePlayerName').className = 'badge local';
  
  // FIX: Always blank the input when advancing to the next player
  $('clueInput').value = '';
  
  $('clueInput').disabled = false;
  $('clueSubmitBtn').disabled = false;
  $('clueSubmitBtn').textContent = 'Send Text';
  $('voiceSubmitBtn').style.display = 'none';
  $('clueError').textContent = '';

  const wl = $('clueWaitingList');
  wl.innerHTML = '';
  local.players.forEach((pl, i) => {
    const d = document.createElement('div');
    d.className = 'player-row';
    let status = '⏳ WAITING';
    if (pl.clue || pl.clueAudio) status = '✅ SENT';
    else if (i === local.clueIndex) status = '✏️ YOUR TURN';
    d.innerHTML = `<span>${esc(pl.name)}</span><span class="tag">${status}</span>`;
    wl.appendChild(d);
  });
  const done = local.players.filter(pl => pl.clue || pl.clueAudio).length;
  $('clueProgress').textContent = `STATUS: ${done} / ${local.players.length} TRANSMITTED`;
  $('chatFab').style.display = 'none';
  show('screen-clue');
  setTimeout(() => $('clueInput').focus(), 100);
}

function localSubmitClue(kind) {
  if (!local) return;
  const p = local.players[local.clueIndex];
  if (!p) return;
  if (p.clue || p.clueAudio) return;

  $('clueError').textContent = '';

  if (kind === 'text') {
    const text = ($('clueInput').value || '').trim();
    if (!text) { $('clueError').textContent = 'ENTER A CLUE.'; return; }
    const w = (local.word || '').toLowerCase();
    if (w && text.toLowerCase().includes(w)) {
      $('clueError').textContent = '❌ CLUE CONTAINS SECRET WORD!';
      return;
    }
    p.clue = text;
    p.clueAudio = null;
  } else {
    if (!recordedAudioDataUrl) {
      $('clueError').textContent = 'NO AUDIO DETECTED.';
      return;
    }
    p.clue = '';
    p.clueAudio = recordedAudioDataUrl;
    clearRecording();
  }

  local.clueIndex++;
  if (local.clueIndex < local.players.length) {
    localRenderClue();
  } else {
    local.phase = 'summary';
    localRenderSummary();
  }
}

// ============================================================================
// LOCAL SUMMARY
// ============================================================================
function localRenderSummary() {
  if (!local) return;
  $('summaryHeader').textContent = `ROUND ${local.round} COMPLETE`;
  const list = $('summaryList');
  list.innerHTML = '';
  local.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'clue-item';
    if (p.clue) d.innerHTML = `<span class="name">${esc(p.name)}:</span> ${esc(p.clue)}`;
    else if (p.clueAudio) d.innerHTML = `<span class="name">${esc(p.name)}:</span> 🎙️ VOICE
      <button class="play-btn" onclick="playAudio('${p.clueAudio}')">▶ Play</button>`;
    else d.innerHTML = `<span class="name">${esc(p.name)}:</span> —`;
    list.appendChild(d);
  });
  $('summaryNextBtn').style.display = 'block';
  $('summaryNextBtn').textContent = local.round === 1 ? 'Start Round 2 →' : 'Proceed to Voting →';
  show('screen-summary');
  $('chatFab').style.display = 'none';
}

function localAdvance() {
  if (!local) return;
  if (local.phase === 'summary') {
    if (local.round === 1) {
      local.round = 2;
      local.clueIndex = 0;
      local.players.forEach(p => { p.clue = ''; p.clueAudio = null; });
      local.phase = 'clue';
      localRenderClue();
    } else {
      local.phase = 'vote';
      local.voteIndex = 0;
      local.players.forEach(p => { p.vote = null; });
      localRenderVote();
    }
  }
}

// ============================================================================
// LOCAL VOTE
// ============================================================================
function localRenderVote() {
  if (!local) return;
  const voter = local.players[local.voteIndex];
  if (!voter) return;
  $('voteVoterName').textContent = voter.name;
  $('voteVoterName').className = 'badge local';
  local.selectedVote = null;
  $('voteSubmitBtn').disabled = true;
  $('voteSubmitBtn').textContent = 'LOCK VOTE';
  $('voteError').textContent = '';
  const list = $('voteList');
  list.innerHTML = '';
  local.players.forEach((p, i) => {
    if (i === local.voteIndex) return;
    const btn = document.createElement('button');
    btn.className = 'vote-btn';
    btn.textContent = p.name;
    btn.onclick = () => {
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
    d.className = 'player-row';
    let status = '⏳ WAITING';
    if (p.vote) status = '✅ VOTED';
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
  local.players[local.voteIndex].vote = local.selectedVote;
  local.voteIndex++;
  if (local.voteIndex < local.players.length) {
    localRenderVote();
  } else {
    localResolveVotes();
  }
}

function localResolveVotes() {
  const counts = {};
  local.players.forEach(p => counts[p.name] = 0);
  local.players.forEach(p => { if (p.vote in counts) counts[p.vote]++; });
  const top = Math.max(...Object.values(counts));
  const leaders = Object.entries(counts).filter(([, c]) => c === top && c > 0).map(([n]) => n);
  const tie = leaders.length > 1;
  const votedOut = tie ? null : leaders[0];
  const imposterNames = local.players.filter(p => p.isImposter).map(p => p.name);
  let banner;
  if (tie) banner = 'imposter';
  else if (imposterNames.includes(votedOut)) banner = imposterNames.length === 1 ? 'crew' : 'imposter';
  else banner = 'imposter';

  if (banner === 'crew') local.players.forEach(p => { if (!p.isImposter) p.score++; });
  else local.players.forEach(p => { if (p.isImposter) p.score++; });

  localResult = { counts, tie, votedOut, imposterNames, banner };
  localRenderResult();
}

function localRenderResult() {
  if (!local || !localResult) return;
  const { counts, tie, votedOut, imposterNames, banner } = localResult;
  $('resultBanner').textContent =
    banner === 'crew' ? '🎉 CREW WINS!' :
    banner === 'imposter' ? '😈 IMPOSTERS WIN!' : '🤝 TIE';
  $('resultBanner').className = 'banner ' + banner;
  let detail = '';
  if (tie) detail += 'VOTE TIED.<br>';
  else if (votedOut) detail += `VOTED OUT: <strong>${esc(votedOut)}</strong><br>`;
  detail += `IMPOSTER${imposterNames.length>1?'S':''}: ` +
    imposterNames.map(n => `<strong>${esc(n)}</strong>`).join(', ') +
    `<br>WORD: <strong>${esc(local.word)}</strong>`;
  $('resultDetail').innerHTML = detail;
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const topCount = entries.length ? entries[0][1] : 0;
  $('voteSummary').innerHTML = entries.map(([n, c]) =>
    `<div class="vote-row ${c === topCount && c > 0 && !tie ? 'top' : ''}">
       <span>${esc(n)}${imposterNames.includes(n) ? ' 🤫' : ''}</span>
       <span class="count">${c} VOTE${c === 1 ? '' : 'S'}</span></div>`
  ).join('');
  $('imposterBox').innerHTML =
    `<div class="round-header">IMPOSTER${imposterNames.length>1?'S':''}</div>` +
    imposterNames.map(n => `<span class="imposter-pill">🕵️ ${esc(n)}</span>`).join(' ');
  const sorted = [...local.players].sort((a, b) => b.score - a.score);
  $('scoreboard').innerHTML = '<h4>SESSION SCORES</h4>' +
    sorted.map(p => `<div class="score-row"><span>${esc(p.name)}</span><span class="pts">${p.score} WIN${p.score===1?'':'S'}</span></div>`).join('');
  $('resultClues').innerHTML = '<div class="round-header">ROUND 2 DATA</div>' +
    local.players.map(p =>
      p.clue ? `<div class="clue-item"><span class="name">${esc(p.name)}:</span> ${esc(p.clue)}</div>` :
      p.clueAudio ? `<div class="clue-item"><span class="name">${esc(p.name)}:</span> 🎙️ VOICE
        <button class="play-btn" onclick="playAudio('${p.clueAudio}')">▶ Play</button></div>` :
      `<div class="clue-item"><span class="name">${esc(p.name)}:</span> —</div>`
    ).join('');
  $('playAgainBtn').style.display = 'block';
  $('resultProgress').textContent = '';
  show('screen-result');
}

function startLocalGameWithScores(scores) {
  const n = local.players.length;
  const lang = local.lang;
  const numImposters = local.numImposters;
  const bank = localWordCache || [];
  const entry = bank[Math.floor(Math.random() * bank.length)][lang];
  const imposterIndices = new Set();
  while (imposterIndices.size < numImposters) {
    imposterIndices.add(Math.floor(Math.random() * n));
  }
  const names = local.players.map(p => p.name);
  local = {
    lang,
    word: entry.word,
    imposterHint: entry.imposter_hint,
    imposterIndices: [...imposterIndices],
    numImposters,
    players: names.map((name, i) => ({
      name,
      isImposter: imposterIndices.has(i),
      clue: '', clueAudio: null, vote: null,
      score: scores[i] || 0,
    })),
    round: 1, phase: 'pass',
    passIndex: 0, clueIndex: 0, voteIndex: 0,
    selectedVote: null,
  };
  localResult = null;
  localRenderPass();
}

// ============================================================================
// RECORDER
// ============================================================================
function pickMimeType() {
  if (!window.MediaRecorder) return '';
  const candidates = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg'];
  for (const t of candidates) {
    if (MediaRecorder.isTypeSupported(t)) return t;
  }
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
  $('recInfo').innerHTML = 'Tap to record voice transmission.<br>Max 10 seconds.';
}

// ============================================================================
// CHAT
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
  const locked = s.phase === 'clue' && !(s.you && (s.you.clue || s.you.clue_audio));
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
    const m = {
      chat_locked: 'COMMS LOCKED.',
      chat_blocked_during_clue: 'SUBMIT CLUE FIRST!',
      empty: 'TYPE MESSAGE.',
    };
    alert(m[e.message] || e.message);
  }
}

// ============================================================================
// MENU
// ============================================================================
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
    print(f"[BOOT] port={PORT} RENDER={os.environ.get('RENDER', 'no')}")
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
