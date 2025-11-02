from psychopy import visual, core, event, logging, prefs
import os, csv, random, datetime
from numbers import Number
import argparse

################### psychopy py file for HORIKAWA with Scanner Trigger ###################

print("initial import is ok")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sub_id", type=str, default="01", help="subject id but only number")
    parser.add_argument("--session", type=int, default=1, help="current session number to run")
    parser.add_argument("--video_csv_path", type=str, default="C:/Users/이태양/Desktop/LAB/EmoFM/Project/EmoFM/pilot_horikawa/test_video_list.csv", help="csv path that has video path information")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--shuffle_videos", action="store_true", default=False, help="shuffle video sequence")

    # args for basic rest
    parser.add_argument("--prerest", type=float, default=32.0, help="prerest time(default is 32.0)")
    parser.add_argument("--interrest", type=float, default=2.0, help="interrest between videos(default is 2.0)")
    parser.add_argument("--postrest", type=float, default=6.0, help="postrest after video block")

    # args for flexible rest and instruction
    parser.add_argument("--flexible_rest", action="store_true", default=False, help="add flexible rest for align with TR")
    parser.add_argument("--flexible_time_unit", type=float, default=3.0, help="time unit to fit for TR")
    parser.add_argument("--instruction_time", type=float, default=3.0, help="instruction display time")

    # args for display
    parser.add_argument("--movie_width_pixel", type=int, default=1280, help="movie width pixel size(default is 1280)")

    # args for scanner trigger
    parser.add_argument("--use_scanner_trigger", action="store_true", default=True, help="wait for scanner trigger to start")
    parser.add_argument("--trigger_key", type=str, default="5", help="scanner trigger key (default is '5')")

    return parser.parse_args()

args = get_args()

# Basic setting
SUB_ID = args.sub_id
CURRENT_SESSION = args.session  # Current session number to run
USE_SCANNER_TRIGGER = args.use_scanner_trigger
TRIGGER_KEY = args.trigger_key  # Single trigger key (default '5')
QUIT_KEY = 'escape'

# Rest setting
REST_PRE = args.prerest
REST_BETWEEN = args.interrest
REST_POST = args.postrest

INSTRUCT_FIX_DUR = args.instruction_time

FLEXIBLE_REST = args.flexible_rest
FLEX_UNIT = args.flexible_time_unit

# CSV that contain video path and video experiment info
CSV_PLAYLIST_PATH = args.video_csv_path

SHUFFLE_VIDEOS = args.shuffle_videos
RANDOM_SEED = 42

# Screen Setting
FULLSCREEN = True
WIN_SIZE = [1920, 1080]
BG_COLOR = [0.4, 0.4, 0.4]
FIX_COLOR = [1, 1, 1]
FIX_HEIGHT = 0.08
TEXT_COLOR = [1, 1, 1]

# Output / Log
OUT_ROOT = args.output_dir
WRITE_PSYCHOPY_LOG = True

DESIRED_MOVIE_WIDTH = args.movie_width_pixel

def set_movie_width_keep_aspect(movie, desired_width):
    native_w = native_h = None
    for attr in ("videoSize", "frameSize", "_videoSize", "_origSize", "size"):
        try:
            val = getattr(movie, attr)
            if callable(val):
                val = val()
            w, h = val
            if w and h and w > 0 and h > 0:
                native_w, native_h = float(w), float(h)
                break
        except Exception:
            continue
    if not native_w or not native_h:
        return
    aspect = native_h / native_w
    movie.size = (desired_width, desired_width * aspect)

# Set video player
prefs.general['movies'] = ['ffpyplayer']

from psychopy import gui

# util function
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def bids_path(sub, ses, run, ext):
    return os.path.join(OUT_ROOT, f"sub-{sub}", f"ses-{ses:02d}", f"run-{run:02d}.{ext}")

def write_events_tsv(events, sub, ses, run):
    ensure_dir(os.path.dirname(bids_path(sub, ses, run, "events.tsv")))
    path = bids_path(sub, ses, run, "events.tsv")
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["onset", "duration", "trial_type", "stim_file"])
        for e in events:
            writer.writerow([f"{e['onset']:.3f}", f"{e['duration']:.3f}", e['trial_type'], e.get('stim_file',"")])
    return path

