import http.server
import socketserver
import webbrowser
import threading
import json
import random
import os  # <-- ADDED

# CHANGED: read PORT from env (Render injects this). Falls back to 8000 locally.
PORT = int(os.environ.get("PORT", 8000))

WORD_BANK = [
    # 1-10: Everyday objects
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

    # 11-20: Places
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

    # 21-30: Animals & nature
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

    # 31-40: Food & drink
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

    # 41-50: Transport, sports, people & concepts
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


MANIFEST_JSON = json.dumps({
    "name": "Imposter Word Game",
    "short_name": "Imposter",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#1e1b4b",
    "theme_color": "#4f46e5",
    "orientation": "portrait-primary",
    "description": "Party word game: find who the imposter is!",
    "icons": [
        {
            "src": "/icon.svg",
            "sizes": "192x192 512x512",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ]
}, indent=2)

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e1b4b"/>
      <stop offset="50%" stop-color="#312e81"/>
      <stop offset="100%" stop-color="#4c1d95"/>
    </linearGradient>
    <linearGradient id="glow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#c084fc"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="115" fill="url(#bg)"/>
  <circle cx="256" cy="256" r="195" fill="none" stroke="url(#glow)" stroke-width="8" opacity="0.35"/>
  <text x="50%" y="52%" font-size="210" text-anchor="middle" dominant-baseline="middle">🕵️</text>
  <text x="50%" y="82%" font-size="44" font-weight="900" font-family="system-ui, -apple-system, sans-serif" fill="#f8fafc" text-anchor="middle" letter-spacing="3">IMPOSTER</text>
</svg>"""

SW_JS = """const CACHE_NAME = 'imposter-v1';
const ASSETS = ['/', '/manifest.json', '/icon.svg'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => k !== CACHE_NAME && caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then((cached) => {
      return cached || fetch(e.request).catch(() => caches.match('/'));
    })
  );
});
"""

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Imposter Word Game</title>
<meta name="theme-color" content="#4f46e5">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Imposter">
<link rel="manifest" href="/manifest.json">
<link rel="icon" type="image/svg+xml" href="/icon.svg">
<link rel="apple-touch-icon" href="/icon.svg">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%);
    color: #f8fafc; min-height: 100vh;
    display: flex; align-items: center; justify-content: center; padding: 16px;
  }
  .app {
    width: 100%; max-width: 540px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 20px; padding: 28px 24px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5); backdrop-filter: blur(8px);
  }
  h1 { font-size: 1.6rem; text-align: center; margin-bottom: 6px; }
  h2 { font-size: 1.15rem; text-align: center; margin-bottom: 6px; }
  .subtitle { text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 20px; }
  .screen { display: none; }
  .screen.active { display: block; animation: fade 0.25s ease; }
  @keyframes fade { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
  label { display: block; font-size: 0.85rem; color: #cbd5e1; margin-bottom: 6px; margin-top: 16px; }
  select, input[type="number"], input[type="text"] {
    width: 100%; padding: 12px; border-radius: 10px;
    border: 1px solid #475569; background: #1e293b; color: #f8fafc; font-size: 1rem;
  }
  input[type="text"]:focus, select:focus, input[type="number"]:focus { outline: 2px solid #6366f1; }
  button {
    width: 100%; padding: 14px; margin-top: 16px; border: none;
    border-radius: 12px; background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white; font-size: 1rem; font-weight: 600; cursor: pointer;
    transition: transform 0.1s, opacity 0.2s;
  }
  button:hover { transform: translateY(-1px); opacity: 0.95; }
  button:active { transform: translateY(1px); }
  button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
  .role-card { text-align: center; padding: 32px 16px; border-radius: 16px; margin-top: 16px; }
  .role-card.crew { background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34,197,94,0.4); }
  .role-card.imposter { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239,68,68,0.4); }
  .role-label { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; }
  .role-word { font-size: 1.9rem; font-weight: 700; margin: 14px 0; word-break: break-word; }
  .role-card.crew .role-word { color: #86efac; }
  .role-card.imposter .role-word { color: #fca5a5; }
  .role-hint { font-size: 0.9rem; color: #cbd5e1; line-height: 1.4; white-space: pre-line; }
  .player-badge {
    display: inline-block; background: #4f46e5; padding: 6px 14px;
    border-radius: 999px; font-size: 0.85rem; font-weight: 600; margin-bottom: 16px;
  }
  .progress { text-align: center; font-size: 0.8rem; color: #94a3b8; margin-top: 14px; }
  .vote-list { display: grid; gap: 10px; margin-top: 16px; }
  .vote-btn {
    margin-top: 0; background: #1e293b; border: 1px solid #475569;
    font-weight: 500; text-align: left; padding-left: 18px;
  }
  .vote-btn:hover { background: #334155; }
  .vote-btn.selected { background: #6366f1; border-color: #818cf8; }
  .result-title { text-align: center; font-size: 1.5rem; margin-bottom: 10px; }
  .result-win { color: #86efac; }
  .result-lose { color: #fca5a5; }
  .result-tie { color: #fde68a; }
  .result-detail { text-align: center; color: #cbd5e1; font-size: 0.95rem; line-height: 1.7; margin-top: 12px; }
  .result-detail strong { color: #f8fafc; }
  .clue-item { padding: 10px 14px; background: #1e293b; border-radius: 10px; font-size: 0.9rem; color: #cbd5e1; line-height: 1.4; }
  .clue-item .name { color: #818cf8; font-weight: 600; }
  .info-box { background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99,102,241,0.35);
              padding: 12px 14px; border-radius: 10px; font-size: 0.88rem; color: #c7d2fe; line-height: 1.5; margin-top: 12px; }
  .round-header { text-align: center; margin: 4px 0 10px; font-size: 0.95rem; color: #a5b4fc; font-weight: 600; letter-spacing: 0.5px; }
  .error { color: #fca5a5; text-align: center; font-size: 0.85rem; margin-top: 10px; }
  .vote-summary { margin-top: 16px; display: grid; gap: 6px; }
  .vote-row { display: flex; justify-content: space-between; padding: 8px 12px; background: #1e293b;
              border-radius: 8px; font-size: 0.9rem; color: #cbd5e1; }
  .vote-row .count { color: #a5b4fc; font-weight: 600; }
</style>
</head>
<body>
<div class="app">
  <h1>🕵️ Imposter Word</h1>
  <p class="subtitle">One player gets a hint. Everyone else gets the word.</p>

  <!-- SETUP -->
  <div id="screen-setup" class="screen active">
    <label for="lang">Language / भाषा</label>
    <select id="lang">
      <option value="en">English</option>
      <option value="hi">हिन्दी (Hindi)</option>
    </select>
    <label for="numPlayers">Number of players (3–10)</label>
    <input type="number" id="numPlayers" min="3" max="10" value="4">
    <button onclick="startGame()">Start Game</button>
    <button id="installAppBtn" type="button" style="display:none; margin-top:12px; background:rgba(99,102,241,0.25); border:1px solid #818cf8; color:#c7d2fe;">📲 Install App</button>
    <div id="iosInstallHint" style="display:none; font-size:0.8rem; color:#94a3b8; margin-top:10px; text-align:center;">
      📱 On iPhone: Tap <strong>Share ⎋</strong> then <strong>Add to Home Screen ➕</strong>
    </div>
    <div id="setupError" class="error"></div>
  </div>

  <div id="screen-loading" class="screen">
    <p class="subtitle" style="margin-top:20px;">Dealing roles...</p>
  </div>

  <!-- PASS DEVICE -->
  <div id="screen-pass" class="screen">
    <div style="text-align:center;"><span class="player-badge" id="passName">Player 1</span></div>
    <p style="text-align:center; color:#cbd5e1; line-height:1.5;">
      Pass the device to <strong id="passNameInline">Player 1</strong>.<br>
      Make sure no one else is looking!
    </p>
    <button onclick="revealRole()">I'm ready — show my role</button>
  </div>

  <!-- ROLE -->
  <div id="screen-role" class="screen">
    <div style="text-align:center;"><span class="player-badge" id="roleName">Player 1</span></div>
    <div id="roleCard" class="role-card">
      <div class="role-label" id="roleLabel">Your word</div>
      <div class="role-word" id="roleWord">—</div>
      <div class="role-hint" id="roleHint"></div>
    </div>
    <button onclick="nextPlayer()">Hide &amp; continue</button>
    <div class="progress" id="roleProgress"></div>
  </div>

  <!-- CLUE INPUT -->
  <div id="screen-clue" class="screen">
    <div class="round-header" id="clueRoundHeader">ROUND 1 OF 2 — CLUES</div>
    <h2 id="clueTitle">Your turn to give a clue</h2>
    <p class="subtitle" id="clueSubtitle">Type one short clue about your word. Don't say the word itself.</p>
    <div style="text-align:center;"><span class="player-badge" id="cluePlayerName">Player 1</span></div>
    <label for="clueInput">Your clue</label>
    <input type="text" id="clueInput" maxlength="80" placeholder="Type your clue..." autocomplete="off">
    <button onclick="submitClue()">Submit clue</button>
    <div id="clueError" class="error"></div>
    <div class="progress" id="clueProgress"></div>
  </div>

  <!-- ROUND SUMMARY -->
  <div id="screen-round-summary" class="screen">
    <div class="round-header" id="summaryRoundHeader">ROUND 1 COMPLETE</div>
    <h2 id="summaryTitle">All clues for this round</h2>
    <p class="subtitle">Everyone reads the clues before the next round.</p>
    <div id="summaryList" style="display:grid;gap:8px;margin-top:12px;"></div>
    <button id="summaryBtn" onclick="advanceRound()">Next round →</button>
  </div>

  <!-- VOTE -->
  <div id="screen-vote" class="screen">
    <h2>Voting — everyone votes</h2>
    <p class="subtitle">Each player will now vote privately. Pass the device between voters.</p>
    <div style="text-align:center;"><span class="player-badge" id="voteVoterName">Player 1</span></div>
    <label>Who do you think is the imposter?</label>
    <div id="voteList" class="vote-list"></div>
    <button id="voteSubmitBtn" onclick="submitVote()" disabled>Submit vote</button>
    <div class="progress" id="voteProgress"></div>
  </div>

  <!-- RESULT -->
  <div id="screen-result" class="screen">
    <div class="result-title" id="resultTitle">—</div>
    <div class="result-detail" id="resultDetail"></div>
    <div id="voteSummaryBox" style="margin-top:16px;">
      <div class="round-header">VOTE TALLY</div>
      <div id="voteSummary" class="vote-summary"></div>
    </div>
    <button onclick="resetGame()">Play again</button>
  </div>
</div>

<script>
const WORD_BANK_DATA = __WORD_BANK_JSON__;

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW registration error:', err));
  });
}

let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const btn = document.getElementById('installAppBtn');
  if (btn) btn.style.display = 'block';
});

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('installAppBtn');
  if (btn) {
    btn.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        if (outcome === 'accepted') {
          btn.style.display = 'none';
        }
        deferredPrompt = null;
      }
    });
  }
  const isIos = () => /iphone|ipad|ipod/.test(window.navigator.userAgent.toLowerCase());
  const isInStandalone = () => ('standalone' in window.navigator) && (window.navigator.standalone);
  if (isIos() && !isInStandalone()) {
    const iosHint = document.getElementById('iosInstallHint');
    if (iosHint) iosHint.style.display = 'block';
  }
});

let state = {};
const $ = id => document.getElementById(id);
const show = id => {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  $(id).classList.add('active');
};

const UI_TEXT = {
  en: {
    crewRole: "Your word", imposterRole: "You are the IMPOSTER!",
    crewHint: "Describe it without saying the word!",
    imposterHint: "Blend in — don't get caught!", hintPrefix: "Hint: ",
    progress: (i, n) => `Player ${i} of ${n}`,
    resultCrew: "🎉 Crew wins! The imposter was caught.",
    resultImposter: "😈 Imposter wins! They escaped detection.",
    resultTie: "🤝 It's a tie! No clear majority.",
    imposterWas: "The imposter was", secretWas: "The secret word was",
    roundHeader: (r, total) => `ROUND ${r} OF ${total} — CLUES`,
    roundSummary: (r) => `ROUND ${r} COMPLETE`,
    cluePlaceholder: "Type your clue..."
  },
  hi: {
    crewRole: "आपका शब्द", imposterRole: "आप IMPOSTER हैं!",
    crewHint: "शब्द कहे बिना इसे बताएं!",
    imposterHint: "घुल-मिल जाएं — पकड़े न जाएं!", hintPrefix: "संकेत: ",
    progress: (i, n) => `खिलाड़ी ${i} / ${n}`,
    resultCrew: "🎉 क्रू जीत गया! इम्पोस्टर पकड़ा गया।",
    resultImposter: "😈 इम्पोस्टर जीत गया! वह बच निकला।",
    resultTie: "🤝 बराबरी! कोई स्पष्ट बहुमत नहीं।",
    imposterWas: "इम्पोस्टर था", secretWas: "गुप्त शब्द था",
    roundHeader: (r, total) => `राउंड ${r} / ${total} — संकेत`,
    roundSummary: (r) => `राउंड ${r} पूरा`,
    cluePlaceholder: "अपना संकेत लिखें..."
  }
};

const NUM_CLUE_ROUNDS = 2;

async function startGame() {
  const lang = $('lang').value;
  const n = parseInt($('numPlayers').value, 10);
  if (isNaN(n) || n < 3 || n > 10) {
    $('setupError').textContent = "Please choose 3–10 players.";
    return;
  }
  $('setupError').textContent = '';
  show('screen-loading');

  let data = null;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1500);
    const res = await fetch('/api/new_round', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang, num_players: n }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (res.ok) {
      data = await res.json();
    }
  } catch (e) {
    // Server is asleep or offline - proceed directly to offline fallback
  }

  if (!data || !data.word) {
    const bank = (typeof WORD_BANK_DATA !== 'undefined' && WORD_BANK_DATA.length) ? WORD_BANK_DATA : [];
    const pair = bank.length > 0 ? bank[Math.floor(Math.random() * bank.length)][lang] : { word: "Elephant", imposter_hint: "A large animal" };
    data = {
      word: pair.word,
      imposter_hint: pair.imposter_hint,
      imposter_index: Math.floor(Math.random() * n),
      players: Array.from({ length: n }, (_, i) => `Player ${i + 1}`)
    };
  }

  state = {
    lang,
    word: data.word,
    imposterHint: data.imposter_hint,
    imposterIndex: data.imposter_index,
    players: data.players,
    currentRole: 0,
    round: 1,
    cluePlayer: 0,
    clues: {},           // { round: [ {player, text}, ... ] }
    voteVoter: 0,
    votes: [],           // [ {voter, target} ]
    selectedVote: null
  };
  state.clues[1] = [];
  state.clues[2] = [];
  goToPass();
}

function goToPass() {
  const name = state.players[state.currentRole];
  $('passName').textContent = name;
  $('passNameInline').textContent = name;
  show('screen-pass');
}

function revealRole() {
  const t = UI_TEXT[state.lang];
  const i = state.currentRole;
  const isImposter = i === state.imposterIndex;
  $('roleName').textContent = state.players[i];
  const card = $('roleCard');
  card.className = 'role-card ' + (isImposter ? 'imposter' : 'crew');
  if (isImposter) {
    $('roleLabel').textContent = t.imposterRole;
    $('roleWord').textContent = '🤫';
    $('roleHint').textContent = t.hintPrefix + state.imposterHint + '\n' + t.imposterHint;
  } else {
    $('roleLabel').textContent = t.crewRole;
    $('roleWord').textContent = state.word;
    $('roleHint').textContent = t.crewHint;
  }
  $('roleProgress').textContent = t.progress(i + 1, state.players.length);
  show('screen-role');
}

function nextPlayer() {
  state.currentRole++;
  if (state.currentRole < state.players.length) {
    goToPass();
  } else {
    showClueScreen();
  }
}

function showClueScreen() {
  const t = UI_TEXT[state.lang];
  $('clueRoundHeader').textContent = t.roundHeader(state.round, NUM_CLUE_ROUNDS);
  $('cluePlayerName').textContent = state.players[state.cluePlayer];
  $('clueTitle').textContent = `Round ${state.round}: give your clue`;
  $('clueSubtitle').textContent = "Type one short clue. Don't say the word itself.";
  $('clueInput').value = '';
  $('clueInput').placeholder = t.cluePlaceholder;
  $('clueError').textContent = '';
  $('clueProgress').textContent = t.progress(state.cluePlayer + 1, state.players.length);
  show('screen-clue');
  setTimeout(() => $('clueInput').focus(), 50);
}

function submitClue() {
  const text = $('clueInput').value.trim();
  if (!text) {
    $('clueError').textContent = "Please type a clue.";
    return;
  }
  if (text.length > 80) {
    $('clueError').textContent = "Clue is too long (max 80).";
    return;
  }
  const playerName = state.players[state.cluePlayer];
  state.clues[state.round].push({ player: playerName, text });
  state.cluePlayer++;

  if (state.cluePlayer < state.players.length) {
    showClueScreen();
  } else {
    showRoundSummary();
  }
}

function showRoundSummary() {
  const t = UI_TEXT[state.lang];
  $('summaryRoundHeader').textContent = t.roundSummary(state.round);
  $('summaryTitle').textContent = `Clues for Round ${state.round}`;
  const list = $('summaryList');
  list.innerHTML = '';
  state.clues[state.round].forEach(c => {
    const div = document.createElement('div');
    div.className = 'clue-item';
    div.innerHTML = `<span class="name">${c.player}:</span> ${escapeHtml(c.text)}`;
    list.appendChild(div);
  });
  $('summaryBtn').textContent = state.round < NUM_CLUE_ROUNDS
    ? `Start Round ${state.round + 1} →`
    : 'All clues done — go to voting →';
  show('screen-round-summary');
}

function advanceRound() {
  if (state.round < NUM_CLUE_ROUNDS) {
    state.round++;
    state.cluePlayer = 0;
    showClueScreen();
  } else {
    startVoting();
  }
}

function startVoting() {
  state.voteVoter = 0;
  state.votes = [];
  state.selectedVote = null;
  showVoteScreen();
}

function showVoteScreen() {
  const voter = state.players[state.voteVoter];
  $('voteVoterName').textContent = voter;
  $('voteProgress').textContent = `Voter ${state.voteVoter + 1} of ${state.players.length}`;
  state.selectedVote = null;
  $('voteSubmitBtn').disabled = true;

  const list = $('voteList');
  list.innerHTML = '';
  state.players.forEach((p, i) => {
    if (p === voter) return; // can't vote for yourself
    const btn = document.createElement('button');
    btn.className = 'vote-btn';
    btn.textContent = p;
    btn.dataset.idx = i;
    btn.onclick = () => {
      document.querySelectorAll('.vote-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      state.selectedVote = i;
      $('voteSubmitBtn').disabled = false;
    };
    list.appendChild(btn);
  });
  show('screen-vote');
}

function submitVote() {
  if (state.selectedVote === null) return;
  state.votes.push({
    voter: state.players[state.voteVoter],
    target: state.players[state.selectedVote]
  });
  state.voteVoter++;
  if (state.voteVoter < state.players.length) {
    showVoteScreen();
  } else {
    resolveVotes();
  }
}

function resolveVotes() {
  const t = UI_TEXT[state.lang];
  // Tally
  const tally = {};
  state.players.forEach(p => tally[p] = 0);
  state.votes.forEach(v => tally[v.target]++);

  // Find max
  let maxCount = 0;
  let topPlayers = [];
  Object.entries(tally).forEach(([p, c]) => {
    if (c > maxCount) { maxCount = c; topPlayers = [p]; }
    else if (c === maxCount && c > 0) { topPlayers.push(p); }
  });

  const imposterName = state.players[state.imposterIndex];
  const caught = topPlayers.length === 1 && topPlayers[0] === imposterName;
  const tie = topPlayers.length > 1;

  const title = $('resultTitle');
  if (tie) {
    title.textContent = t.resultTie;
    title.className = 'result-title result-tie';
  } else if (caught) {
    title.textContent = t.resultCrew;
    title.className = 'result-title result-win';
  } else {
    title.textContent = t.resultImposter;
    title.className = 'result-title result-lose';
  }

  let detailHtml = `${t.imposterWas} <strong>${imposterName}</strong>.<br>${t.secretWas} <strong>${state.word}</strong>.`;
  if (tie) {
    detailHtml = `Tie between: <strong>${topPlayers.join(', ')}</strong>.<br>` +
                 `${t.imposterWas} <strong>${imposterName}</strong>.<br>${t.secretWas} <strong>${state.word}</strong>.`;
  }
  $('resultDetail').innerHTML = detailHtml;

  // Vote tally display
  const summary = $('voteSummary');
  summary.innerHTML = '';
  Object.entries(tally).sort((a,b) => b[1]-a[1]).forEach(([p, c]) => {
    const row = document.createElement('div');
    row.className = 'vote-row';
    row.innerHTML = `<span>${p}${p === imposterName ? ' 🤫' : ''}</span><span class="count">${c} vote${c===1?'':'s'}</span>`;
    summary.appendChild(row);
  });

  show('screen-result');
}

function resetGame() {
  show('screen-setup');
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, ch => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[ch]));
}

$('numPlayers').addEventListener('keydown', e => { if (e.key === 'Enter') startGame(); });
$('clueInput').addEventListener('keydown', e => { if (e.key === 'Enter') submitClue(); });
</script>
</body>
</html>
"""


class GameHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            rendered = HTML_PAGE.replace("__WORD_BANK_JSON__", json.dumps(WORD_BANK, ensure_ascii=False))
            self._send(200, rendered.encode("utf-8"), "text/html; charset=utf-8")
        elif self.path == "/manifest.json":
            self._send(200, MANIFEST_JSON.encode("utf-8"), "application/manifest+json; charset=utf-8")
        elif self.path == "/sw.js":
            self._send(200, SW_JS.encode("utf-8"), "application/javascript; charset=utf-8")
        elif self.path == "/icon.svg":
            self._send(200, ICON_SVG.encode("utf-8"), "image/svg+xml; charset=utf-8")
        else:
            self._send(404, b"Not found", "text/plain")

    def do_POST(self):
        if self.path == "/api/new_round":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw)
                lang = payload.get("lang", "en")
                num_players = int(payload.get("num_players", 4))
            except (ValueError, TypeError):
                self._send(400, b'{"error":"bad request"}', "application/json")
                return

            if lang not in ("en", "hi"):
                lang = "en"
            if not (3 <= num_players <= 10):
                num_players = 4

            entry = random.choice(WORD_BANK)[lang]
            imposter_index = random.randrange(num_players)
            response = {
                "word": entry["word"],
                "imposter_hint": entry["imposter_hint"],
                "imposter_index": imposter_index,
                "players": [f"Player {i + 1}" for i in range(num_players)],
            }
            body = json.dumps(response, ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
        else:
            self._send(404, b"Not found", "text/plain")


def open_browser():
    webbrowser.open(f"http://localhost:{PORT}/")


def main():
    socketserver.TCPServer.allow_reuse_address = True
    # CHANGED: bind to 0.0.0.0 so Render's router can reach the process.
    with socketserver.TCPServer(("0.0.0.0", PORT), GameHandler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}/")
        print("Press Ctrl+C to stop.")
        # CHANGED: only open a browser locally; on Render this would just fail silently.
        if not os.environ.get("RENDER"):
            threading.Timer(1.0, open_browser).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


if __name__ == "__main__":
    main()
