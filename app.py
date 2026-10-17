
from flask import Flask, render_template_string, request, redirect, url_for
from flask_socketio import SocketIO, join_room
import secrets
import string
import time
app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)
socketio = SocketIO(app)

rooms = {}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WatchParty | Movie Nights, Together</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #080b18;
    --panel: rgba(22, 25, 48, .84);
    --border: rgba(154, 120, 255, .25);
    --purple: #9b6cff;
    --pink: #ec55d9;
    --blue: #2588ff;
    --muted: #a7aecb;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Inter, Arial, sans-serif;
    color: #f7f7ff;
    background:
      radial-gradient(ellipse at 75% 15%, #251342 0%, transparent 38%),
      radial-gradient(ellipse at 5% 40%, #101e45 0%, transparent 40%),
      var(--bg);
    min-height: 100vh;
}
nav {
    height: 76px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 6%;
    border-bottom: 1px solid rgba(255,255,255,.09);
    background: rgba(8,11,24,.78);
    gap: 18px;
}
.logo { font-size: 25px; font-weight: 800; white-space: nowrap; }
.logo span {
    background: linear-gradient(90deg, #a679ff, #f05edc);
    color: transparent;
    background-clip: text;
}
.navlinks { display: flex; gap: 30px; color: #c3c5de; font-size: 14px; }
.navlinks a { color: inherit; text-decoration: none; }
.navlinks a:hover { color: white; }
.pill {
    border: 1px solid var(--border);
    color: #d4c1ff;
    padding: 10px 15px;
    border-radius: 30px;
    font-size: 12px;
    background: rgba(120,80,220,.12);
}
main { max-width: 1200px; margin: auto; padding: 55px 25px 35px; }
.hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: 30px;
    margin-bottom: 48px;
}
.eyebrow {
    display: inline-block;
    background: rgba(112,67,255,.18);
    border: 1px solid var(--border);
    padding: 10px 15px;
    border-radius: 30px;
    color: #d0b9ff;
    font-size: 12px;
    margin-bottom: 18px;
}
h1 { font-size: clamp(38px, 5vw, 64px); line-height: 1.08; margin: 0 0 20px; letter-spacing: -2.5px; }
.gradient {
    background: linear-gradient(90deg, #6bb8ff, #b16cff, #f16bdc);
    color: transparent;
    background-clip: text;
}
.subtitle { color: var(--muted); line-height: 1.8; max-width: 500px; font-size: 15px; }
.hero-art {
    min-height: 300px;
    border: 1px solid var(--border);
    border-radius: 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background:
      radial-gradient(circle at 50% 35%, rgba(143,83,255,.38), transparent 48%),
      linear-gradient(135deg, #16172e, #0c1021);
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 65px rgba(104,50,220,.12);
}
.hero-art:before, .hero-art:after {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    border: 1px solid rgba(190,145,255,.15);
    border-radius: 50%;
}
.hero-art:after { width: 290px; height: 290px; }
.tv { font-size: 100px; filter: drop-shadow(0 0 25px #925aff); animation: float 3s ease-in-out infinite; }
@keyframes float { 50% { transform: translateY(-8px); } }
.art-label { color: #d6c9ff; font-size: 14px; margin-top: 10px; }
.bubble {
    position: absolute;
    background: #20223d;
    border: 1px solid #3a3c61;
    border-radius: 14px;
    padding: 10px 13px;
    font-size: 12px;
}
.b1 { top: 22px; right: 18px; }
.b2 { bottom: 25px; left: 16px; }
.forms {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 22px;
}
.card {
    position: relative;
    overflow: hidden;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 28px;
    backdrop-filter: blur(14px);
    transition: transform .2s, border-color .2s;
}
.card:hover { transform: translateY(-4px); border-color: #9264ff; }
.card.join { border-color: rgba(49,137,255,.4); }
.card h2 { font-size: 23px; margin: 18px 0 10px; }
.card p { color: var(--muted); font-size: 13px; line-height: 1.7; }
.card-icon { font-size: 38px; }
.tag {
    display: inline-block;
    background: rgba(146,99,255,.15);
    color: #d3beff;
    padding: 8px 12px;
    border-radius: 30px;
    font-size: 11px;
}
.join .tag { background: rgba(36,135,255,.15); color: #a8d2ff; }
input {
    display: block;
    width: 100%;
    margin-top: 12px;
    background: rgba(8,11,24,.65);
    border: 1px solid #373a5b;
    color: white;
    padding: 15px;
    border-radius: 12px;
    outline: none;
    font: inherit;
    font-size: 13px;
}
input:focus { border-color: #a17aff; box-shadow: 0 0 0 3px rgba(150,100,255,.1); }
input::placeholder { color: #858ba9; }
button {
    width: 100%;
    border: 0;
    border-radius: 12px;
    padding: 15px;
    margin-top: 15px;
    background: linear-gradient(100deg, #d14bed, #754bff);
    color: white;
    font-weight: 700;
    font: inherit;
    font-size: 13px;
    cursor: pointer;
    transition: filter .2s, transform .2s;
}
button:hover { filter: brightness(1.15); transform: translateY(-1px); }
.join button { background: linear-gradient(100deg, #2897ff, #1763f6); }
.features {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 18px;
    text-align: center;
    padding: 35px 0 15px;
    margin-top: 42px;
    border-top: 1px solid rgba(255,255,255,.09);
}
.feature-icon { font-size: 27px; }
.feature h3 { font-size: 13px; }
.feature p { color: var(--muted); font-size: 11px; line-height: 1.7; }
footer { text-align: center; color: #777f9e; font-size: 12px; padding: 25px; }
.notice {
    background: rgba(25,190,130,.1);
    border: 1px solid rgba(25,190,130,.3);
    padding: 13px 16px;
    border-radius: 12px;
    margin-bottom: 20px;
    color: #9af0cd;
    font-size: 13px;
}
@media(max-width:750px) {
    .navlinks, nav .pill { display: none; }
    .hero, .forms { grid-template-columns: 1fr; }
    main { padding-top: 35px; }
    .hero-art { min-height: 250px; }
    .features { grid-template-columns: repeat(2, 1fr); }
    h1 { letter-spacing: -1.5px; }
}

/* Modern WatchParty header */
.room-header {
    padding: 17px 6%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
    background: rgba(8, 11, 24, 0.88);
    border-bottom: 1px solid rgba(155, 108, 255, 0.22);
    backdrop-filter: blur(20px);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-icon {
    width: 44px;
    height: 44px;
    display: grid;
    place-items: center;
    border-radius: 14px;
    background: linear-gradient(135deg, #a34df0, #704cff);
    color: white;
    font-size: 19px;
    box-shadow: 0 5px 22px rgba(125, 75, 255, 0.3);
}

.brand .logo {
    font-size: 23px;
    line-height: 1.2;
    color: #d3baff;
}

.brand-tagline {
    margin-top: 5px;
    font-size: 9px;
    letter-spacing: 1.8px;
    color: #9299bc;
}

.header-details {
    display: flex;
    align-items: center;
    gap: 24px;
}

.header-room-code,
.header-host {
    display: flex;
    align-items: center;
    gap: 10px;
}

.header-room-code {
    padding: 10px 15px;
    border: 1px solid rgba(155, 108, 255, 0.28);
    border-radius: 12px;
    background: rgba(155, 108, 255, 0.09);
}

.header-room-code strong {
    color: #d3baff;
    letter-spacing: 2px;
    font-size: 15px;
}

.header-host {
    gap: 9px;
}

.host-crown {
    font-size: 23px;
}

.header-label {
    display: block;
    margin-bottom: 4px;
    color: #9299bc;
    font-size: 9px;
    letter-spacing: 1.5px;
}

.header-host strong {
    font-size: 13px;
    color: #f4f0ff;
    overflow-wrap: anywhere;
}

@media (max-width: 560px) {
    .room-header {
        padding: 15px 5%;
        align-items: flex-start;
    }

    .header-details {
        width: 100%;
        justify-content: space-between;
        gap: 12px;
    }

    .brand .logo {
        font-size: 21px;
    }

    .header-room-code {
        padding: 9px 11px;
    }
}

/* Premium watch screen */
.row > .panel:first-child {
    min-width: 0;
    background:
        radial-gradient(
            ellipse at top left,
            rgba(131, 78, 226, 0.12),
            transparent 55%
        ),
        rgba(22, 25, 48, 0.9);
    border-color: rgba(155, 108, 255, 0.3);
}

.row > .panel:first-child h2 {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    font-size: 23px;
}

#player {
    display: block;
    width: 100%;
    aspect-ratio: 16 / 9;
    max-height: 520px;
    object-fit: contain;
    background: #03040a;
    border: 1px solid rgba(185, 155, 255, 0.2);
    border-radius: 16px;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
}

#nowPlaying {
    margin-top: 18px;
    padding: 13px 15px;
    background: rgba(155, 108, 255, 0.1);
    border: 1px solid rgba(155, 108, 255, 0.2);
    border-radius: 12px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

.row > .panel:first-child p small {
    display: block;
    margin-top: 12px;
    line-height: 1.7;
    color: #a7aecb;
}

/* Modern live party chat */
#messages {
    height: 280px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 16px;
    background: rgba(5, 7, 18, 0.72);
    border: 1px solid rgba(155, 108, 255, 0.18);
    border-radius: 15px;
    scrollbar-width: thin;
    scrollbar-color: #6545a5 transparent;
    overflow-wrap: anywhere;
}

#chat {
    margin-top: 14px;
    margin-bottom: 10px;
}

#chat:focus {
    border-color: #a477ff;
    box-shadow: 0 0 0 3px rgba(155, 108, 255, 0.13);
}

.row > .panel:nth-child(2) h2 {
    margin-bottom: 18px;
}

.row > .panel:nth-child(2) h3 {
    margin-top: 24px;
    margin-bottom: 12px;
    font-size: 15px;
    color: #d8c7ff;
}

.row > .panel:nth-child(2) button {
    min-height: 38px;
}

#reaction {
    min-height: 44px;
    padding: 8px 10px;
    border-radius: 12px;
    background: rgba(155, 108, 255, 0.08);
    border: 1px solid rgba(155, 108, 255, 0.13);
}

#participants {
    padding: 13px;
    background: rgba(5, 7, 18, 0.48);
    border: 1px solid rgba(155, 108, 255, 0.16);
    border-radius: 12px;
    color: #c5cbe5;
    font-size: 13px;
    line-height: 1.8;
    overflow-wrap: anywhere;
}

/* Premium shared playlist */
.row > .panel:nth-child(3) {
    min-width: 0;
    background:
        radial-gradient(
            ellipse at top right,
            rgba(236, 85, 217, 0.08),
            transparent 45%
        ),
        rgba(22, 25, 48, 0.9);
}

.row > .panel:nth-child(3) h2 {
    margin-bottom: 18px;
}

.row > .panel:nth-child(3) > small {
    display: block;
    margin: 12px 0;
    line-height: 1.6;
}

#playlistLeaderboard {
    background: linear-gradient(
        120deg,
        rgba(111, 65, 190, 0.32),
        rgba(236, 85, 217, 0.12)
    ) !important;
    border: 1px solid rgba(184, 139, 255, 0.35);
    border-radius: 15px !important;
    padding: 17px !important;
    margin: 16px 0 !important;
    box-shadow: 0 8px 24px rgba(90, 45, 160, 0.12);
}

#playlistLeaderboard strong {
    color: #e0caff;
    font-size: 15px;
}

#leaderboardResult {
    line-height: 1.7;
    overflow-wrap: anywhere;
}

#playlistUrl {
    margin-top: 16px;
}

#playlistStatus {
    font-size: 13px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

#playlistItems {
    list-style: none;
    padding: 0;
    margin: 18px 0;
}

#playlistItems li {
    margin: 10px 0;
    padding: 14px;
    border: 1px solid rgba(155, 108, 255, 0.17);
    border-radius: 13px;
    background: rgba(7, 9, 22, 0.56);
    line-height: 1.7;
    overflow-wrap: anywhere;
    transition: border-color 0.2s, background 0.2s;
}

#playlistItems li:hover {
    border-color: rgba(171, 126, 255, 0.48);
    background: rgba(31, 23, 56, 0.7);
}

#votingStatus {
    padding: 13px 15px;
    background: rgba(155, 108, 255, 0.09);
    border: 1px solid rgba(155, 108, 255, 0.19);
    border-radius: 12px;
    line-height: 1.7;
    overflow-wrap: anywhere;
}

/* SyncSense and connection status */
#status,
#syncStatus {
    display: block;
    padding: 12px 14px;
    margin: 12px 0;
    border-radius: 12px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

#status {
    background: rgba(52, 211, 153, 0.08);
    border: 1px solid rgba(52, 211, 153, 0.2);
    color: #9af0cd;
}

#syncStatus {
    background: rgba(155, 108, 255, 0.09);
    border: 1px solid rgba(155, 108, 255, 0.2);
    color: #d0baff;
}

/* Movie night countdown */
#countdownPanel {
    margin-top: 20px !important;
    padding: 22px !important;
    text-align: center;
    background:
        radial-gradient(
            ellipse at top,
            rgba(155, 108, 255, 0.2),
            transparent 70%
        ),
        rgba(9, 11, 27, 0.7);
    border: 1px solid rgba(155, 108, 255, 0.28);
    border-radius: 18px;
}

