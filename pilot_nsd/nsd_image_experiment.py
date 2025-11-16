from psychopy import visual, core, event, logging, prefs
import os, csv, random, datetime, numpy as np
import argparse

################### PsychoPy script for NSD-style Image Presentation with Scanner Trigger ###################
# Based on Natural Scenes Dataset (NSD) experimental design
# Allen et al., 2022, Nature Neuroscience
# Trial structure: 3s image presentation + 1s blank (4s total per trial)
# Task: Continuous recognition memory (button 1=new, button 2=old)

print("initial import is ok")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sub_id", type=str, default="01", help="subject id but only number")
    parser.add_argument("--session", type=int, default=1, help="current session number to run")
    parser.add_argument("--image_csv_path", type=str, required=True, help="csv path that has image path information")
    parser.add_argument("--output_dir", type=str, default="nsd_outputs")
    parser.add_argument("--shuffle_images", action="store_true", default=False, help="shuffle image sequence within run")

    # NSD-specific timing parameters (default values from paper)
    parser.add_argument("--image_duration", type=float, default=3.0, help="image presentation duration in seconds (default: 3.0)")
    parser.add_argument("--blank_duration", type=float, default=1.0, help="blank interval between images in seconds (default: 1.0)")
    parser.add_argument("--prerest", type=float, default=12.0, help="initial blank trials duration (3 trials × 4s = 12s)")
    parser.add_argument("--postrest", type=float, default=16.0, help="final blank trials duration (4 trials × 4s = 16s)")

    # Display parameters (NSD specifications)
    parser.add_argument("--image_size_pixels", type=int, default=714, help="image size in pixels (default: 714×714 for 8.4° visual angle)")
    parser.add_argument("--fixation_size_deg", type=float, default=0.2, help="fixation dot size in degrees (default: 0.2)")
    parser.add_argument("--fixation_opacity", type=float, default=0.5, help="fixation dot opacity (default: 0.5)")

    # Scanner trigger
    parser.add_argument("--use_scanner_trigger", action="store_true", default=True, help="wait for scanner trigger to start")
    parser.add_argument("--trigger_key", type=str, default="5", help="scanner trigger key (default is '5')")

    # Response collection
    parser.add_argument("--collect_responses", action="store_true", default=True, help="collect button responses for memory task")
    parser.add_argument("--new_key", type=str, default="1", help="button for 'new' image response")
    parser.add_argument("--old_key", type=str, default="2", help="button for 'old' image response")

    return parser.parse_args()

args = get_args()

# Basic setting
SUB_ID = args.sub_id
CURRENT_SESSION = args.session
USE_SCANNER_TRIGGER = args.use_scanner_trigger
TRIGGER_KEY = args.trigger_key
QUIT_KEY = 'escape'

# NSD timing parameters
IMAGE_DURATION = args.image_duration  # 3s image presentation
BLANK_DURATION = args.blank_duration  # 1s blank gap
TRIAL_DURATION = IMAGE_DURATION + BLANK_DURATION  # 4s total per trial
REST_PRE = args.prerest  # 12s = 3 blank trials
REST_POST = args.postrest  # 16s = 4 blank trials

# Display parameters
IMAGE_SIZE_PIXELS = args.image_size_pixels  # 714×714 pixels
FIXATION_SIZE_DEG = args.fixation_size_deg  # 0.2° visual angle
FIXATION_OPACITY = args.fixation_opacity  # 50% opacity

# Response collection
COLLECT_RESPONSES = args.collect_responses
NEW_KEY = args.new_key
OLD_KEY = args.old_key

# CSV that contains image paths
CSV_PLAYLIST_PATH = args.image_csv_path
# Expected CSV columns: session, run, image_path, order, is_repeat (0=new, 1=old)

SHUFFLE_IMAGES = args.shuffle_images
RANDOM_SEED = 42

# Screen Setting
FULLSCREEN = True
WIN_SIZE = [1920, 1080]
BG_COLOR = [0.5, 0.5, 0.5]  # Middle gray background (NSD specification)
FIX_COLOR = [1.0, 0.0, 0.0]  # Red fixation dot
FIX_BORDER_COLOR = [0.0, 0.0, 0.0]  # Black border
TEXT_COLOR = [1, 1, 1]

# Output / Log
OUT_ROOT = args.output_dir
WRITE_PSYCHOPY_LOG = True

# Utility functions
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def bids_path(sub, ses, run, ext):
    return os.path.join(OUT_ROOT, f"sub-{sub}", f"ses-{ses:02d}", f"run-{run:02d}.{ext}")

