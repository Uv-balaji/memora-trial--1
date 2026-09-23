MEMORA PRESENTS GENOGAME - ENHANCED OFFLINE/LOCAL PACKAGE
===========================================================

WHAT IS INCLUDED
----------------
- Daily reminder system with preset elderly-friendly routines.
- Browser notifications + repeat-every-10-minutes behavior until Done.
- Memory Journey: up to 4 attempts per question, per-attempt timing and action history.
- Memory Matrix: maximum 8 selections per physical card, repeated-card tracking and pair history.
- Catch the Balloon: maximum 4 wrong selections per round, wrong streak tracking and reaction-time history.
- Doctor-style cumulative performance dashboard.
- Selectable metrics: Memory, Response Speed, Attention/Accuracy,
  Repetition & Error Control, Sequence Performance, Overall Behavioral Score.
- Session-by-session graph that preserves real dips; no smoothing.
- Detailed behavioral evidence and complete action history.
- Existing K-Means adaptive-difficulty ML model and RandomForest model files.
- Complete local MediaPipe runtime under vendor/node_modules.

IMPORTANT ML NOTE
-----------------
The ML component is a research/screening prototype for gameplay-performance patterns.
It is NOT a diagnosis of Alzheimer's disease, dementia, or any other medical condition.
The bundled training script uses synthetic/demo data and should not be presented as clinically validated.

HOW TO RUN THE WEBSITE
----------------------
1. Double-click START_MEMORA.bat.
2. Open http://localhost:8000 in Chrome/Edge.
3. Do not delete the vendor folder: it contains the local MediaPipe runtime.

WHY USE localhost?
------------------
Camera access and browser notifications can be restricted when opening index.html
with file://. localhost gives the browser a secure local origin while remaining local/offline.

HOW TO RUN THE ML BACKEND
-------------------------
1. Double-click START_ML_SERVER.bat.
2. Keep the terminal open.
3. The website sends enhanced event-derived features to http://127.0.0.1:5000/api/predict.
4. If the ML server is unavailable, the dashboard still shows the local behavioral metrics.

ML FILES
--------
model.pkl
ml_model/kmeans_performance_model.pkl
ml_model/performance_scaler.pkl
ml_model/ml_features.pkl
ml_model/difficulty_mapping.pkl
train_model.py
ml_colab/01_train_memora_model.ipynb

DATA STORAGE
------------
Session/profile data is stored in the browser's localStorage under:
memora_genogame_profiles_v3

For a real clinical deployment, replace the demo/synthetic ML training with an
appropriately validated dataset and clinical validation process.


===========================================================
FIXES APPLIED (index.html)
===========================================================

1. HAND TRACKING / CAMERA
   trackingLoopRunning and trackingProcessing were declared with
   "let" inside initTracking(), so they were local to that function.
   stopCamera() was assigning to different, top-level variables, so
   the real tracking loop never stopped. Restarting the balloon game
   left the old loop alive and started a second one; both called
   hands.send() on the same MediaPipe instance, which stalls it.
   Result: hand not detected, and sometimes the camera would not open.
   Fixed: both flags are now global, plus a trackingGeneration counter
   guarantees a stale loop exits on its next frame.

2. RESULTS SCREEN OPENING ONLY ONCE
   renderDashboard() replaces the innerHTML of "#resultsScreen .container",
   destroying the six elements showResults() writes into (resultPatient,
   overallScore, riskLevel, metricsContainer, balloonReport, aiSummary).
   On the second open, showResults() threw on a null element before it
   reached its final show("resultsScreen") call, so nothing happened.
   Fixed: the original container markup is snapshotted once and restored
   before each rebuild, with try/catch so an error cannot hide the screen.

3. DOCTOR VIEW NOT OPENING
   switchResultView() was defined inside an IIFE and never attached to
   window, but the tab button calls it from an inline onclick, which only
   resolves globals. Every click threw "switchResultView is not defined".
   Fixed: window.switchResultView = switchResultView.

ALSO REMOVED
   vendor/mediapipe/*.js  (four 0-byte files, unreferenced)
   __pycache__/           (compiled Python)
   .dist/                 (empty)

NOTE
   node_modules/ at the root is an exact duplicate of
   vendor/node_modules/. Only the vendor copy is used by index.html.
   The root copy can be deleted; "npm install" recreates it.


===========================================================
DAILY CARE PLAN (upgraded reminder page)
===========================================================

The reminder page is now a full daily health-care routine,
grouped into Morning / Afternoon / Evening / Night.

DEFAULT PLAN (21 reminders)
  Morning   wake up, yoga/stretch, morning walk, breakfast,
            morning tablet, water, brain game, water
  Afternoon lunch, afternoon tablet, water, rest/nap, water
  Evening   evening walk, breathing/pranayama, family time, water
  Night     dinner, night tablet, relax & stretch, sleep

FEATURES
  - Progress bar and % complete for the day
  - Reminders grouped by part of day, each group showing done/total
  - Add your own reminder using the form (name, icon, time,
    part of day, note) - no more prompt() pop-ups
  - Remove any reminder with the small x button
  - One-tap packs: "Hydration pack" (6 water reminders) and
    "Yoga & exercise" (5 gentle movement/breathing reminders)
  - "Reset plan" restores the default routine
  - Repeat-every-10-minutes behaviour until Done is unchanged

ALSO FIXED
  addReminder() validated the time with /^([01]\\d|2[0-3]):[0-5]\\d$/.
  The doubled backslash made it match a literal backslash, so every
  valid time such as 08:30 was rejected. Now /^([01]\d|2[0-3]):[0-5]\d$/.

STORAGE
  Key bumped to memora_daily_reminders_v2 so the new plan loads.
  Old v1 reminders are left untouched in localStorage.

SAFETY
  Medicine reminders use only the times you enter. Memora does not
  suggest medicines or dosages - follow your doctor's prescription.
  Exercise and yoga should start gently; stop if there is pain,
  dizziness or breathlessness.