#countdownPanel h2 {
    margin-bottom: 14px;
}

#countdownDisplay {
    font-size: clamp(30px, 5vw, 44px) !important;
    font-weight: 800;
    letter-spacing: 1px;
    color: #d2b5ff !important;
    margin: 18px 0;
    overflow-wrap: anywhere;
}

#countdownMessage {
    font-size: 13px;
    line-height: 1.7;
    color: #b9aed9 !important;
    margin-bottom: 0;
}




</style>
</head>
<body>
<nav>
    <div class="logo">▣ Watch<span>Party</span></div>
    <div class="navlinks">
        <a href="/">Home</a>
        <a href="#features">Discover</a>
        <a href="#rooms">My Rooms</a>
    </div>
    <div class="pill">👥 Movie nights. Better together.</div>
</nav>

<main>
    {% if message %}
    <div class="notice">{{ message }}</div>
    {% endif %}

    <section class="hero">
        <div>
            <div class="eyebrow">✨ REAL-TIME · SYNCHRONIZED · TOGETHER</div>
            <h1>Movies are better <span class="gradient">together.</span></h1>
            <p class="subtitle">
                Create a room, invite your friends, and experience movie night
                with synchronized playback, live chat, reactions and more.
            </p>
            <p class="subtitle">🍿 &nbsp; Your people. Your movie. One shared moment.</p>
        </div>
        <div class="hero-art">
            <div class="bubble b1">😍 This is amazing!</div>
            <div class="tv">📺</div>
            <div class="art-label">YOUR NEXT MOVIE NIGHT STARTS HERE</div>
            <div class="bubble b2">❤️ 😂 🔥 &nbsp; Live reactions</div>
        </div>
    </section>

    <section class="forms" id="rooms">
        <div class="card">
            <span class="tag">👑 BE THE HOST</span>
            <div class="card-icon">🎬</div>
            <h2>Create a Room</h2>
            <p>Start a new watch party and become its host. Invite your friends using a unique room code.</p>
            <form action="/create" method="POST">
                <input name="username" placeholder="👤  Your name" required maxlength="30">
                <button type="submit">Create Watch Party &nbsp; →</button>
            </form>
        </div>

        <div class="card join">
            <span class="tag">🔗 JOIN A ROOM</span>
            <div class="card-icon">🍿</div>
            <h2>Join Your Friends</h2>
            <p>Have a room code? Enter it below and join your friends' movie night.</p>
            <form action="/join" method="POST">
                <input name="username" placeholder="👤  Your name" required maxlength="30">
                <input name="room_code" placeholder="🔑  Room code (e.g. ABC123)" required maxlength="8">
                <button type="submit">Join Watch Party &nbsp; →</button>
            </form>
        </div>
    </section>

    <section class="features" id="features">
        <div class="feature"><div class="feature-icon">▶️</div><h3>Synchronized Playback</h3><p>Watch together, in sync.</p></div>
        <div class="feature"><div class="feature-icon">💬</div><h3>Live Chat & Reactions</h3><p>React together in real time.</p></div>
        <div class="feature"><div class="feature-icon">🔎</div><h3>Discover Movies</h3><p>Find your next favorite.</p></div>
        <div class="feature"><div class="feature-icon">📋</div><h3>Shared Playlists</h3><p>Build a list as a group.</p></div>
        <div class="feature"><div class="feature-icon">📊</div><h3>Group Polls</h3><p>Choose what to watch.</p></div>
    </section>
