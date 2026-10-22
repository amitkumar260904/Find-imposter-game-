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
import base64
import signal
import sys

PORT = int(os.environ.get("PORT", 8000))
START_TIME = time.time()

# ===========================================================================
# WORD BANK (your original 50 entries — unchanged)
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
# STATE
# ===========================================================================
GAMES = {}
GAMES_LOCK = threading.Lock()
GAME_TTL_SECONDS = 3 * 60 * 60
MAX_VOICE_BYTES = 60_000          # ~10s webm/opus mono ≈ 20-40KB
MAX_CLIP_COUNT = 4                # per player per game
MAX_CHAT_LEN = 200
MAX_CHAT_HISTORY = 200

# ===========================================================================
# HELPERS
# ===========================================================================
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
        "score": 0, "connected": True,
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
        "code": game["code"],
        "phase": game["phase"],
        "lang": game["lang"],
        "round": game["round"],
        "players": players,
        "is_host": bool(me and me["token"] == game["host_token"]),
        "host_name": host["name"] if host else "",
        "imposter_count": game["imposter_count"],
        "chat": game.get("chat", [])[-60:],           # last 60 messages
        "chat_open": game.get("chat_open", True),
        "you": None,
    }
    if me:
        state["you"] = {
            "name": me["name"],
            "ready": me["ready"],
            "clue": me["clue"],
            "clue_audio": me.get("clue_audio"),
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

    # ---------------------------------------------------------------- util
    def _with_game(self, payload, fn):
        if not payload:
            return self._json(400, {"error": "bad request"})
        code = (payload.get("code") or "").upper().strip()
        token = payload.get("token") or ""
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
        text = (text or "").strip()[:MAX_CHAT_LEN]
        if not text:
            return
        entry = {"ts": int(time.time() * 1000), "name": sender_name, "text": text}
        game.setdefault("chat", []).append(entry)
        game["chat"] = game["chat"][-MAX_CHAT_HISTORY:]

    # ------------------------------------------------------------- create
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
                "code": code, "lang": lang, "phase": "lobby",
                "host_token": token,
                "players": [_make_player(token, name)],
                "word": "", "imposter_hint": "", "imposter_index": 0,
                "imposter_count": 1, "imposter_names": [],
                "result_banner": "", "vote_counts": {},
                "voted_out_name": None, "vote_tie": False,
                "round": 1, "chat": [], "chat_open": True,
                "created_at": time.time(), "last_activity": time.time(),
            }
            game = GAMES[code]
        self._json(200, {"code": code, "token": token, "state": _public_state(game, token)})

    # --------------------------------------------------------------- join
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

    # -------------------------------------------------------------- state
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

    # -------------------------------------------------------------- start
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
            self._add_chat(game, "System", "Game started! Check your secret role.")
            self._json(200, _public_state(game, token))

        self._with_game(payload, run)

    # --------------------------------------------------------------- clue
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
            # reject clue that contains the actual word (basic anti-cheat)
            if game["word"] and game["word"].lower() in text.lower():
                return self._json(400, {"error": "contains_word"})
            me["clue"] = text
            if all(p["clue"] or p.get("clue_audio") for p in game["players"]):
                game["phase"] = "summary"
            self._json(200, _public_state(game, token))

        self._with_game(payload, run)

    # -------------------------------------------------------------- audio
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
            me["clue"] = ""   # voice replaces text
            if all(p["clue"] or p.get("clue_audio") for p in game["players"]):
                game["phase"] = "summary"
            self._json(200, _public_state(game, token))

        self._with_game(payload, run)

    # ------------------------------------------------------------ advance
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
            self._json(200, _public_state(game, token))

        self._with_game(payload, run)

    # --------------------------------------------------------------- vote
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
                crew_count = len(game["players"]) - len(imposter_names)
                if is_tie:
                    game["result_banner"] = "imposter"
                elif top_name in imposter_names:
                    if len(imposter_names) == 1:
                        game["result_banner"] = "crew"
                    else:
                        game["result_banner"] = "imposter"
                else:
                    game["result_banner"] = "imposter"
                # scoring
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

    # -------------------------------------------------------------- reset
    def _handle_reset(self):
        """Back to lobby, keep same players and scores."""
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
        """Delete the game entirely. Host only. All other players lose the room."""
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

    # --------------------------------------------------------------- chat
    def _handle_chat(self):
        payload = self._read_json() or {}
        text = payload.get("text") or ""

        def run(game, token, payload):
            if not game.get("chat_open", True):
                return self._json(403, {"error": "chat_locked"})
            me = self._find_player(game, token)
            if not text.strip():
                return self._json(400, {"error": "empty"})
            if len(text) > MAX_CHAT_LEN:
                text = text[:MAX_CHAT_LEN]
            # only allow chat in safe phases (not mid-clue-submission)
            if game["phase"] == "clue" and not (me["clue"] or me.get("clue_audio")):
                return self._json(403, {"error": "chat_blocked_during_clue"})
            self._add_chat(game, me["name"], text)
            self._json(200, _public_state(game, token))

        self._with_game(payload, run)

    # -------------------------------------------------------------- leave
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
            # host transfer
            if me["token"] == game["host_token"] and game["players"]:
                game["host_token"] = game["players"][0]["token"]
                self._add_chat(game, "System",
                    f"{game['players'][0]['name']} is now the host")
            # empty game → delete
            if not game["players"]:
                del GAMES[code]
            # if enough players left → auto-reset to lobby
            elif len(game["players"]) < 3 and game["phase"] not in ("lobby",):
                game["phase"] = "lobby"
                for p in game["players"]:
                    p["ready"] = False
                self._add_chat(game, "System",
                    "Not enough players — game reset to lobby")
        self._json(200, {"ok": True})

    # --------------------------------------------------------------- kick
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
# HTML (SPA)
# ===========================================================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Imposter Word — Multiplayer</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%);
    color: #f8fafc; min-height: 100vh;
    display: flex; align-items: flex-start; justify-content: center; padding: 16px;
    padding-bottom: 90px;
  }
  .app {
    width: 100%; max-width: 540px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 20px; padding: 24px 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5); backdrop-filter: blur(8px);
    margin: auto;
  }
  h1 { font-size: 1.5rem; text-align: center; margin-bottom: 4px; }
  h2 { font-size: 1.15rem; text-align: center; margin-bottom: 6px; }
  .subtitle { text-align: center; color: #94a3b8; font-size: 0.88rem; margin-bottom: 16px; line-height: 1.45; }
  .screen { display: none; }
  .screen.active { display: block; animation: fade 0.25s ease; }
  @keyframes fade { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
  label { display: block; font-size: 0.85rem; color: #cbd5e1; margin-bottom: 6px; margin-top: 14px; }
  select, input[type="text"] {
    width: 100%; padding: 12px; border-radius: 10px;
    border: 1px solid #475569; background: #1e293b; color: #f8fafc; font-size: 1rem;
  }
  input[type="text"]:focus, select:focus { outline: 2px solid #6366f1; }
  button {
    width: 100%; padding: 14px; margin-top: 14px; border: none;
    border-radius: 12px; background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white; font-size: 1rem; font-weight: 600; cursor: pointer;
    transition: transform 0.1s, opacity 0.2s;
  }
  button:hover { transform: translateY(-1px); opacity: 0.95; }
  button:active { transform: translateY(1px); }
  button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
  button.secondary { background: #334155; }
  button.danger { background: #b91c1c; }
  .role-card { text-align: center; padding: 28px 16px; border-radius: 16px; margin-top: 14px; }
  .role-card.crew { background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34,197,94,0.4); }
  .role-card.imposter { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239,68,68,0.4); }
  .role-label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; }
  .role-word { font-size: 1.8rem; font-weight: 700; margin: 14px 0; word-break: break-word; }
  .role-card.crew .role-word { color: #86efac; }
  .role-card.imposter .role-word { color: #fca5a5; }
  .role-hint { font-size: 0.9rem; color: #cbd5e1; line-height: 1.4; white-space: pre-line; }
  .progress { text-align: center; font-size: 0.8rem; color: #94a3b8; margin-top: 12px; }
  .vote-list { display: grid; gap: 10px; margin-top: 14px; }
  .vote-btn { margin-top: 0; background: #1e293b; border: 1px solid #475569; font-weight: 500; text-align: left; padding-left: 18px; }
  .vote-btn:hover { background: #334155; }
  .vote-btn.selected { background: #6366f1; border-color: #818cf8; }
  .vote-btn.done { opacity: 0.55; }
  .result-title { text-align: center; font-size: 1.35rem; margin-bottom: 10px; line-height: 1.3; }
  .result-detail { text-align: center; color: #cbd5e1; font-size: 0.95rem; line-height: 1.7; margin-top: 12px; }
  .result-detail strong { color: #f8fafc; }
  .clue-item { padding: 10px 14px; background: #1e293b; border-radius: 10px; font-size: 0.9rem; color: #cbd5e1; line-height: 1.4; }
  .clue-item .name { color: #818cf8; font-weight: 600; }
  .clue-item.mine { border: 1px solid #6366f1; }
  .clue-item .play-btn { margin-top: 6px; padding: 6px 12px; font-size: 0.8rem; width: auto; background: #4f46e5; }
  .round-header { text-align: center; margin: 4px 0 10px; font-size: 0.92rem; color: #a5b4fc; font-weight: 600; letter-spacing: 0.5px; }
  .error { color: #fca5a5; text-align: center; font-size: 0.85rem; margin-top: 10px; min-height: 1em; }
  .vote-summary { margin-top: 16px; display: grid; gap: 6px; }
  .vote-row { display: flex; justify-content: space-between; padding: 8px 12px; background: #1e293b;
              border-radius: 8px; font-size: 0.9rem; color: #cbd5e1; }
  .vote-row .count { color: #a5b4fc; font-weight: 600; }
  .vote-row.top { border: 1px solid #6366f1; }
  .code-box { text-align: center; font-size: 2rem; font-weight: 800; letter-spacing: 6px;
              color: #a5b4fc; background: #1e293b; padding: 14px; border-radius: 12px;
              border: 1px dashed #6366f1; margin: 14px 0; user-select: all; }
  .players-list { display: grid; gap: 8px; margin-top: 12px; }
  .player-row { display: flex; justify-content: space-between; align-items: center;
                padding: 10px 14px; background: #1e293b; border-radius: 10px; font-size: 0.92rem; }
  .player-row .tag { font-size: 0.75rem; color: #94a3b8; }
  .player-row.ready { border-left: 3px solid #22c55e; }
  .tabs { display: flex; gap: 8px; margin-top: 12px; }
  .tabs button { margin-top: 0; }
  .small { font-size: 0.78rem; color: #94a3b8; text-align:center; margin-top: 8px; }
  .qr-wrap { text-align: center; margin: 12px 0; }
  .qr-wrap img { width: 180px; height: 180px; border-radius: 12px; background: white; padding: 8px; }
  .imposter-pill {
    display:inline-block; background: rgba(239,68,68,0.2); color:#fca5a5;
    border: 1px solid rgba(239,68,68,0.5); border-radius:999px;
    padding:4px 12px; font-size:0.8rem; margin: 2px;
  }
  .banner {
    text-align:center; padding: 18px 14px; border-radius: 14px; margin-top: 8px;
    font-size: 1.15rem; font-weight: 700; line-height: 1.4;
  }
  .banner.crew { background: rgba(34,197,94,0.15); border:1px solid rgba(34,197,94,0.5); color:#86efac; }
  .banner.imposter { background: rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.5); color:#fca5a5; }
  .banner.tie { background: rgba(253,224,71,0.12); border:1px solid rgba(253,224,71,0.45); color:#fde68a; }

  /* ---------- audio recorder ---------- */
  .recorder {
    display: flex; align-items: center; gap: 12px;
    background: #1e293b; border: 1px solid #475569; border-radius: 12px;
    padding: 12px; margin-top: 8px;
  }
  .rec-btn {
    width: 60px; height: 60px; border-radius: 50%;
    background: #dc2626; border: 2px solid #7f1d1d;
    color: white; font-size: 1.5rem; padding: 0; margin: 0;
    flex-shrink: 0; cursor: pointer;
    transition: transform 0.1s;
  }
  .rec-btn:active { transform: scale(0.92); }
  .rec-btn.recording {
    background: #991b1b;
    animation: pulse 1s infinite;
  }
  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(220,38,38,0.7); }
    50% { box-shadow: 0 0 0 12px rgba(220,38,38,0); }
  }
  .rec-info { flex: 1; font-size: 0.85rem; color: #cbd5e1; line-height: 1.4; }
  .rec-timer { color: #fca5a5; font-weight: 700; font-size: 1rem; }
  .rec-clear { padding: 6px 12px; font-size: 0.8rem; width: auto; margin: 0; background: #475569; }

  /* ---------- chat ---------- */
  .chat-fab {
    position: fixed; bottom: 18px; right: 18px;
    width: 56px; height: 56px; border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    box-shadow: 0 8px 24px rgba(99,102,241,0.5);
    color: white; font-size: 1.4rem; padding: 0; margin: 0;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; z-index: 100;
  }
  .chat-fab .unread {
    position: absolute; top: 4px; right: 4px;
    background: #ef4444; color: white; font-size: 0.7rem;
    min-width: 18px; height: 18px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    padding: 0 4px; font-weight: 700;
  }
  .chat-panel {
    position: fixed; bottom: 0; left: 0; right: 0; top: 0;
    background: rgba(2, 6, 23, 0.95); z-index: 200;
    display: none; flex-direction: column;
  }
  .chat-panel.open { display: flex; }
  .chat-header {
    padding: 16px; border-bottom: 1px solid #334155;
    display: flex; justify-content: space-between; align-items: center;
    background: #0f172a;
  }
  .chat-header h3 { font-size: 1.1rem; }
  .chat-close {
    background: transparent; border: none; color: white;
    font-size: 1.6rem; width: auto; padding: 0 8px; margin: 0;
  }
  .chat-messages {
    flex: 1; overflow-y: auto; padding: 12px 16px;
    display: flex; flex-direction: column; gap: 8px;
  }
  .chat-msg {
    max-width: 80%; padding: 8px 12px; border-radius: 12px;
    font-size: 0.9rem; line-height: 1.4; word-wrap: break-word;
  }
  .chat-msg.mine { align-self: flex-end; background: #4f46e5; border-bottom-right-radius: 4px; }
  .chat-msg.other { align-self: flex-start; background: #334155; border-bottom-left-radius: 4px; }
  .chat-msg.system { align-self: center; background: transparent; color: #94a3b8;
                      font-size: 0.78rem; font-style: italic; text-align: center; padding: 4px; }
  .chat-msg .sender { font-size: 0.72rem; opacity: 0.7; margin-bottom: 2px; font-weight: 600; }
  .chat-input-row {
    padding: 12px 16px 20px; border-top: 1px solid #334155;
    display: flex; gap: 8px; background: #0f172a;
  }
  .chat-input-row input { flex: 1; margin: 0; }
  .chat-input-row button { width: auto; padding: 12px 18px; margin: 0; }
  .chat-locked {
    padding: 10px; text-align: center; color: #fca5a5;
    font-size: 0.85rem; background: rgba(239,68,68,0.1);
    border-top: 1px solid rgba(239,68,68,0.3);
  }

  /* ---------- menu / reset ---------- */
  .menu-fab {
    position: fixed; bottom: 18px; left: 18px;
    width: 48px; height: 48px; border-radius: 50%;
    background: #334155; color: white; font-size: 1.4rem;
    padding: 0; margin: 0; z-index: 100;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.4);
  }
  .menu-panel {
    position: fixed; inset: 0; background: rgba(2,6,23,0.9); z-index: 300;
    display: none; align-items: center; justify-content: center; padding: 20px;
  }
  .menu-panel.open { display: flex; }
  .menu-card {
    background: #0f172a; border: 1px solid #334155; border-radius: 16px;
    padding: 24px; max-width: 380px; width: 100%;
  }
  .menu-card h3 { margin-bottom: 14px; text-align: center; }
  .menu-card button { margin-top: 10px; }

  /* ---------- scoreboard ---------- */
  .scoreboard { background: #1e293b; border-radius: 12px; padding: 10px 14px; margin-top: 12px; }
  .scoreboard h4 { font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
  .score-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 0.9rem; }
  .score-row .pts { color: #86efac; font-weight: 700; }
</style>
</head>
<body>
<div class="app">
  <h1>🕵️ Imposter Word</h1>
  <p class="subtitle">Everyone on their own phone. Same word — except the imposters.</p>

  <!-- ===================== HOME ===================== -->
  <div id="screen-home" class="screen active">
    <label for="playerName">Your name</label>
    <input type="text" id="playerName" maxlength="20" placeholder="e.g. Rahul" autocomplete="off">

    <div class="tabs">
      <button onclick="createGame()">Create game</button>
      <button class="secondary" onclick="showJoin()">Join game</button>
    </div>

    <div id="joinBox" style="display:none;">
      <label for="joinCode">Room code</label>
      <input type="text" id="joinCode" maxlength="6" placeholder="XK4P2Q"
             style="text-transform:uppercase;letter-spacing:3px;text-align:center;font-size:1.3rem;"
             autocomplete="off">
      <button onclick="joinGame()">Join</button>
    </div>

    <label for="lang">Language / भाषा (host only)</label>
    <select id="lang">
      <option value="en">English</option>
      <option value="hi">हिन्दी (Hindi)</option>
    </select>

    <div id="homeError" class="error"></div>
    <div class="small" id="resumeHint" style="display:none;">
      <button class="secondary" onclick="resumeSession()" style="margin-top:8px;">Resume last game</button>
    </div>
  </div>

  <!-- ===================== LOBBY ===================== -->
  <div id="screen-lobby" class="screen">
    <h2>Lobby</h2>
    <p class="subtitle">Scan the QR or share the code</p>
    <div class="code-box" id="lobbyCode">------</div>
    <div class="qr-wrap" id="qrWrap"></div>
    <div class="players-list" id="lobbyPlayers"></div>
    <div class="progress" id="lobbyProgress"></div>

    <div id="hostImposterBox" style="display:none;">
      <label for="numImposters">Number of imposters</label>
      <select id="numImposters">
        <option value="1">1 imposter</option>
        <option value="2">2 imposters</option>
        <option value="3">3 imposters</option>
      </select>
      <div class="small" id="imposterNote"></div>
    </div>

    <button id="lobbyReadyBtn" onclick="toggleReady()">I'm ready</button>
    <button id="lobbyStartBtn" onclick="startGame()" style="display:none;">Start game</button>
    <div class="error" id="lobbyError"></div>
    <div class="small">Auto-updates every 1.5s.</div>
  </div>

  <!-- ===================== REVEAL ===================== -->
  <div id="screen-reveal" class="screen">
    <div class="round-header" id="revealRound">ROLE REVEAL</div>
    <h2>Your secret role</h2>
    <p class="subtitle">Keep this hidden!</p>
    <div id="revealCard" class="role-card">
      <div class="role-label" id="revealLabel">—</div>
      <div class="role-word" id="revealWord">—</div>
      <div class="role-hint" id="revealHint"></div>
    </div>
    <button onclick="hostAdvance()" id="revealNextBtn" style="display:none;">Everyone ready — go to clues →</button>
    <div class="progress" id="revealProgress">Only the host can advance.</div>
  </div>

  <!-- ===================== CLUE ===================== -->
  <div id="screen-clue" class="screen">
    <div class="round-header" id="clueRoundHeader">ROUND 1 — CLUES</div>
    <h2>Give your clue</h2>
    <p class="subtitle">Type a clue <em>or</em> record a voice note (max 10s).</p>

    <label for="clueInput">Type your clue</label>
    <input type="text" id="clueInput" maxlength="80" placeholder="Type your clue..." autocomplete="off">
    <button id="clueSubmitBtn" onclick="submitClue()">Submit written clue</button>

    <div style="text-align:center;color:#94a3b8;font-size:0.85rem;margin:14px 0 6px;">— OR —</div>

    <div class="recorder" id="recorderBox">
      <button class="rec-btn" id="recBtn" onclick="toggleRecording()">🎙️</button>
      <div class="rec-info" id="recInfo">
        Tap the mic to record a voice clue.<br>
        Max 10 seconds.
      </div>
      <button class="rec-clear" id="recClearBtn" onclick="clearRecording()" style="display:none;">Clear</button>
    </div>
    <audio id="recPlayback" controls style="width:100%;margin-top:8px;display:none;"></audio>
    <button id="voiceSubmitBtn" onclick="submitVoice()" style="display:none;">Submit voice clue</button>

    <div class="error" id="clueError"></div>
    <div class="players-list" id="clueWaitingList"></div>
    <div class="progress" id="clueProgress"></div>
  </div>

  <!-- ===================== SUMMARY ===================== -->
  <div id="screen-summary" class="screen">
    <div class="round-header" id="summaryHeader">ROUND 1 COMPLETE</div>
    <h2>All clues</h2>
    <p class="subtitle">Read carefully. Tap ▶ to play voice clues.</p>
    <div id="summaryList" style="display:grid;gap:8px;margin-top:12px;"></div>
    <button onclick="hostAdvance()" id="summaryNextBtn" style="display:none;">Continue →</button>
    <div class="progress">Waiting for the host...</div>
  </div>

  <!-- ===================== VOTE ===================== -->
  <div id="screen-vote" class="screen">
    <h2>Vote!</h2>
    <p class="subtitle">Who is an imposter? Your vote is secret.</p>
    <label>Your vote</label>
    <div id="voteList" class="vote-list"></div>
    <button id="voteSubmitBtn" onclick="submitVote()" disabled>Lock in vote</button>
    <div class="error" id="voteError"></div>
    <div class="players-list" id="voteWaitingList"></div>
    <div class="small">💬 Use chat below to discuss while waiting.</div>
  </div>

  <!-- ===================== RESULT ===================== -->
  <div id="screen-result" class="screen">
    <div id="resultBanner" class="banner">—</div>
    <div class="result-detail" id="resultDetail"></div>

    <div id="voteSummaryBox" style="margin-top:14px;">
      <div class="round-header">VOTE TALLY</div>
      <div id="voteSummary" class="vote-summary"></div>
    </div>

    <div id="imposterBox" style="margin-top:14px;text-align:center;"></div>

    <div class="scoreboard" id="scoreboard"></div>

    <div id="resultClues" style="margin-top:14px;"></div>

    <button onclick="playAgain()" id="playAgainBtn" style="display:none;">▶ Play again (same players)</button>
    <div class="progress" id="resultProgress">Waiting for host...</div>
  </div>
</div>

<!-- ===================== CHAT FAB ===================== -->
<button class="chat-fab" id="chatFab" onclick="toggleChat()" style="display:none;">
  💬<span class="unread" id="chatUnread" style="display:none;">0</span>
</button>

<!-- ===================== CHAT PANEL ===================== -->
<div class="chat-panel" id="chatPanel">
  <div class="chat-header">
    <h3>💬 Room chat</h3>
    <button class="chat-close" onclick="toggleChat()">×</button>
  </div>
  <div class="chat-messages" id="chatMessages"></div>
  <div class="chat-locked" id="chatLocked" style="display:none;">Chat is locked during this phase.</div>
  <div class="chat-input-row" id="chatInputRow">
    <input type="text" id="chatInput" maxlength="200" placeholder="Say something..." autocomplete="off">
    <button onclick="sendChat()">Send</button>
  </div>
</div>

<!-- ===================== MENU FAB ===================== -->
<button class="menu-fab" id="menuFab" onclick="toggleMenu()" style="display:none;">☰</button>

<!-- ===================== MENU PANEL ===================== -->
<div class="menu-panel" id="menuPanel">
  <div class="menu-card">
    <h3>Game menu</h3>
    <div class="small" style="margin-bottom:12px;">
      Room: <strong id="menuRoomCode">------</strong><br>
      You: <strong id="menuYouName">—</strong>
    </div>
    <button class="secondary" onclick="leaveGame()">🚪 Leave game</button>
    <button class="danger" id="menuEndBtn" onclick="endGame()" style="display:none;">🛑 End game for everyone</button>
    <button class="secondary" onclick="toggleMenu()">Cancel</button>
  </div>
</div>

<script>
// ============================================================================
//  STATE
// ============================================================================
const STORAGE_KEY = 'imposter_session_v4';
let session = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
let current = null;
let pollTimer = null;
let selectedVote = null;
let chatOpen = false;
let lastChatCount = 0;
let mediaRecorder = null;
let recordedChunks = [];
let recordedAudioDataUrl = null;
let recordTimer = null;
let recordSeconds = 0;

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

function saveSession(s) {
  session = s;
  if (s) localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  else localStorage.removeItem(STORAGE_KEY);
}

// ============================================================================
//  HOME
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
  if (!name) return err('Enter your name first');
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
  if (!name) return err('Enter your name first');
  if (code.length !== 6) return err('Room code must be 6 characters');
  try {
    const r = await api('join', { name, code });
    saveSession({ code: r.code, token: r.token, name });
    applyState(r.state);
  } catch (e) {
    const m = { game_not_found: 'No game with that code', game_in_progress: 'That game already started',
                game_full: 'That game is full (10 max)', name_taken: 'That name is taken in this room' };
    err(m[e.message] || e.message);
  }
}

async function resumeSession() {
  if (!session) return;
  try { applyState(await api('state', session)); }
  catch (e) { saveSession(null); err('That game no longer exists'); }
}

// ============================================================================
//  POLLING
// ============================================================================
function startPolling() {
  stopPolling();
  pollTimer = setInterval(async () => {
    if (!session) return;
    try { applyState(await api('state', session)); }
    catch (e) {
      if (e.message === 'game_not_found' || e.message === 'not_in_game') {
        saveSession(null); stopPolling(); show('screen-home');
      }
    }
  }, 1500);
}
function stopPolling() { if (pollTimer) { clearInterval(pollTimer); pollTimer = null; } }

// ============================================================================
//  ROUTER
// ============================================================================
function applyState(s) {
  current = s;
  const p = s.phase;
  if (p === 'lobby')        renderLobby(s);
  else if (p === 'reveal')  renderReveal(s);
  else if (p === 'clue')    renderClue(s);
  else if (p === 'summary') renderSummary(s);
  else if (p === 'vote')    renderVote(s);
  else if (p === 'result')  renderResult(s);
  updateChatBadge(s);
  if (chatOpen) renderChat(s);
  // show menu FAB when in a game
  $('menuFab').style.display = 'flex';
  $('menuRoomCode').textContent = s.code;
  $('menuYouName').textContent = s.you ? s.you.name : '—';
  $('menuEndBtn').style.display = s.is_host ? 'block' : 'none';
  startPolling();
}

// ============================================================================
//  LOBBY
// ============================================================================
function renderLobby(s) {
  show('screen-lobby');
  $('lobbyCode').textContent = s.code;
  const joinUrl = location.origin + '/join?code=' + s.code;
  $('qrWrap').innerHTML = `<img alt="QR to join" src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(joinUrl)}">`;
  const list = $('lobbyPlayers');
  list.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'player-row' + (p.ready ? ' ready' : '');
    const mine = p.name === s.you.name;
    const kick = s.is_host && !mine && s.phase === 'lobby'
      ? ` <button class="rec-clear" style="padding:2px 8px;font-size:0.7rem;" onclick="kickPlayer('${esc(p.name)}')">✕</button>` : '';
    d.innerHTML = `<span>${esc(p.name)}${mine ? ' (you)' : ''}${p.name === s.host_name ? ' 👑' : ''}</span>
                   <span class="tag">${p.ready ? '✅ ready' : '⏳ not ready'}${kick}</span>`;
    list.appendChild(d);
  });
  $('lobbyProgress').textContent = `${s.players.length} player(s) — need 3+, up to 10`;
  $('lobbyReadyBtn').textContent = s.you.ready ? 'Not ready' : "I'm ready";
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
      opt.value = k; opt.textContent = k + ' imposter' + (k > 1 ? 's' : '');
      sel.appendChild(opt);
    }
    sel.value = String(Math.min(s.imposter_count, Math.min(3, maxK)));
    $('imposterNote').textContent = `Max ${maxK} with ${n} players.`;
  } else {
    box.style.display = 'none';
  }

  if (s.is_host) {
    $('lobbyStartBtn').style.display = 'block';
    const allReady = s.players.every(p => p.ready);
    $('lobbyStartBtn').disabled = !(n >= 3 && allReady);
    $('lobbyStartBtn').textContent = n < 3
      ? `Need ${3 - n} more player(s)`
      : (allReady ? '▶ Start game' : 'Waiting for everyone to be ready');
  } else {
    $('lobbyStartBtn').style.display = 'none';
  }
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
  if (!confirm(`Remove ${name} from the room?`)) return;
  try { applyState(await api('kick', { ...session, target: name })); }
  catch (e) { alert(e.message); }
}

// ============================================================================
//  REVEAL
// ============================================================================
function renderReveal(s) {
  show('screen-reveal');
  const card = $('revealCard');
  const isImp = !!s.you_are_imposter;
  card.className = 'role-card ' + (isImp ? 'imposter' : 'crew');
  $('revealLabel').textContent = isImp ? 'You are an IMPOSTER!' : 'Your word';
  $('revealWord').textContent = isImp ? '🤫' : (s.your_word || '—');
  $('revealHint').textContent = isImp
    ? 'Hint: ' + (s.your_hint || '') + '\nBlend in — don\'t get caught!'
    : 'Describe it without saying the word!';
  $('revealRound').textContent = `ROLE REVEAL — ${s.imposter_count} IMPOSTER${s.imposter_count>1?'S':''} HIDDEN`;
  $('revealNextBtn').style.display = s.is_host ? 'block' : 'none';
  $('chatFab').style.display = 'flex';
}

// ============================================================================
//  CLUE + RECORDING
// ============================================================================
let clueAudioEl = null;

function renderClue(s) {
  show('screen-clue');
  $('clueRoundHeader').textContent = `ROUND ${s.round} OF 2 — CLUES`;
  const submitted = s.you.clue || s.you.clue_audio;
  $('clueInput').disabled = !!submitted;
  $('clueSubmitBtn').disabled = !!submitted;
  $('clueSubmitBtn').textContent = submitted ? 'Submitted ✅' : 'Submit written clue';
  if (submitted && s.you.clue) $('clueInput').value = s.you.clue;
  $('voiceSubmitBtn').style.display = recordedAudioDataUrl && !submitted ? 'block' : 'none';
  $('voiceSubmitBtn').disabled = !!submitted;

  const wl = $('clueWaitingList');
  wl.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'player-row';
    d.innerHTML = `<span>${esc(p.name)}</span><span class="tag">${p.has_clue ? '✅ done' : '✏️ thinking...'}</span>`;
    wl.appendChild(d);
  });
  const done = s.players.filter(p => p.has_clue).length;
  $('clueProgress').textContent = `${done} / ${s.players.length} submitted`;
  $('chatFab').style.display = submitted ? 'flex' : 'none';  // chat unlocked after submit
  if (chatOpen && submitted) renderChat(s);
}

async function toggleRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    stopRecording();
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) recordedChunks.push(e.data);
    };
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(recordedChunks, { type: 'audio/webm' });
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
    $('clueError').textContent = 'Mic permission denied or unavailable.';
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
  clearInterval(recordTimer);
  $('recBtn').classList.remove('recording');
  $('recBtn').textContent = '🎙️';
  $('recInfo').innerHTML = 'Recorded! Tap ▶ to preview, or Clear to redo.';
}

function clearRecording() {
  recordedAudioDataUrl = null;
  $('recPlayback').style.display = 'none';
  $('recPlayback').src = '';
  $('voiceSubmitBtn').style.display = 'none';
  $('recClearBtn').style.display = 'none';
  $('recInfo').innerHTML = 'Tap the mic to record a voice clue.<br>Max 10 seconds.';
}

async function submitClue() {
  if (!session) return;
  $('clueError').textContent = '';
  const text = $('clueInput').value.trim();
  if (!text) { $('clueError').textContent = 'Please type a clue.'; return; }
  try { applyState(await api('clue', { ...session, text })); }
  catch (e) {
    const m = { contains_word: '❌ Your clue contains the secret word!' };
    $('clueError').textContent = m[e.message] || e.message;
  }
}

async function submitVoice() {
  if (!session || !recordedAudioDataUrl) return;
  $('clueError').textContent = '';
  try {
    applyState(await api('audio', { ...session, audio: recordedAudioDataUrl }));
    clearRecording();
  } catch (e) {
    const m = { audio_too_large: 'Recording too large. Try a shorter clip.' };
    $('clueError').textContent = m[e.message] || e.message;
  }
}

// ============================================================================
//  SUMMARY
// ============================================================================
function renderSummary(s) {
  show('screen-summary');
  $('summaryHeader').textContent = `ROUND ${s.round} COMPLETE`;
  const list = $('summaryList');
  list.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'clue-item' + (p.name === s.you.name ? ' mine' : '');
    if (p.clue) {
      d.innerHTML = `<span class="name">${esc(p.name)}:</span> ${esc(p.clue)}`;
    } else if (p.clue_audio) {
      d.innerHTML = `<span class="name">${esc(p.name)}:</span> 🎙️ voice clue
        <button class="play-btn" onclick="playAudio('${p.clue_audio}')">▶ Play</button>`;
    } else {
      d.innerHTML = `<span class="name">${esc(p.name)}:</span> —`;
    }
    list.appendChild(d);
  });
  const btn = $('summaryNextBtn');
  if (s.is_host) {
    btn.style.display = 'block';
    btn.textContent = s.round === 1 ? 'Start Round 2 →' : 'Go to voting →';
  } else {
    btn.style.display = 'none';
  }
  $('chatFab').style.display = 'flex';
}

function playAudio(dataUrl) {
  const a = new Audio(dataUrl);
  a.play().catch(() => alert('Tap again to play'));
}

async function hostAdvance() {
  if (!session) return;
  try { applyState(await api('advance', session)); }
  catch (e) { alert(e.message); }
}

// ============================================================================
//  VOTE
// ============================================================================
function renderVote(s) {
  show('screen-vote');
  const voted = s.you.has_voted;
  if (voted) selectedVote = null;
  $('voteSubmitBtn').disabled = !selectedVote || voted;
  $('voteSubmitBtn').textContent = voted ? 'Vote locked ✅' : 'Lock in vote';
  const list = $('voteList');
  list.innerHTML = '';
  s.players.forEach(p => {
    const btn = document.createElement('button');
    btn.className = 'vote-btn' + (p.name === selectedVote ? ' selected' : '') + (voted ? ' done' : '');
    btn.textContent = p.name + (p.name === s.you.name ? ' (you)' : '');
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
    d.innerHTML = `<span>${esc(p.name)}</span><span class="tag">${p.has_voted ? '✅ voted' : '⏳ waiting'}</span>`;
    wl.appendChild(d);
  });
  $('chatFab').style.display = 'flex';
}

async function submitVote() {
  if (!session || !selectedVote) return;
  $('voteError').textContent = '';
  try {
    const r = await api('vote', { ...session, target: selectedVote });
    selectedVote = null;
    applyState(r);
  } catch (e) { $('voteError').textContent = e.message; }
}

// ============================================================================
//  RESULT
// ============================================================================
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
  if (s.vote_tie) detail += `The vote was a tie.<br>`;
  else if (s.voted_out_name) detail += `Voted out: <strong>${esc(s.voted_out_name)}</strong>.<br>`;
  detail += `Imposter${imposterNames.length>1?'s':''}: ` +
            imposterNames.map(n => `<strong>${esc(n)}</strong>`).join(', ') +
            `<br>Secret word: <strong>${esc(s.secret_word)}</strong>.`;
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
                     <span class="count">${count} vote${count === 1 ? '' : 's'}</span>`;
    box.appendChild(row);
  });

  $('imposterBox').innerHTML =
    `<div class="round-header">IMPOSTER${imposterNames.length>1?'S':''}</div>` +
    imposterNames.map(n => `<span class="imposter-pill">🕵️ ${esc(n)}</span>`).join(' ');

  const sb = $('scoreboard');
  const scores = s.scores || {};
  const sortedScores = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  if (sortedScores.length) {
    sb.innerHTML = '<h4>🏆 Session scores</h4>' +
      sortedScores.map(([n, v]) => `<div class="score-row"><span>${esc(n)}</span><span class="pts">${v} win${v===1?'':'s'}</span></div>`).join('');
  }

  const rc = $('resultClues');
  rc.innerHTML = '<div class="round-header">ROUND 2 CLUES</div>';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'clue-item' + (p.name === s.you.name ? ' mine' : '');
    if (p.clue) d.innerHTML = `<span class="name">${esc(p.name)}:</span> ${esc(p.clue)}`;
    else if (p.clue_audio) d.innerHTML = `<span class="name">${esc(p.name)}:</span> 🎙️ voice
      <button class="play-btn" onclick="playAudio('${p.clue_audio}')">▶ Play</button>`;
    else d.innerHTML = `<span class="name">${esc(p.name)}:</span> —`;
    rc.appendChild(d);
  });

  $('playAgainBtn').style.display = s.is_host ? 'block' : 'none';
  $('resultProgress').textContent = s.is_host ? '' : 'Waiting for host to start a new round...';
  $('chatFab').style.display = 'flex';
}

async function playAgain() {
  if (!session) return;
  try { applyState(await api('reset', session)); }
  catch (e) { alert(e.message); }
}

// ============================================================================
//  CHAT
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
    const diff = newCount - lastChatCount;
    const badge = $('chatUnread');
    badge.textContent = diff;
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
  // chat lock
  const locked = s.phase === 'clue' && !(s.you && (s.you.clue || s.you.clue_audio));
  $('chatLocked').style.display = locked ? 'block' : 'none';
  $('chatInputRow').style.display = locked ? 'none' : 'flex';
}

async function sendChat() {
  if (!session) return;
  const input = $('chatInput');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  try { applyState(await api('chat', { ...session, text })); }
  catch (e) {
    const m = {
      chat_locked: 'Chat is locked right now.',
      chat_blocked_during_clue: 'Submit your clue first!'
    };
    alert(m[e.message] || e.message);
  }
}

// ============================================================================
//  MENU / LEAVE / END
// ============================================================================
function toggleMenu() {
  $('menuPanel').classList.toggle('open');
}

async function leaveGame() {
  if (!session) return;
  if (!confirm('Leave this game? You cannot rejoin without the code.')) return;
  try { await api('leave', session); } catch (e) {}
  saveSession(null);
  stopPolling();
  $('chatFab').style.display = 'none';
  $('menuFab').style.display = 'none';
  $('menuPanel').classList.remove('open');
  show('screen-home');
  err('You left the game.');
}

async function endGame() {
  if (!session) return;
  if (!confirm('End game for everyone? All players will be kicked out.')) return;
  try { await api('end', session); } catch (e) {}
  saveSession(null);
  stopPolling();
  $('chatFab').style.display = 'none';
  $('menuFab').style.display = 'none';
  $('menuPanel').classList.remove('open');
  show('screen-home');
  err('Game ended.');
}

// ============================================================================
//  BOOT
// ============================================================================
(async function boot() {
  if (session) {
    $('resumeHint').style.display = 'block';
    $('playerName').value = session.name || '';
    try { applyState(await api('state', session)); return; }
    catch (e) { saveSession(null); }
  }
  const params = new URLSearchParams(location.search);
  if (params.get('code')) showJoin();
  show('screen-home');
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
    print("\n[SHUTDOWN] Cleaning up...")
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, _graceful_shutdown)
    print(f"[BOOT] Imposter Word on port {PORT} | RENDER={os.environ.get('RENDER', 'no')}")
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
