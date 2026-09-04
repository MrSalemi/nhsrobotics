#!/bin/bash
# v31 - Refuse to run when a symlink in the source tree points at nothing.
#       The cleanup decides a robot file is stale with [ -d ] and [ -f ],
#       and both follow symlinks, so a dangling link looks exactly like a
#       file somebody deleted on purpose. With libs_on_github not checked
#       out, that deleted the Alvik driver off a robot and printed a tick
#       -- twice. The check runs before the robot is touched at all.
# v30 - Never ship the laptop's droppings. __pycache__, .DS_Store and
#       stray .pyc files are stripped from the staging copy before upload,
#       and deleted from the robot if they are already there. The delete
#       runs BEFORE the whitelist, because a .robotignore entry means
#       "leave this alone" -- naming them there would preserve them.
# v29 - main.py now belongs to the student. From P04 on, main.py holds
#       their own "import workspace.pNN" line, so a plain sync leaves it
#       alone. Pass -c to reset it back to the shipped version. A robot
#       with no main.py at all still gets one, flag or not.
# v28 - FIXED: Added explicit removal of legacy /workspace/logs directory.
# v27 - FIXED: Added carriage return stripping (tr -d '\r') to remote output.
#       This fixes the bug where files were falsely identified as "extraneous"
#       due to invisible characters in the serial output.
#
# Developed with the assistance of Google Gemini

set -e

# --- CONFIGURATION ---
PORT=""
SOURCE_DIR=""
CLEAN_WORKSPACE=false
ROBOTIGNORE_FILENAME=".robotignore"
SAFETY_FILE_NAME="STORE_FILES_HERE_FOR_SAFETY.md"

# --- ARGUMENT PARSING ---
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -d|--dir) SOURCE_DIR="$2"; shift 2 ;;
        -p|--port) PORT="$2"; shift 2 ;;
        # -c wipes the student's own files: /workspace and main.py.
        -c|--clean-workspace) CLEAN_WORKSPACE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "Running initialize_robot.sh - v31 (broken symlinks stop the run)"

# --- VALIDATION ---
if [ -z "$SOURCE_DIR" ]; then echo "❌ ERROR: Source directory not specified. Use -d <path>."; exit 1; fi
if [ ! -d "$SOURCE_DIR" ]; then echo "❌ ERROR: Source '$SOURCE_DIR' is not a valid directory."; exit 1; fi

# --- BROKEN SYMLINK CHECK ---
# This has to happen before the robot is touched, because the cleanup
# further down deletes anything on the robot that is not in the source
# tree, and it decides that with [ -d ] and [ -f ]. Both follow symlinks,
# so a link pointing at nothing is indistinguishable from a file that was
# deliberately removed -- and the source tree is full of symlinks:
# lib -> ../../nhs_lib, and inside that, arduino_alvik, qwiic_i2c and
# qwiic_buzzer.py all point into libs_on_github.
#
# On 2026-09-04 those three submodules were not checked out. The sync
# deleted the entire Alvik driver from a robot, reported success, and did
# it again on the next run. There is no recovering a robot mid-class from
# that, so this refuses to start instead.
#
# find -L follows links, which is what makes a broken one report as
# type l. It also reaches links nested inside a linked directory, which
# is exactly where these live.
echo "🔗 Checking symlinks in '$SOURCE_DIR'..."
BROKEN_LINKS=$(find -L "$SOURCE_DIR" -type l 2>/dev/null | sort)
if [ -n "$BROKEN_LINKS" ]; then
    echo "❌ ERROR: these symlinks point at nothing:"
    echo "$BROKEN_LINKS" | sed 's/^/     /'
    echo ""
    echo "   Nothing on the robot was changed."
    echo ""
    echo "   The sync would read them as files you deleted and remove them"
    echo "   from the robot. Usually this means a submodule is not checked"
    echo "   out. From the repo root:"
    echo ""
    echo "       git submodule update --init --recursive"
    echo ""
    echo "   The objects are normally already in .git, so that works with"
    echo "   no network -- which matters at school, where GitHub is blocked."
    exit 1
fi
echo "   - all resolve"