</main>
<footer>Made for movie nights with your favorite people ✨</footer>
</body>
</html>
"""


ROOM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WatchParty | Room {{ code }}</title>
<style>

* {
    box-sizing: border-box;
}

:root {
    --bg: #080b18;
    --panel: rgba(22, 25, 48, 0.82);
    --border: rgba(154, 120, 255, 0.24);
    --purple: #9b6cff;
    --pink: #ec55d9;
    --muted: #a7aecb;
}

body {
    margin: 0;
    color: #f7f7ff;
    font-family: Inter, Arial, sans-serif;
    background:
        radial-gradient(ellipse at 80% 0%, #281443 0%, transparent 38%),
        radial-gradient(ellipse at 0% 45%, #101e45 0%, transparent 42%),
        var(--bg);
    min-height: 100vh;
}

header {
    padding: 20px 6%;
    border-bottom: 1px solid rgba(255, 255, 255, 0.09);
    background: rgba(8, 11, 24, 0.78);
    backdrop-filter: blur(18px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    position: sticky;
    top: 0;
    z-index: 10;
}

.logo {
    font-size: 25px;
    font-weight: 800;
    color: #c6a5ff;
    letter-spacing: -0.7px;
}

main {
    max-width: 1240px;
    margin: auto;
    padding: 32px 24px 50px;
}

.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 22px;
    backdrop-filter: blur(16px);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.16);
    transition: border-color 0.2s, transform 0.2s;
}

.panel:hover {
    border-color: rgba(171, 126, 255, 0.42);
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

h1 {
    font-size: clamp(28px, 4vw, 40px);
    margin-top: 0;
}

h2 {
    font-size: 22px;
    margin-top: 0;
}

p {
    line-height: 1.65;
}

.row {
    display: grid;
    grid-template-columns: minmax(0, 1.7fr) minmax(280px, 1fr);
    gap: 22px;
    align-items: start;
}

video {
    width: 100%;
    max-height: 520px;
    background: #000;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    display: block;
}

.code {
    font-size: clamp(28px, 5vw, 38px);
    letter-spacing: 6px;
    color: #c3a5ff;
    font-weight: 800;
    margin: 14px 0;
}

input {
    display: block;
    width: 100%;
    padding: 14px 15px;
    background: rgba(8, 11, 24, 0.72);
    color: white;
    border: 1px solid #373a5b;
    border-radius: 12px;
    margin: 9px 0;
    outline: none;
    font: inherit;
    font-size: 14px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

input:focus {
    border-color: var(--purple);
    box-shadow: 0 0 0 3px rgba(155, 108, 255, 0.14);
}

input::placeholder {
    color: #858ba9;
}

button {
    padding: 12px 17px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 11px;
    background: linear-gradient(110deg, #a34df0, #704cff);
    color: white;
    cursor: pointer;
    margin: 5px 3px 5px 0;
    font: inherit;
    font-size: 13px;
    font-weight: 700;
    transition: filter 0.2s, transform 0.2s, box-shadow 0.2s;
}

button:hover {
    filter: brightness(1.12);
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(125, 75, 255, 0.22);
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

a {
    color: #c5adff;
}

#messages {
    height: 240px;
    overflow-y: auto;
    background: rgba(8, 11, 24, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.07);
    padding: 14px;
    border-radius: 13px;
    font-size: 14px;
    line-height: 1.7;
}

#status {
    color: #9af0cd;
    font-size: 13px;
}

#syncStatus {
    color: #c5adff;
    font-size: 13px;
}

#reaction {
    font-size: 26px;
    margin-top: 12px;
    min-height: 34px;
}

#playlistItems {
    padding-left: 24px;
}

#playlistItems li {
    margin: 12px 0;
    padding: 10px;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    background: rgba(8, 11, 24, 0.38);
    overflow-wrap: anywhere;
}

#playlistLeaderboard {
    background: linear-gradient(
        120deg,
        rgba(111, 65, 190, 0.3),
        rgba(236, 85, 217, 0.1)
    ) !important;
    border: 1px solid var(--border);
    padding: 15px !important;
    border-radius: 14px !important;
}

small {
    color: var(--muted);
}

@media (max-width: 800px) {
    .row {
        grid-template-columns: 1fr;
    }

    main {
        padding: 22px 14px 35px;
    }

    .panel {
        padding: 18px;
    }

    header {
        padding: 17px 5%;
    }
}

@media (max-width: 480px) {
    .logo {
        font-size: 21px;
    }

    .code {
        letter-spacing: 4px;
    }

    button {
        max-width: 100%;
    }
}

</style>
</head>
<body>


<header class="room-header">
    <div class="brand">
        <div class="brand-icon">▶</div>
        <div>
            <div class="logo">WatchParty</div>
            <div class="brand-tagline">MOVIES ARE BETTER TOGETHER</div>
        </div>
    </div>

    <div class="header-details">
        <div class="header-room-code">
            <span class="header-label">ROOM CODE</span>
            <strong>{{ code }}</strong>
        </div>

        <div class="header-host">
            <span class="host-crown">👑</span>
            <div>
                <span class="header-label">HOST</span>
                <strong>{{ host }}</strong>
            </div>
        </div>
    </div>
</header>



<main>
  <div class="panel">
    <h1>🍿 Movie night is on!</h1>
    <p>Welcome, {{ username }}. Invite your friends with this room code.</p>
    <p style="color:#c5adff;font-weight:bold;">
    👑 Host: {{ host }}
    </p>
    <div class="code">{{ code }}</div>
    <p style="color:#c5adff;font-weight:bold;">
    👥 Watching together: <span id="participantCount">1</span>
    </p>
    <button onclick="copyCode()">📋 Copy room code</button>
    <button onclick="copyInviteLink()">
    🔗 Copy invite link
    </button>
    <a href="/" style="color:#c5adff;margin-left:10px">Home</a>
    <button onclick="leaveRoom()"
        style="background:#ff4d6d;color:white;margin-left:10px;">
    🚪 Leave Room
    </button>
    <p id="status">🟢 Connecting to your watch party...</p>
<p id="syncStatus" style="color:#c5adff;font-size:13px">
    🎯 SyncSense: Waiting for playback data...
</p>

<div class="panel" id="countdownPanel" style="text-align:center;margin-top:15px;">
    <h2>⏱️ Movie Night Countdown</h2>

    <p id="countdownDisplay" style="font-size:36px;font-weight:bold;color:#c5adff;">
        Ready when you are!
    </p>

    <button id="startCountdownButton" onclick="startCountdown()">
        🎬 Start 10-Second Countdown
    </button>

    <p id="countdownMessage" style="color:#c5adff;">
        Waiting for the host to start the countdown.
    </p>
</div>

  </div>

  <div class="row">
    <div class="panel">
      <h2>🎬 The Watch Screen</h2>
      
<video id="player" controls playsinline
       {% if username != host %}controlsList="nodownload" disablepictureinpicture{% endif %}
       {% if username != host %}style="pointer-events: none;"{% endif %}>

        <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4" type="video/mp4">
        Your browser does not support video playback.
      </video>
      <p id="nowPlaying" style="color:#c3a5ff;font-weight:bold;margin-top:12px;">
      🎵 Now Playing: Nothing selected
      </p>

      <p><small>Use the video controls to play, pause, or seek. Room playback changes will be shared with other connected viewers.</small></p>
    </div>

    
<div class="panel">
      <h2>💬 Party Chat</h2>
      <div id="messages"></div>
      <input id="chat" placeholder="Say something fun..." maxlength="500">
      <button onclick="sendChat()">Send message</button>
      <h3>React to the moment</h3>
      <button onclick="react('❤️')">❤️</button>
      <button onclick="react('😂')">😂</button>
      <button onclick="react('🔥')">🔥</button>
      <div id="reaction"></div>
      <h3>👥 Party Members</h3>
      <div id="participants">Waiting for room members...</div>
    </div>

    <div class="panel">
      <h2>🎬 Shared Playlist</h2>
      <div id="playlistLeaderboard"
     style="background:#2b2045; padding:12px; margin:12px 0;
            border-radius:10px; color:#ffffff;">
    🏆 <strong>Most-Voted Video</strong>
    <p id="leaderboardResult" style="margin:8px 0 0;">
        No votes yet — be the first to vote!
    </p>
</div>

      <small>Share video links with everyone in this room.</small>
      <input id="playlistUrl" type="url"
             placeholder="Paste a video URL (https://...)" maxlength="2000">
      <button onclick="addToPlaylist()">Add video</button>
      <p id="playlistStatus" role="status"></p>
      <ul id="playlistItems">
      <li>No videos added yet.</li>
      </ul>
      <p id="votingStatus" style="color:#c5adff;">
      🗳️ Vote for the video you'd like to watch next!
      </p>

    </div>
  </div>
</main>


<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<script>
const socket = io();
const roomCode = {{ code|tojson }};
const username = {{ username|tojson }};
const hostName = {{ host|tojson }};
const isHost = username === hostName;
const player = document.getElementById("player");

let applyingRemoteState = false;
let lastRemoteState = null;

socket.on("connect", () => {
  document.getElementById("status").textContent =
    "🟢 Connected — joining your watch party...";
  socket.emit("join_room", {room: roomCode, username: username});
  socket.emit("request_state", {room: roomCode});
});

function startCountdown() {
  if (!isHost) {
    document.getElementById("countdownMessage").textContent =
      "Only the host can start the countdown.";
    return;
  }

  socket.emit("start_countdown", {
    room: roomCode,
    username: username
  });
}

let countdownInterval = null;

socket.on("countdown_started", data => {
  const display = document.getElementById("countdownDisplay");
  const message = document.getElementById("countdownMessage");

  if (countdownInterval) {
    clearInterval(countdownInterval);
  }

  function updateCountdown() {
    const secondsLeft = Math.max(
      0,
      Math.ceil(data.ends_at - (Date.now() / 1000))
    );

    if (secondsLeft > 0) {
      display.textContent = secondsLeft;
      message.textContent = "🍿 Get ready! The movie is about to start.";
    } else {
      display.textContent = "🎬 0";
      message.textContent = "It's movie time!";
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
  }

  updateCountdown();
  countdownInterval = setInterval(updateCountdown, 200);
});

socket.on("countdown_error", data => {
  document.getElementById("countdownMessage").textContent =
    data.message || "Unable to start countdown.";
});


socket.on("disconnect", () => {
  document.getElementById("status").textContent =
    "🟠 Connection lost. Reconnecting...";
});

function copyCode() {
  navigator.clipboard.writeText(roomCode)
    .then(() => alert("Room code copied: " + roomCode))
    .catch(() => alert("Your room code is: " + roomCode));
}

function copyInviteLink() {
  const inviteLink = window.location.origin +
    "/room/" + roomCode +
    "?username=" + encodeURIComponent(username);

  navigator.clipboard.writeText(inviteLink)
    .then(() => alert("Invite link copied! Share it with your friends."))
    .catch(() => prompt("Copy this invite link:", inviteLink));
}

function leaveRoom() {
  if (confirm("Are you sure you want to leave this watch party?")) {
    window.location.href = "/";
  }
}



function sendChat() {
  const field = document.getElementById("chat");
  const message = field.value.trim();
  if (!message) return;
  socket.emit("chat_message", {
    room: roomCode,
    username: username,
    message: message
  });
  field.value = "";
}

function addToPlaylist() {
    const input = document.getElementById("playlistUrl");
    const status = document.getElementById("playlistStatus");
    const url = input.value.trim();

    if (!url) {
        status.textContent = "Please enter a video URL.";
        return;
    }

    if (!/^https?:\/\/\S+$/i.test(url)) {
        status.textContent = "Please enter a valid HTTP or HTTPS URL.";
        return;
    }

    socket.emit("add_to_playlist", {
        room: roomCode,
        username: username,
        url: url
    });

    input.value = "";
    status.textContent = "Adding video...";
}


socket.on("playlist_updated", function(data) {
    const list = document.getElementById("playlistItems");
    const status = document.getElementById("playlistStatus");

    list.innerHTML = "";

    if (!data.playlist || data.playlist.length === 0) {
        list.innerHTML = "<li>No videos added yet.</li>";
        return;
    }

    data.playlist.forEach(function(item, index) {
        const li = document.createElement("li");

        // Host-only video selection
        const link = document.createElement("button");
        link.textContent = (index + 1) + ". " + item.title;
        link.style.color = "#c3a5ff";

        if (isHost) {
            link.onclick = function() {
                socket.emit("select_playlist_video", {
                    room: roomCode,
                    username: username,
                    index: index
                });
            };
        } else {
            link.disabled = true;
            link.title = "Only the host can select a video";
        }

        li.appendChild(link);

        li.appendChild(
            document.createTextNode(" — added by " + item.added_by + " ")
        );

        // Voting button
        const voteButton = document.createElement("button");
        voteButton.textContent = "🗳️ Vote";
        voteButton.onclick = function() {
            socket.emit("vote_playlist", {
                room: roomCode,
                username: username,
                index: index
            });
        };

        li.appendChild(voteButton);

        // Vote count
        const voteCount = document.createElement("span");
        voteCount.id = "votes-" + index;
        voteCount.textContent = " Votes: 0";
        li.appendChild(voteCount);

        list.appendChild(li);
    });

    status.textContent = "Playlist updated for everyone!";
});

socket.on("playlist_votes_updated", function(data) {
    const votes = data.votes || {};

    document.querySelectorAll('[id^="votes-"]').forEach(function(element) {
        const index = element.id.replace("votes-", "");
        const itemVotes = votes[index] || [];

        element.textContent = " Votes: " + itemVotes.length;
    });
});

socket.on("playlist_leaderboard_updated", function(data) {
    const result = document.getElementById("leaderboardResult");

    if (!result) {
        return;
    }

    if (data.winner_votes === 0) {
        result.textContent = "No votes yet — be the first to vote!";
    } else {
        result.textContent =
            "🥇 " + data.winner_title +
            " — " + data.winner_votes +
            (data.winner_votes === 1 ? " vote" : " votes");
    }
});




socket.on("playlist_error", function(data) {
    document.getElementById("playlistStatus").textContent =
        data.message || "Unable to add this video.";
});


document.getElementById("chat").addEventListener("keydown", event => {
  if (event.key === "Enter") sendChat();
});

socket.on("chat_message", data => {
  const box = document.getElementById("messages");
  const line = document.createElement("div");
  line.textContent = data.username + ": " + data.message;
  box.appendChild(line);
  box.scrollTop = box.scrollHeight;
});

function react(emoji) {
  socket.emit("reaction", {
    room: roomCode,
    username: username,
    emoji: emoji
  });
}

socket.on("reaction", data => {
  document.getElementById("reaction").textContent =
    data.username + " reacted " + data.emoji;
});

function sendPlaybackAction(action) {
  if (applyingRemoteState) return;

  socket.emit("playback_action", {
    room: roomCode,
    username: username,
    action: action,
    position: player.currentTime || 0
  });
}

player.addEventListener("play", () => sendPlaybackAction("play"));
player.addEventListener("pause", () => sendPlaybackAction("pause"));
player.addEventListener("seeked", () => sendPlaybackAction(
  player.paused ? "pause" : "seek"
));

player.addEventListener("loadedmetadata", () => {
  socket.emit("request_state", {room: roomCode});
});


socket.on("room_state", data => {
    document.getElementById("syncStatus").textContent =
        "🎯 SyncSense: Playback state received at " +
        new Date().toLocaleTimeString();

    if (data.participants) {
        document.getElementById("participants").textContent =
            data.participants.join(", ");
    }
    document.getElementById("participantCount").textContent =
    data.participants ? data.participants.length : 1;

    if (!data.playback) return;

    lastRemoteState = data.playback;

    // Apply the latest shared playback position and play/pause state.
    applyPlaybackState(data.playback);
});


function applyPlaybackState(state) {
  const syncStatus = document.getElementById("syncStatus");

  if (!player.readyState) {
    syncStatus.textContent =
      "🎯 SyncSense: Waiting for video to load...";
    return;
  }

  const targetPosition = Number(state.position) || 0;
  const difference = Math.abs(player.currentTime - targetPosition);

  applyingRemoteState = true;

  if (difference > 0.8) {
    player.currentTime = targetPosition;
    syncStatus.textContent =
      "🔄 SyncSense: Correcting playback position...";
  } else {
    syncStatus.textContent =
      "✅ SyncSense: Playback synchronized";
  }

  if (state.playing && player.paused) {
    player.play().catch(() => {
      document.getElementById("status").textContent =
        "ℹ️ Press Play once if your browser blocks automatic playback.";
    });
  } else if (!state.playing && !player.paused) {
    player.pause();
  }

  setTimeout(() => {
    applyingRemoteState = false;
  }, 300);
}


socket.on("playlist_video_selected", function(data) {
    const player = document.getElementById("player");
    const status = document.getElementById("status");

    if (!data.url) {
        return;
    }

    player.src = data.url;
    document.getElementById("nowPlaying").textContent =
    "🎵 Now Playing: " + data.url.split("/").pop();
    player.load();

    // Reset the shared playback position for the newly selected video.
    applyingRemoteState = true;
    player.currentTime = 0;

    setTimeout(function() {
        applyingRemoteState = false;
    }, 500);

    status.textContent = "🎬 Host selected a playlist video!";
});


socket.on("permission_denied", data => {
    document.getElementById("status").textContent =
        "🔒 " + data.message;
});

</script>
</body>
</html>
"""



