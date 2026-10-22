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

PORT = int(os.environ.get("PORT", 8000))

# ===========================================================================
# WORD BANK  — paste your original 50 entries here unchanged.
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
# IN-MEMORY GAME STORE
# ===========================================================================
GAMES = {}
GAMES_LOCK = threading.Lock()
GAME_TTL_SECONDS = 3 * 60 * 60


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
        "clue": "", "vote": None, "ready": False,
    }


def _tally_votes(game):
    """Count votes → (winner_name_or_None, tie_bool, counts_dict)."""
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
        players.append({
            "name": p["name"],
            "ready": p["ready"],
            "clue": p["clue"] if game["phase"] in ("summary", "vote", "result") else "",
            "has_voted": p["vote"] is not None,
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
        "you": None,
    }
    if me:
        state["you"] = {
            "name": me["name"],
            "ready": me["ready"],
            "clue": me["clue"],
            "has_voted": me["vote"] is not None,
        }
        if game["phase"] in ("reveal", "clue", "summary", "vote", "result"):
            state["your_word"] = me["role_word"]
            state["your_hint"] = me["role_hint"]
            state["you_are_imposter"] = me["is_imposter"]
    if game["phase"] == "result":
        state["imposter_names"] = game["imposter_names"]
        state["secret_word"] = game["word"]
        state["result_banner"] = game["result_banner"]          # crew / imposter / tie
        state["vote_counts"] = game["vote_counts"]              # {name: n}
        state["voted_out_name"] = game["voted_out_name"]        # name or None (tie)
        state["vote_tie"] = game["vote_tie"]
    return state


# ===========================================================================
# HTTP HANDLER
# ===========================================================================
class GameHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
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
            self._json(200, {"ok": True})
        elif path == "/join":                      # QR short link → SPA with ?code
            qs = urllib.parse.urlparse(self.path).query
            self.send_response(302)
            self.send_header("Location", "/?" + qs)
            self.end_headers()
        else:
            self._send(404, "Not found", "text/plain")

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            if path == "/api/create":
                self._handle_create()
            elif path == "/api/join":
                self._handle_join()
            elif path == "/api/state":
                self._handle_state()
            elif path == "/api/ready":
                self._handle_ready()
            elif path == "/api/start":
                self._handle_start()
            elif path == "/api/clue":
                self._handle_clue()
            elif path == "/api/advance":
                self._handle_advance()
            elif path == "/api/vote":
                self._handle_vote()
            elif path == "/api/reset":
                self._handle_reset()
            else:
                self._send(404, "Not found", "text/plain")
        except Exception as e:
            self._json(500, {"error": str(e)})

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

    # ----------------------------------------------------------- create/join
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
                "round": 1,
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
            game["last_activity"] = time.time()
        self._json(200, {"code": code, "token": token, "state": _public_state(game, token)})

    # ------------------------------------------------------------------ state
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

    # ------------------------------------------------------------------ start
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
            # imposters must be fewer than half the players (strict majority for crew)
            max_k = max(1, (n - 1) // 2)
            k = max(1, min(k, max_k))
            entry = random.choice(WORD_BANK)[game["lang"]]
            game["word"] = entry["word"]
            game["imposter_hint"] = entry["imposter_hint"]
            game["imposter_count"] = k
            # pick k distinct imposter indices
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
                p["vote"] = None
            game["phase"] = "reveal"
            game["round"] = 1
            game["result_banner"] = ""
            game["vote_counts"] = {}
            game["voted_out_name"] = None
            game["vote_tie"] = False
            self._json(200, _public_state(game, token))

        self._with_game(payload, run)

    # ------------------------------------------------------------------- clue
    def _handle_clue(self):
        payload = self._read_json() or {}
        text = (payload.get("text") or "").strip()[:80]

        def run(game, token, payload):
            if game["phase"] != "clue":
                return self._json(409, {"error": "not_clue_phase"})
            me = self._find_player(game, token)
            if not text:
                return self._json(400, {"error": "empty_clue"})
            if me["clue"]:
                return self._json(409, {"error": "already_submitted"})
            me["clue"] = text
            if all(p["clue"] for p in game["players"]):
                game["phase"] = "summary"
            self._json(200, _public_state(game, token))

        self._with_game(payload, run)

    # ---------------------------------------------------------------- advance
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
            elif game["phase"] == "summary":
                if game["round"] == 1:
                    game["round"] = 2
                    game["phase"] = "clue"
                    for p in game["players"]:
                        p["clue"] = ""
                else:
                    game["phase"] = "vote"
                    for p in game["players"]:
                        p["vote"] = None
            self._json(200, _public_state(game, token))

        self._with_game(payload, run)

    # ------------------------------------------------------------------- vote
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
                # === WINNER BANNER COMPUTATION (server-side, once) ===
                game["phase"] = "result"
                top_name, is_tie, counts = _tally_votes(game)
                game["vote_counts"] = counts
                game["vote_tie"] = is_tie
                game["voted_out_name"] = top_name

                imposter_names = set(game["imposter_names"])
                crew_count = len(game["players"]) - len(imposter_names)

                if is_tie:
                    # No majority → imposters survive
                    game["result_banner"] = "imposter" if crew_count > 0 else "tie"
                elif top_name in imposter_names:
                    # An imposter is voted out. Crew wins only if *all* imposters
                    # are removed — with one vote that only happens if there's
                    # exactly one imposter.
                    if len(imposter_names) == 1:
                        game["result_banner"] = "crew"
                    else:
                        # Multi-imposter: removing one still leaves others.
                        # Standard rule: crew wins only if ALL caught.
                        # With one vote round, this is a partial catch → imposter survives.
                        game["result_banner"] = "imposter"
                else:
                    # A crew member was voted out → imposters win
                    game["result_banner"] = "imposter"

            self._json(200, _public_state(game, token))

        self._with_game(payload, run)

    # ------------------------------------------------------------------ reset
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
            for p in game["players"]:
                p["clue"] = ""
                p["vote"] = None
                p["ready"] = False
                p["is_imposter"] = False
                p["role_word"] = ""
                p["role_hint"] = ""
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
  .role-card { text-align: center; padding: 28px 16px; border-radius: 16px; margin-top: 14px; }
  .role-card.crew { background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34,197,94,0.4); }
  .role-card.imposter { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239,68,68,0.4); }
  .role-label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; }
  .role-word { font-size: 1.8rem; font-weight: 700; margin: 14px 0; word-break: break-word; }
  .role-card.crew .role-word { color: #86efac; }
  .role-card.imposter .role-word { color: #fca5a5; }
  .role-hint { font-size: 0.9rem; color: #cbd5e1; line-height: 1.4; white-space: pre-line; }
  .pill {
    display: inline-block; background: #4f46e5; padding: 6px 14px;
    border-radius: 999px; font-size: 0.82rem; font-weight: 600; margin-bottom: 14px;
  }
  .pill.green { background: #166534; } .pill.gray { background: #334155; }
  .progress { text-align: center; font-size: 0.8rem; color: #94a3b8; margin-top: 12px; }
  .vote-list { display: grid; gap: 10px; margin-top: 14px; }
  .vote-btn { margin-top: 0; background: #1e293b; border: 1px solid #475569; font-weight: 500; text-align: left; padding-left: 18px; }
  .vote-btn:hover { background: #334155; }
  .vote-btn.selected { background: #6366f1; border-color: #818cf8; }
  .vote-btn.done { opacity: 0.55; }
  .result-title { text-align: center; font-size: 1.35rem; margin-bottom: 10px; line-height: 1.3; }
  .result-win { color: #86efac; } .result-lose { color: #fca5a5; } .result-tie { color: #fde68a; }
  .result-detail { text-align: center; color: #cbd5e1; font-size: 0.95rem; line-height: 1.7; margin-top: 12px; }
  .result-detail strong { color: #f8fafc; }
  .clue-item { padding: 10px 14px; background: #1e293b; border-radius: 10px; font-size: 0.9rem; color: #cbd5e1; line-height: 1.4; }
  .clue-item .name { color: #818cf8; font-weight: 600; }
  .clue-item.mine { border: 1px solid #6366f1; }
  .info-box { background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99,102,241,0.35);
              padding: 12px 14px; border-radius: 10px; font-size: 0.88rem; color: #c7d2fe; line-height: 1.5; margin-top: 12px; }
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
    <p class="subtitle">One short clue. Don't say the word itself.</p>
    <label for="clueInput">Your clue</label>
    <input type="text" id="clueInput" maxlength="80" placeholder="Type your clue..." autocomplete="off">
    <button id="clueSubmitBtn" onclick="submitClue()">Submit clue</button>
    <div class="error" id="clueError"></div>
    <div class="players-list" id="clueWaitingList"></div>
    <div class="progress" id="clueProgress"></div>
  </div>

  <!-- ===================== SUMMARY ===================== -->
  <div id="screen-summary" class="screen">
    <div class="round-header" id="summaryHeader">ROUND 1 COMPLETE</div>
    <h2>All clues</h2>
    <p class="subtitle">Read carefully. Then continue.</p>
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
    <div id="resultClues" style="margin-top:14px;"></div>
    <button onclick="playAgain()" id="playAgainBtn" style="display:none;">Play again (host)</button>
    <div class="progress" id="resultProgress">Waiting for host...</div>
  </div>
</div>

<script>
const STORAGE_KEY = 'imposter_session_v3';
let session = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
let current = null;
let pollTimer = null;
let selectedVote = null;

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

// ---------------- HOME ----------------
function showJoin() {
  $('joinBox').style.display = 'block';
  // Prefill from ?code=XXXXXX (used by QR links)
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

// ---------------- POLLING ----------------
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

// ---------------- ROUTER ----------------
function applyState(s) {
  current = s;
  const p = s.phase;
  if (p === 'lobby')        renderLobby(s);
  else if (p === 'reveal')  renderReveal(s);
  else if (p === 'clue')    renderClue(s);
  else if (p === 'summary') renderSummary(s);
  else if (p === 'vote')    renderVote(s);
  else if (p === 'result')  renderResult(s);
  startPolling();
}

// ---------------- LOBBY ----------------
function renderLobby(s) {
  show('screen-lobby');
  $('lobbyCode').textContent = s.code;
  // ---- QR code ----
  const joinUrl = location.origin + '/join?code=' + s.code;
  $('qrWrap').innerHTML = `<img alt="QR to join" src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(joinUrl)}">`;
  // ---- player list ----
  const list = $('lobbyPlayers');
  list.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'player-row' + (p.ready ? ' ready' : '');
    const mine = p.name === s.you.name;
    d.innerHTML = `<span>${esc(p.name)}${mine ? ' (you)' : ''}${p.name === s.host_name ? ' 👑' : ''}</span>
                   <span class="tag">${p.ready ? '✅ ready' : '⏳ not ready'}</span>`;
    list.appendChild(d);
  });
  $('lobbyProgress').textContent = `${s.players.length} player(s) — need 3+, up to 10`;
  $('lobbyReadyBtn').textContent = s.you.ready ? 'Not ready' : "I'm ready";
  $('lobbyReadyBtn').className = s.you.ready ? 'secondary' : '';

  // ---- host: imposter count selector ----
  const n = s.players.length;
  const maxK = Math.max(1, Math.floor((n - 1) / 2));
  const box = $('hostImposterBox');
  if (s.is_host) {
    box.style.display = 'block';
    const sel = $('numImposters');
    // rebuild options that are valid for n
    sel.innerHTML = '';
    for (let k = 1; k <= Math.min(3, maxK); k++) {
      const opt = document.createElement('option');
      opt.value = k; opt.textContent = k + ' imposter' + (k > 1 ? 's' : '');
      sel.appendChild(opt);
    }
    sel.value = String(Math.min(s.imposter_count, Math.min(3, maxK)));
    $('imposterNote').textContent = `Max ${maxK} with ${n} players (imposters must be fewer than half).`;
  } else {
    box.style.display = 'none';
  }

  // ---- start button ----
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

// ---------------- REVEAL ----------------
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
}

// ---------------- CLUE ----------------
function renderClue(s) {
  show('screen-clue');
  $('clueRoundHeader').textContent = `ROUND ${s.round} OF 2 — CLUES`;
  const mine = s.you.clue;
  if (mine) {
    $('clueInput').value = mine;
    $('clueInput').disabled = true;
    $('clueSubmitBtn').disabled = true;
    $('clueSubmitBtn').textContent = 'Clue submitted ✅';
  } else if (document.activeElement !== $('clueInput')) {
    $('clueInput').disabled = false;
    $('clueInput').value = '';
    $('clueSubmitBtn').disabled = false;
    $('clueSubmitBtn').textContent = 'Submit clue';
  }
  const wl = $('clueWaitingList');
  wl.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'player-row';
    d.innerHTML = `<span>${esc(p.name)}</span><span class="tag">${p.clue ? '✅ done' : '✏️ thinking...'}</span>`;
    wl.appendChild(d);
  });
  const done = s.players.filter(p => p.clue).length;
  $('clueProgress').textContent = `${done} / ${s.players.length} submitted`;
  if (!mine && !$('clueInput').disabled) setTimeout(() => $('clueInput').focus(), 100);
}

async function submitClue() {
  if (!session) return;
  $('clueError').textContent = '';
  const text = $('clueInput').value.trim();
  if (!text) { $('clueError').textContent = 'Please type a clue.'; return; }
  try { applyState(await api('clue', { ...session, text })); }
  catch (e) { $('clueError').textContent = e.message; }
}

// ---------------- SUMMARY ----------------
function renderSummary(s) {
  show('screen-summary');
  $('summaryHeader').textContent = `ROUND ${s.round} COMPLETE`;
  const list = $('summaryList');
  list.innerHTML = '';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'clue-item' + (p.name === s.you.name ? ' mine' : '');
    d.innerHTML = `<span class="name">${esc(p.name)}${p.name === s.you.name ? ' (you)' : ''}:</span> ${esc(p.clue || '—')}`;
    list.appendChild(d);
  });
  const btn = $('summaryNextBtn');
  if (s.is_host) {
    btn.style.display = 'block';
    btn.textContent = s.round === 1 ? 'Start Round 2 →' : 'Go to voting →';
  } else {
    btn.style.display = 'none';
  }
}

async function hostAdvance() {
  if (!session) return;
  try { applyState(await api('advance', session)); }
  catch (e) { alert(e.message); }
}

// ---------------- VOTE ----------------
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

// ---------------- RESULT (with winner banner) ----------------
function renderResult(s) {
  show('screen-result');
  const imposterNames = s.imposter_names || [];
  const youImp = !!s.you_are_imposter;

  // ---- WINNER BANNER ----
  const banner = $('resultBanner');
  let title = '', cls = '';
  if (s.result_banner === 'crew') {
    title = '🎉 CREW WINS!'; cls = 'crew';
  } else if (s.result_banner === 'imposter') {
    title = '😈 IMPOSTERS WIN!'; cls = 'imposter';
  } else {
    title = '🤝 TIE — NO ONE VOTED OUT'; cls = 'tie';
  }
  banner.textContent = title;
  banner.className = 'banner ' + cls;

  // ---- DETAILS ----
  let detail = '';
  if (s.vote_tie) {
    detail += `The vote was a tie — nobody was voted out.<br>`;
  } else if (s.voted_out_name) {
    detail += `Voted out: <strong>${esc(s.voted_out_name)}</strong>.<br>`;
  }
  detail += `Imposter${imposterNames.length>1?'s':''}: ` +
            imposterNames.map(n => `<strong>${esc(n)}</strong>`).join(', ') +
            `<br>Secret word: <strong>${esc(s.secret_word)}</strong>.`;
  if (youImp) detail += `<br><em>You were an imposter 😈</em>`;
  $('resultDetail').innerHTML = detail;

  // ---- VOTE TALLY ----
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

  // ---- IMPOSTER PILLS ----
  $('imposterBox').innerHTML =
    `<div class="round-header">IMPOSTER${imposterNames.length>1?'S':''}</div>` +
    imposterNames.map(n => `<span class="imposter-pill">🕵️ ${esc(n)}</span>`).join(' ');

  // ---- CLUES RECAP ----
  const rc = $('resultClues');
  rc.innerHTML = '<div class="round-header">ROUND 2 CLUES</div>';
  s.players.forEach(p => {
    const d = document.createElement('div');
    d.className = 'clue-item' + (p.name === s.you.name ? ' mine' : '');
    d.innerHTML = `<span class="name">${esc(p.name)}${p.name === s.you.name ? ' (you)' : ''}:</span> ${esc(p.clue || '—')}`;
    rc.appendChild(d);
  });

  $('playAgainBtn').style.display = s.is_host ? 'block' : 'none';
  $('resultProgress').textContent = s.is_host ? '' : 'Waiting for host to start a new round...';
}

async function playAgain() {
  if (!session) return;
  try { applyState(await api('reset', session)); }
  catch (e) { alert(e.message); }
}

// ---------------- BOOT ----------------
(async function boot() {
  if (session) {
    $('resumeHint').style.display = 'block';
    $('playerName').value = session.name || '';
    try { applyState(await api('state', session)); return; }
    catch (e) { saveSession(null); }
  }
  // QR deep-link: ?code=XXXXXX → open join box pre-filled
  const params = new URLSearchParams(location.search);
  if (params.get('code')) showJoin();
  show('screen-home');
})();

$('playerName').addEventListener('keydown', e => { if (e.key === 'Enter') $('joinCode').focus(); });
$('joinCode').addEventListener('keydown', e => { if (e.key === 'Enter') joinGame(); });
$('clueInput').addEventListener('keydown', e => { if (e.key === 'Enter') submitClue(); });
</script>
</body>
</html>
"""


def open_browser():
    webbrowser.open(f"http://localhost:{PORT}/")


class ThreadingServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    with ThreadingServer(("0.0.0.0", PORT), GameHandler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}/")
        print("Press Ctrl+C to stop.")
        if not os.environ.get("RENDER"):
            threading.Timer(1.0, open_browser).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


if __name__ == "__main__":
    main()