# --- AUTO-DETECT PORT ---
if [ -z "$PORT" ]; then
    echo "🔎 Auto-detecting Alvik..."
    PORT=$(mpremote connect list | grep 'usbmodem' | awk '{print $1}' | head -n 1)
    if [ -z "$PORT" ]; then echo "❌ ERROR: No robot found."; exit 1; fi
    echo "✅ Found Alvik on port: $PORT"
fi
CONNECT_ARGS=("connect" "${PORT}")

# --- SETUP WORKSPACE ---
echo "------------------------------------------"
echo "🛠️  Checking /workspace..."
if ! mpremote "${CONNECT_ARGS[@]}" ls :workspace > /dev/null 2>&1; then
    mpremote "${CONNECT_ARGS[@]}" mkdir :workspace
    echo "   - Created /workspace"
fi

echo "🧹 Removing legacy log directories..."
mpremote "${CONNECT_ARGS[@]}" rm -r :/workspace/logs > /dev/null 2>&1 || true
mpremote "${CONNECT_ARGS[@]}" rm -r :/workspace/log > /dev/null 2>&1 || true
echo "   - Cleared logs"

# Ensure safety file
mpremote "${CONNECT_ARGS[@]}" exec "
import os
try:
    with open('/workspace/${SAFETY_FILE_NAME}', 'w') as f: f.write('# Safe place!')
except: pass
"

# --- OPTIONAL WORKSPACE CLEAN ---
if [ "$CLEAN_WORKSPACE" = true ]; then
    echo "🧹 Cleaning /workspace (keeping safety file)..."
    mpremote "${CONNECT_ARGS[@]}" exec "
import os
try:
    for f in os.ilistdir('/workspace'):
        name = f[0]
        if name != '${SAFETY_FILE_NAME}':
            path = '/workspace/' + name
            try:
                os.remove(path)
            except:
                pass 
            print('Deleted ' + path)
except: pass
"
    echo "✅ Workspace cleaned."
fi