@app.route("/")
def home():
    return render_template_string(HTML, message=request.args.get("message", ""))



@app.route("/create", methods=["POST"])
def create_room():
    username = request.form.get("username", "").strip()[:30]

    if not username:
        return redirect(url_for("home", message="Please enter your name."))

    code = "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(6)
    )

    rooms[code] = {
        "host": username,
        "participants": [username],
        "socket_ids": {},
        "playback": {
            "playing": False,
            "position": 0,
            "updated_at": time.time()
        },
        "playlist": []
    }

    return redirect(
        url_for("watch_room", code=code, username=username)
    )


@app.route("/join", methods=["POST"])
def join_existing_room():
    username = request.form.get("username", "").strip()[:30]
    code = request.form.get("room_code", "").strip().upper()

    if not username:
        return redirect(url_for("home", message="Please enter your name."))
    if code not in rooms:
        return redirect(url_for("home", message="Room not found. Check the code and try again."))
    if username not in rooms[code]["participants"]:
        rooms[code]["participants"].append(username)

    return redirect(url_for("watch_room", code=code, username=username))


@app.route("/room/<code>")
def watch_room(code):
    code = code.upper()
    username = request.args.get("username", "Guest")[:30]
    if code not in rooms:
        return redirect(url_for("home", message="That room does not exist anymore."))
    return render_template_string(
    ROOM_HTML,
    code=code,
    username=username,
    host=rooms[code]["host"]
)