def write_events_tsv(events, sub, ses, run):
    """Write events to BIDS-formatted TSV file"""
    ensure_dir(os.path.dirname(bids_path(sub, ses, run, "events.tsv")))
    path = bids_path(sub, ses, run, "events.tsv")
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["onset", "duration", "trial_type", "stim_file", "response", "rt", "is_repeat"])
        for e in events:
            writer.writerow([
                f"{e['onset']:.3f}",
                f"{e['duration']:.3f}",
                e['trial_type'],
                e.get('stim_file', ""),
                e.get('response', ""),
                f"{e.get('rt', ''):.3f}" if e.get('rt') else "",
                e.get('is_repeat', "")
            ])
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
    """Load image playlist for specific session and run"""
    lst = []
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Playlist CSV not found: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            if int(row['session']) == ses and int(row['run']) == run:
                order = int(row.get('order', len(lst)+1))
                image_path = row['image_path']
                is_repeat = int(row.get('is_repeat', 0))  # 0=new, 1=old
                lst.append((order, image_path, is_repeat))

    lst.sort(key=lambda x: x[0])
    return [(path, is_repeat) for _, path, is_repeat in lst]

# ======== Window/Stimulus Setup ========
win = visual.Window(
    size=WIN_SIZE,
    fullscr=FULLSCREEN,
    color=BG_COLOR,
    units='pix',  # Use pixels for precise image sizing
    monitor='testMonitor'
)

# Create fixation dot with border (NSD specification: semi-transparent red with black border)
# Using two overlapping circles to create bordered effect
fix_border = visual.Circle(
    win,
    radius=FIXATION_SIZE_DEG * 50,  # Approximate pixel conversion (will need calibration)
    fillColor=FIX_BORDER_COLOR,
    lineColor=FIX_BORDER_COLOR,
    opacity=FIXATION_OPACITY
)

fix_dot = visual.Circle(
    win,
    radius=FIXATION_SIZE_DEG * 45,  # Slightly smaller for border effect
    fillColor=FIX_COLOR,
    lineColor=FIX_COLOR,
    opacity=FIXATION_OPACITY
)

def draw_fixation():
    """Draw fixation dot with border"""
    fix_border.draw()
    fix_dot.draw()

# Instruction text (Korean)
instr_text = visual.TextStim(
    win,
    text="화면 중앙의 빨간 점을 주시하세요.\n\n이미지가 새로운 이미지면 1번 버튼을,\n이전에 본 이미지면 2번 버튼을 누르세요.\n\n(잠시 후 시작됩니다)",
    color=TEXT_COLOR,
    height=30,
    wrapWidth=1200,
    font="Malgun Gothic",
    units='pix'
)

# Write log
if WRITE_PSYCHOPY_LOG:
    ensure_dir(OUT_ROOT)
    log_path = os.path.join(OUT_ROOT, f"{SUB_ID}_log_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log")
    logging.console.setLevel(logging.INFO)
    logging.LogFile(log_path, level=logging.INFO)
logging.info("=== NSD Image Experiment started ===")