# --- BUILD WHITELIST ---
# --- BUILD WHITELIST ---
WHITELIST=("/workspace") 
if [ -f "${SOURCE_DIR}/${ROBOTIGNORE_FILENAME}" ]; then
    echo "Found .robotignore. Building whitelist..."
    while IFS= read -r line; do
        # Strip invisible carriage returns from the file!
        line=$(echo "$line" | tr -d '\r')
        if [[ -n "$line" && ! "$line" =~ ^\s*# ]]; then
            # Ensure leading slash for comparison
            [[ "$line" != /* ]] && line="/$line"
            WHITELIST+=("$line")
        fi
    done < "${SOURCE_DIR}/${ROBOTIGNORE_FILENAME}"
fi

# --- PYTHON FILESYSTEM WALKER ---
WALKER_SCRIPT="
import os
def walk(top):
    try:
        for entry in os.ilistdir(top):
            name = entry[0]
            if name in ['.', '..']: continue
            
            # Construct full path
            if top == '/': path = '/' + name
            elif top == '': path = name
            else: path = top + '/' + name
            
            # Entry[1] is type. 0x4000=Dir, 0x8000=File
            is_dir = (entry[1] & 0x4000) == 0x4000
            
            if is_dir:
                print('D|' + path)
                walk(path)
            else:
                print('F|' + path)
    except OSError:
        pass
walk('')
"

echo "------------------------------------------"
echo "🔎 Scanning remote filesystem recursively..."
# FIX: Pipe output to tr -d '\r' to strip carriage returns
REMOTE_ITEMS=$(mpremote "${CONNECT_ARGS[@]}" exec "$WALKER_SCRIPT" | tr -d '\r')

echo "🧹 Comparing and Cleaning..."

# Process the remote list line by line
while IFS= read -r line; do
    if [[ -z "$line" ]]; then continue; fi
    
    TYPE=$(echo "$line" | cut -d'|' -f1)
    RPATH=$(echo "$line" | cut -d'|' -f2)
    
    # Normalize path with leading slash for whitelist check
    NORM_PATH="/$RPATH"
    [[ "$RPATH" == /* ]] || NORM_PATH="/$RPATH"

    # 1. JUNK CHECK, and it runs BEFORE the whitelist on purpose.
    # __pycache__ and .DS_Store exist locally -- the tests folder is a
    # symlink into the repo, and running the suite on a laptop fills it
    # with caches -- so the existence check further down would keep them
    # on the robot forever. Naming them in .robotignore makes that worse,
    # not better: a whitelisted path is one this loop leaves alone. So the
    # junk is matched here, by name, ahead of everything, and always goes.
    BASENAME="${RPATH##*/}"
    case "$BASENAME" in
        __pycache__|.DS_Store|*.pyc)
            echo "   - 🗑️  Removing junk: $RPATH"
            mpremote "${CONNECT_ARGS[@]}" rm -r ":$RPATH" > /dev/null 2>&1 || true
            continue
            ;;
    esac

    # 2. WHITELIST CHECK
    SKIP=false
    for allow in "${WHITELIST[@]}"; do
        if [[ "$NORM_PATH" == "$allow"* ]]; then
            # echo "   - Keeping '$RPATH' (Whitelisted)"
            SKIP=true
            break
        fi
    done
    if [ "$SKIP" = true ]; then continue; fi

    # 3. LOCAL EXISTENCE CHECK
    LOCAL_PATH="${SOURCE_DIR}/${RPATH}"
    
    EXISTS_LOCALLY=false
    if [ "$TYPE" == "D" ]; then
        if [ -d "$LOCAL_PATH" ]; then EXISTS_LOCALLY=true; fi
    else
        if [ -f "$LOCAL_PATH" ]; then EXISTS_LOCALLY=true; fi
    fi

    # 4. DELETE IF STALE
    if [ "$EXISTS_LOCALLY" = false ]; then
        echo "   - 🗑️  Removing extraneous item: $RPATH"
        mpremote "${CONNECT_ARGS[@]}" rm -r ":$RPATH" > /dev/null 2>&1 || true
    fi

done <<< "$REMOTE_ITEMS"

echo "✅ Cleanup complete."

# --- COPY FILES ---
# --- COPY FILES ---
echo "------------------------------------------"
echo "📂 Uploading local files..."

# Create a temporary staging directory
STAGING_DIR=$(mktemp -d)

# Copy everything to the staging directory first
cp -r "${SOURCE_DIR}/"* "$STAGING_DIR/"

# Drop the laptop's droppings: __pycache__ from running the tests, and
# .DS_Store from the Finder. Both appear at every level of the tree, so
# .robotignore cannot name them -- it matches exact paths from the image
# root. MicroPython reads neither.
JUNK_PATTERN=( -name '__pycache__' -o -name '.DS_Store' -o -name '*.pyc' )
JUNK=$(find "$STAGING_DIR" \( "${JUNK_PATTERN[@]}" \) -prune -print | wc -l | tr -d ' ')
find "$STAGING_DIR" \( "${JUNK_PATTERN[@]}" \) -prune -exec rm -rf {} +
if [ "$JUNK" -gt 0 ]; then
    echo "   - Skipping $JUNK cache or junk item(s)"
fi

# Remove ignored items from the staging directory before upload
for ignore in "${WHITELIST[@]}"; do
    # Skip /workspace as it's a remote-only system folder
    if [ "$ignore" != "/workspace" ]; then
        # Remove the leading slash to map to our local staging folder
        REL_IGNORE="${ignore#/}"
        if [ -e "${STAGING_DIR}/${REL_IGNORE}" ]; then
            rm -rf "${STAGING_DIR}/${REL_IGNORE}"
        fi
    fi
done

# --- PROTECT THE STUDENT'S main.py ---
# From P04 on, main.py is the student's: it holds their own
# "import workspace.pNN" line. Overwriting it on every sync silently
# undoes their work. So leave it alone unless -c was passed, or unless
# the robot has no main.py at all.
if [ "$CLEAN_WORKSPACE" = true ]; then
    echo "   - Resetting main.py (-c was passed)"
elif echo "$REMOTE_ITEMS" | grep -q '^F|main\.py$'; then
    rm -f "${STAGING_DIR}/main.py"
    echo "   - Keeping the robot's existing main.py (use -c to reset it)"
else
    echo "   - Robot has no main.py; installing the shipped one"
fi

# Bulk upload the filtered files
if [ "$(ls -A "$STAGING_DIR")" ]; then
    mpremote "${CONNECT_ARGS[@]}" cp -r "${STAGING_DIR}/"* :
else
    echo "   - No files to upload."
fi

# Clean up the temporary directory
rm -rf "$STAGING_DIR"

echo "✅ Synchronization complete."