@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid

    for code, room in rooms.items():
        if sid in room.get("socket_ids", {}):
            username = room["socket_ids"].pop(sid)

            if username in room["participants"]:
                room["participants"].remove(username)

            socketio.emit("room_state", {
                "participants": room["participants"],
                "playback": room["playback"]
            }, to=code)

            socketio.emit("chat_message", {
                "username": "System",
                "message": username + " left the party!"
            }, to=code)

            break

@socketio.on("join_room")
def handle_join(data):
    code = str(data.get("room", "")).upper()
    username = str(data.get("username", "Guest")).strip()[:30]

    if code not in rooms:
        return

    join_room(code)
    rooms[code].setdefault("socket_ids", {})[request.sid] = username
    if username not in rooms[code]["participants"]:
        rooms[code]["participants"].append(username)


    # Announce the new member in the chat.
    socketio.emit("chat_message", {
        "username": "System",
        "message": username + " joined the party!"
    }, to=code)

    # Update the participant list for everyone in the room.
    socketio.emit("room_state", {
        "participants": rooms[code]["participants"],
        "playback": rooms[code]["playback"]
    }, to=code)
    
    # Send the existing playlist to the newly joined participant.
    socketio.emit("playlist_updated", {
        "playlist": rooms[code].get("playlist", [])
    }, to=request.sid)

    # Send the current vote counts to the newly joined participant.
    socketio.emit("playlist_votes_updated", {
        "votes": rooms[code].get("playlist_votes", {})
    }, to=request.sid)





