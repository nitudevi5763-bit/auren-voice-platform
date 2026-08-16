# Auren Voice Platform — Chunk 1

Yeh ek single test client ke liye poora voice agent engine hai (STT -> LLM -> TTS).
Iska maqsad hai proof karna ki full pipeline call pe kaam karta hai — UI/dashboard baad
ke chunks mein aayega.

## Step 1: GitHub par push karo

1. github.com par ek naya **private** repo banao: `auren-voice-platform`
2. Is poore folder ko us repo mein push karo (Claude Code terminal se ya GitHub Desktop se)

## Step 2: API keys collect karo

`.env.example` file ko `.env` naam se copy karo, aur yeh values bharo:

- **LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET** — cloud.livekit.io par project
  banao, Settings > Keys mein milega
- **DEEPGRAM_API_KEY** — deepgram.com signup, dashboard mein milega
- **ELEVENLABS_API_KEY** — elevenlabs.io signup, Profile > API Keys
- **OPENAI_API_KEY** — platform.openai.com, API keys section

`.env` file ko GitHub par push MAT karna — yeh secrets hain. (`.gitignore` already
isko block karta hai agar tum standard Python .gitignore use karo.)

## Step 3: Railway par deploy karo

1. railway.app par account banao (GitHub se sign-in kar sakte ho)
2. "New Project" > "Deploy from GitHub repo" > apna `auren-voice-platform` repo choose karo
3. Railway apne aap `railway.json` padh lega aur deploy shuru kar dega
4. Railway ke dashboard mein "Variables" tab mein jaake apni `.env` wali saari
   keys yahan bhi paste karo (Railway isi tarah secrets leta hai)
5. Deploy complete hone ke baad, "Logs" tab mein dekho — "registered worker" jaisa
   message aana chahiye, matlab agent live hai aur calls sunne ke liye ready hai

## Step 4: Test karo (bina phone number ke)

LiveKit Cloud ke dashboard mein ek "Playground" hota hai jaha tum browser se hi
seedha is agent se baat kar sakte ho — asli phone number ki zaroorat nahi hai
Chunk 1 test karne ke liye. LiveKit Cloud > tumhara project > "Agents Playground"
mein jaake connect karo aur bolke dekho agent reply de raha hai ya nahi.

Agar agent sahi se bol/sun raha hai — Chunk 1 done hai. Phone number (Plivo)
wiring Chunk 2 mein hoga.

## Agar koi error aaye

Railway "Logs" tab se pura error copy karke seedha yahan chat mein paste kar do,
main fix karke updated code dunga.