# Set random seed
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
        images = load_playlist_from_csv(CSV_PLAYLIST_PATH, SUB_ID, CURRENT_SESSION, run)

        if len(images) == 0:
            logging.warning(f"No images for session {CURRENT_SESSION}, run {run}. Skipping run.")
            continue

        if SHUFFLE_IMAGES:
            random.shuffle(images)

        logging.info(f"Run {run}: {len(images)} images loaded")

        # Waiting for scanner trigger or manual start
        trigger_time_clock = None
        trigger_datetime = None

        if USE_SCANNER_TRIGGER:
            msg = visual.TextStim(win, text="Waiting for scanner trigger...", color=TEXT_COLOR, height=30, units='pix')
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
            msg = visual.TextStim(win, text="Press any key to start run", color=TEXT_COLOR, height=30, units='pix')
            msg.draw()
            win.flip()
            event.waitKeys(keyList=None)

        # Clock for run timing
        run_clock = core.Clock()
        events_log = []

        # Record scanner trigger event if used
        if USE_SCANNER_TRIGGER and trigger_time_clock is not None:
            events_log.append({
                "onset": 0.0,
                "duration": 0.0,
                "trial_type": "scanner_trigger",
                "stim_file": f"trigger_key_{TRIGGER_KEY}",
                "response": "",
                "rt": "",
                "is_repeat": ""
            })

        # Show instruction
        instr_on = run_clock.getTime()
        instr_text.draw()
        win.flip()
        core.wait(3.0)

        events_log.append({
            "onset": instr_on,
            "duration": run_clock.getTime() - instr_on,
            "trial_type": "instruction",
            "stim_file": "",
            "response": "",
            "rt": "",
            "is_repeat": ""
        })

        # PREREST - Initial blank trials (3 trials = 12s in NSD)
        fix_on = run_clock.getTime()
        event.clearEvents()
        while run_clock.getTime() - fix_on < REST_PRE:
            draw_fixation()
            win.flip()
            if QUIT_KEY in event.getKeys():
                raise KeyboardInterrupt

        events_log.append({
            "onset": fix_on,
            "duration": run_clock.getTime() - fix_on,
            "trial_type": "rest_pre",
            "stim_file": "",
            "response": "",
            "rt": "",
            "is_repeat": ""
        })

        # Present images
        for idx, (image_path, is_repeat) in enumerate(images, start=1):
            if not os.path.isfile(image_path):
                logging.error(f"Image not found: {image_path}")
                continue

            # Load and prepare image
            try:
                img_stim = visual.ImageStim(
                    win,
                    image=image_path,
                    size=(IMAGE_SIZE_PIXELS, IMAGE_SIZE_PIXELS),  # 714×714 pixels (8.4° visual angle)
                    units='pix'
                )
                logging.info(f"[IMAGE {idx}] Loaded: {os.path.basename(image_path)}, repeat={is_repeat}")
            except Exception as e:
                logging.error(f"[IMAGE {idx}] FAILED to load: {e}", exc_info=True)
                continue

            # Present image with fixation overlay (3s)
            img_on = run_clock.getTime()
            event.clearEvents()

            trial_response = None
            trial_rt = None

            while run_clock.getTime() - img_on < IMAGE_DURATION:
                img_stim.draw()
                draw_fixation()  # Semi-transparent fixation overlaid on image
                win.flip()

                # Collect response during image presentation
                if COLLECT_RESPONSES and trial_response is None:
                    keys = event.getKeys(keyList=[NEW_KEY, OLD_KEY, QUIT_KEY], timeStamped=run_clock)
                    if keys:
                        if keys[0][0] == QUIT_KEY:
                            raise KeyboardInterrupt
                        trial_response = keys[0][0]
                        trial_rt = keys[0][1] - img_on

                if QUIT_KEY in event.getKeys():
                    raise KeyboardInterrupt

            img_duration = run_clock.getTime() - img_on

            # Blank interval with fixation (1s)
            blank_on = run_clock.getTime()
            event.clearEvents()

            while run_clock.getTime() - blank_on < BLANK_DURATION:
                draw_fixation()
                win.flip()

                # Continue collecting response during blank if not yet responded
                if COLLECT_RESPONSES and trial_response is None:
                    keys = event.getKeys(keyList=[NEW_KEY, OLD_KEY, QUIT_KEY], timeStamped=run_clock)
                    if keys:
                        if keys[0][0] == QUIT_KEY:
                            raise KeyboardInterrupt
                        trial_response = keys[0][0]
                        trial_rt = keys[0][1] - img_on  # RT relative to image onset

                if QUIT_KEY in event.getKeys():
                    raise KeyboardInterrupt

            blank_duration = run_clock.getTime() - blank_on

            # Log trial
            events_log.append({
                "onset": img_on,
                "duration": img_duration + blank_duration,
                "trial_type": "image_trial",
                "stim_file": os.path.basename(image_path),
                "response": trial_response if trial_response else "",
                "rt": trial_rt if trial_rt else "",
                "is_repeat": is_repeat
            })

            logging.info(f"[TRIAL {idx}] Image: {os.path.basename(image_path)}, Response: {trial_response}, RT: {trial_rt:.3f}s" if trial_rt else f"[TRIAL {idx}] Image: {os.path.basename(image_path)}, No response")

        # POSTREST - Final blank trials (4 trials = 16s in NSD)
        post_on = run_clock.getTime()
        event.clearEvents()
        while run_clock.getTime() - post_on < REST_POST:
            draw_fixation()
            win.flip()
            if QUIT_KEY in event.getKeys():
                raise KeyboardInterrupt

        events_log.append({
            "onset": post_on,
            "duration": run_clock.getTime() - post_on,
            "trial_type": "rest_post",
            "stim_file": "",
            "response": "",
            "rt": "",
            "is_repeat": ""
        })

        # Save events
        tsv_path = write_events_tsv(events_log, SUB_ID, CURRENT_SESSION, run)
        logging.info(f"[Saved] {tsv_path}")

        # Show run completion message
        end_msg = visual.TextStim(
            win,
            text=f"Run {run} complete.\nPlease wait.",
            color=TEXT_COLOR,
            height=30,
            units='pix'
        )
        end_msg.draw()
        win.flip()
        core.wait(2.0)

    logging.info("=== Experiment finished ===")

except KeyboardInterrupt:
    logging.warning("Experiment aborted by user.")
finally:
    win.close()
    core.quit()