@socketio.on("start_countdown")
def handle_start_countdown(data):
    code = str(data.get("room", "")).upper()

    if code not in rooms:
        return

    username = str(data.get("username", "")).strip()[:30]

    if username != rooms[code]["host"]:
        socketio.emit("countdown_error", {
            "message": "Only the host can start the countdown."
        }, to=request.sid)
        return

    ends_at = time.time() + 10

    socketio.emit("countdown_started", {
        "ends_at": ends_at
    }, to=code)

@socketio.on("chat_message")
def handle_chat(data):
    code = str(data.get("room", "")).upper()

    if code not in rooms:
        return

    username = str(data.get("username", "Guest"))[:30]
    message = str(data.get("message", ""))[:500].strip()

    if message:
        socketio.emit("chat_message", {
            "username": username,
            "message": message
        }, to=code)


@socketio.on("add_to_playlist")
def handle_add_to_playlist(data):
    code = str(data.get("room", "")).upper()

    if code not in rooms:
        return

    username = str(data.get("username", "Guest")).strip()[:30]
    video_url = str(data.get("url", "")).strip()

    if not video_url or not (
        video_url.startswith("https://") or
        video_url.startswith("http://")
    ):
        socketio.emit("playlist_error", {
            "message": "Please enter a valid HTTP or HTTPS URL."
        }, to=request.sid)
        return

    playlist = rooms[code].setdefault("playlist", [])

    if len(playlist) >= 50:
        socketio.emit("playlist_error", {
            "message": "The playlist is full (maximum 50 videos)."
        }, to=request.sid)
        return

    item = {
        "title": video_url,
        "url": video_url,
        "added_by": username
    }

    playlist.append(item)

    socketio.emit("playlist_updated", {
        "playlist": playlist
    }, to=code)