def write_scan_times(sub, ses, run, trigger_time_clock, trigger_datetime):
    """Write scanner trigger times to a log file"""
    ensure_dir(os.path.dirname(bids_path(sub, ses, run, "scan_times.txt")))
    path = bids_path(sub, ses, run, "scan_times.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"Scanner Trigger Information\n")
        f.write(f"===========================\n")
        f.write(f"Time (PsychoPy clock): {trigger_time_clock:.6f}\n")
        f.write(f"Timestamp (datetime): {trigger_datetime}\n")
    return path

def get_runs_for_session(csv_path, ses):
    """Get list of run numbers for a given session from CSV"""
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Playlist CSV not found: {csv_path}")

    runs = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            if int(row['session']) == ses:
                runs.add(int(row['run']))

    return sorted(list(runs))

def load_playlist_from_csv(csv_path, sub, ses, run):
    lst = []
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Playlist CSV not found: {csv_path}")
    with open(csv_path, 'r', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            if int(row['session']) == ses and int(row['run']) == run:
                lst.append((int(row.get('order', len(lst)+1)), row['video_path']))
    lst.sort(key=lambda x: x[0])
    return [p for _, p in lst]

# ======== Window/Stimulus Setting ========
win = visual.Window(size=WIN_SIZE, fullscr=FULLSCREEN, color=BG_COLOR, units='height')
fix = visual.TextStim(win, text='+', color=FIX_COLOR, height=FIX_HEIGHT)

instr_text = visual.TextStim(
    win,
    text="화면 중앙의 십자점을 응시하세요.\n(잠시 후 시작됩니다)",
    color=TEXT_COLOR,
    height=0.05,
    wrapWidth=1.6,
    font="Malgun Gothic",
)

# write log
if WRITE_PSYCHOPY_LOG:
    ensure_dir(OUT_ROOT)
    log_path = os.path.join(OUT_ROOT, f"{SUB_ID}_log_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log")
    logging.console.setLevel(logging.INFO)
    logging.LogFile(log_path, level=logging.INFO)
logging.info("=== Experiment started ===")

# set random seed
random.seed(RANDOM_SEED)

# Main Loop
try:
    # Get all runs for the current session from CSV
    runs_in_session = get_runs_for_session(CSV_PLAYLIST_PATH, CURRENT_SESSION)

    if len(runs_in_session) == 0:
        logging.error(f"No runs found for session {CURRENT_SESSION} in CSV file.")
        raise ValueError(f"No runs found for session {CURRENT_SESSION}")

    logging.info(f"Session {CURRENT_SESSION}: Found {len(runs_in_session)} run(s) - {runs_in_session}")

    for run in runs_in_session:
        videos = load_playlist_from_csv(CSV_PLAYLIST_PATH, SUB_ID, CURRENT_SESSION, run)

        if len(videos) == 0:
            logging.warning(f"No videos for session {CURRENT_SESSION}, run {run}. Skipping run.")
            continue

        if SHUFFLE_VIDEOS:
            random.shuffle(videos)

        # Waiting for scanner trigger or manual start
        trigger_time_clock = None
        trigger_datetime = None

        if USE_SCANNER_TRIGGER:
            msg = visual.TextStim(win, text="Waiting for scanner trigger...", color=FIX_COLOR, height=0.05)
            msg.draw()
            win.flip()
            event.clearEvents()

            # Wait for scanner trigger with timestamp
            keys = event.waitKeys(keyList=[TRIGGER_KEY], timeStamped=True)
            trigger_time_clock = keys[0][1]  # PsychoPy clock time
            trigger_datetime = datetime.datetime.now()  # Actual datetime

            logging.info(f"[SCANNER TRIGGER] Received at {trigger_time_clock:.6f}s (datetime: {trigger_datetime})")

            # Save trigger times
            scan_times_path = write_scan_times(SUB_ID, CURRENT_SESSION, run, trigger_time_clock, str(trigger_datetime))
            logging.info(f"[Saved] Scanner trigger times: {scan_times_path}")
        else:
            msg = visual.TextStim(win, text="Press any key to start run", color=FIX_COLOR, height=0.05)
            msg.draw()
            win.flip()
            event.waitKeys(keyList=None)

        # Clock with run start
        run_clock = core.Clock()
        events_log = []

        # Record scanner trigger event if used
        if USE_SCANNER_TRIGGER and trigger_time_clock is not None:
            events_log.append({
                "onset": 0.0,  # Trigger is time zero
                "duration": 0.0,
                "trial_type": "scanner_trigger",
                "stim_file": f"trigger_key_{TRIGGER_KEY}"
            })

        # Instruction before prerest
        instr_on = run_clock.getTime()
        instr_end = instr_on + INSTRUCT_FIX_DUR
        event.clearEvents()
        while run_clock.getTime() < instr_end:
            instr_text.draw()
            win.flip()
            if QUIT_KEY in event.getKeys():
                raise KeyboardInterrupt

        events_log.append({
            "onset": instr_on,
            "duration": run_clock.getTime() - instr_on,
            "trial_type": "instruction_fixate",
            "stim_file": ""
        })

        # PREREST (32s)
        fix_on = run_clock.getTime()
        while run_clock.getTime() - fix_on < REST_PRE:
            fix.draw()
            win.flip()
            if QUIT_KEY in event.getKeys():
                raise KeyboardInterrupt
        events_log.append({
            "onset": fix_on,
            "duration": run_clock.getTime() - fix_on,
            "trial_type": "rest_pre",
            "stim_file": ""
        })

        # Running videos
        from psychopy.visual import MovieStim3
        for idx, vid_path in enumerate(videos, start=1):
            if not os.path.isfile(vid_path):
                logging.error(f"Video not found: {vid_path}")
                continue

            print(f'Preparing video {idx}: {vid_path}')

            # prepare vids
            try:
                movie = MovieStim3(
                    win, filename=vid_path, noAudio=True,
                    flipVert=False, flipHoriz=False, loop=False, autoLog=True
                )

                set_movie_width_keep_aspect(movie, DESIRED_MOVIE_WIDTH)

                meta_dur = getattr(movie, "duration", None)
                if not isinstance(meta_dur, Number) or meta_dur <= 0:
                    try:
                        meta_dur = movie.getDuration()
                    except Exception:
                        meta_dur = None
                logging.info(f"[VIDEO] Loaded: duration={meta_dur if meta_dur is not None else 'NA'} size={getattr(movie, 'size', 'NA')}")
            except Exception as e:
                logging.error(f"[VIDEO] FAILED to init MovieStim3: {e}", exc_info=True)
                continue

            print('Movie object created successfully')

            # running vids (play once if >=8s, else play twice)
            plays = 0
            total_play_time = 0.0
            must_play_twice = (isinstance(meta_dur, Number) and meta_dur < 8.0)

            while True:
                plays += 1
                vid_on = run_clock.getTime()
                movie.play()
                while movie.status != visual.FINISHED:
                    movie.draw()
                    win.flip()
                    if QUIT_KEY in event.getKeys():
                        movie.stop()
                        raise KeyboardInterrupt
                this_play = run_clock.getTime() - vid_on
                total_play_time += this_play

                # Decide whether to replay
                if plays == 1:
                    effective_dur = meta_dur if isinstance(meta_dur, Number) else this_play
                    if effective_dur < 8.0:
                        must_play_twice = True

                if must_play_twice and plays < 2:
                    # rewind to start and play again
                    try:
                        movie.seek(0.0)
                    except Exception:
                        movie.stop()
                        movie = MovieStim3(
                            win, filename=vid_path, noAudio=True,
                            flipVert=False, flipHoriz=False, loop=False, autoLog=True
                        )
                        set_movie_width_keep_aspect(movie, DESIRED_MOVIE_WIDTH)
                    continue
                else:
                    break

            events_log.append({
                "onset": vid_on,
                "duration": total_play_time,
                "trial_type": f"video_{idx}",
                "stim_file": os.path.basename(vid_path),
                "plays": plays
            })

            # Flexible rest for TR alignment
            if FLEXIBLE_REST and FLEX_UNIT > 0:
                remainder = total_play_time % FLEX_UNIT
                flex_dur = (FLEX_UNIT - remainder) % FLEX_UNIT
                if flex_dur > 1e-3:
                    flex_on = run_clock.getTime()
                    while run_clock.getTime() - flex_on < flex_dur:
                        fix.draw()
                        win.flip()
                        if QUIT_KEY in event.getKeys():
                            raise KeyboardInterrupt
                    events_log.append({
                        "onset": flex_on,
                        "duration": run_clock.getTime() - flex_on,
                        "trial_type": "rest_flexible",
                        "stim_file": ""
                    })
                    logging.info(f"[FLEX REST] Added {flex_dur:.3f}s after video_{idx} to hit {FLEX_UNIT:.1f}s multiple")

            # Inter-REST (2s)
            if idx < len(videos):
                ib_on = run_clock.getTime()
                while run_clock.getTime() - ib_on < REST_BETWEEN:
                    fix.draw()
                    win.flip()
                    if QUIT_KEY in event.getKeys():
                        raise KeyboardInterrupt
                events_log.append({
                    "onset": ib_on,
                    "duration": run_clock.getTime() - ib_on,
                    "trial_type": "rest_between",
                    "stim_file": ""
                })

        # POSTREST (6s)
        post_on = run_clock.getTime()
        while run_clock.getTime() - post_on < REST_POST:
            fix.draw()
            win.flip()
            if QUIT_KEY in event.getKeys():
                raise KeyboardInterrupt
        events_log.append({
            "onset": post_on,
            "duration": run_clock.getTime() - post_on,
            "trial_type": "rest_post",
            "stim_file": ""
        })

        # Saving
        tsv_path = write_events_tsv(events_log, SUB_ID, CURRENT_SESSION, run)
        logging.info(f"[Saved] {tsv_path}")

        # screen run ended
        end_msg = visual.TextStim(win, text=f"Run {run} complete.\nPlease wait.", color=FIX_COLOR, height=0.05)
        end_msg.draw()
        win.flip()
        core.wait(2.0)

    logging.info("=== Experiment finished ===")

except KeyboardInterrupt:
    logging.warning("Experiment aborted by user.")
finally:
    win.close()
    core.quit()