@socketio.on("vote_playlist")
def handle_vote_playlist(data):
    code = str(data.get("room", "")).upper()

    if code not in rooms:
        return

    username = str(data.get("username", "")).strip()[:30]

    if not username:
        return

    try:
        index = int(data.get("index", -1))
    except (TypeError, ValueError):
        return

    playlist = rooms[code].get("playlist", [])

    if index < 0 or index >= len(playlist):
        return

    # Store one vote per username per playlist item.
    votes = rooms[code].setdefault("playlist_votes", {})
    item_votes = votes.setdefault(str(index), [])

    if username in item_votes:
        item_votes.remove(username)
    else:
        item_votes.append(username)

    socketio.emit("playlist_votes_updated", {
        "votes": votes
    }, to=code)
    
    # Calculate the most-voted video.
    playlist = rooms[code].get("playlist", [])

    if playlist:
        vote_counts = {
            int(index): len(usernames)
            for index, usernames in votes.items()
        }

        winner_index = max(
            range(len(playlist)),
            key=lambda i: vote_counts.get(i, 0)
        )

        socketio.emit("playlist_leaderboard_updated", {
            "winner_index": winner_index,
            "winner_title": playlist[winner_index].get("title", "Untitled"),
            "winner_votes": vote_counts.get(winner_index, 0)
        }, to=code)


@socketio.on("select_playlist_video")
def handle_select_playlist_video(data):
    code = str(data.get("room", "")).upper()

    if code not in rooms:
        return

    username = str(data.get("username", "")).strip()[:30]

    if username != rooms[code]["host"]:
        socketio.emit("playlist_error", {
            "message": "Only the host can select the next video."
        }, to=request.sid)
        return

    try:
        index = int(data.get("index", -1))
    except (TypeError, ValueError):
        return

    playlist = rooms[code].get("playlist", [])

    if index < 0 or index >= len(playlist):
        return

    video = playlist[index]

    rooms[code]["playback"] = {
        "playing": False,
        "position": 0,
        "updated_at": time.time()
    }

    socketio.emit("playlist_video_selected", {
        "url": video["url"],
        "index": index
    }, to=code)

    socketio.emit("room_state", {
        "participants": rooms[code]["participants"],
        "playback": rooms[code]["playback"]
    }, to=code)




@socketio.on("reaction")
def handle_reaction(data):
    code = data.get("room", "").upper()
    if code not in rooms:
        return
    socketio.emit("reaction", {
        "username": str(data.get("username", "Guest"))[:30],
        "emoji": str(data.get("emoji", "❤️"))[:8]
    }, to=code)

@socketio.on("request_state")
def request_playback_state(data):
    code = str(data.get("room", "")).upper()

    if code not in rooms:
        return

    socketio.emit("room_state", {
        "participants": rooms[code]["participants"],
        "playback": rooms[code]["playback"]
    }, to=request.sid)



@socketio.on("playback_action")
def handle_playback_action(data):
    code = str(data.get("room", "")).upper()

    if code not in rooms:
        return

    # Only the host can control shared playback.
    username = str(data.get("username", ""))[:30]

    if username != rooms[code]["host"]:
        socketio.emit("permission_denied", {
            "message": "Only the host can control playback."
        }, to=request.sid)
        return

    action = data.get("action")

    if action not in ("play", "pause", "seek"):
        return

    try:
        position = max(0.0, float(data.get("position", 0)))
    except (TypeError, ValueError):
        return

    playback = rooms[code]["playback"]
    playback["position"] = position
    playback["playing"] = action == "play"
    playback["updated_at"] = time.time()

    socketio.emit("room_state", {
        "participants": rooms[code]["participants"],
        "playback": playback
    }, to=code, include_self=False)



if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
