import os, sys
import re
import subprocess
from pathlib import Path
import tempfile

def get_pixel_map_dump(pl2_file_path):
    # Determine where to look for the pixelmapdump.exe file
    if getattr(sys, "frozen", False):
        parent_folder = Path(sys._MEIPASS)
    else: 
        parent_folder = Path(__file__).parent
    
    executable_path = parent_folder / "pixelmapdump.exe"
    if not executable_path.exists():
        raise FileNotFoundError(f"Pixelmapdump executable not found at {executable_path}")

    with tempfile.NamedTemporaryFile(mode="w+") as tmp_out:
        with tempfile.NamedTemporaryFile(mode="w+") as tmp_err:
            print("sys.frozen:", getattr(sys, "frozen", False))
            print("sys._MEIPASS:", getattr(sys, "_MEIPASS", None))
            print("executable_path:", executable_path)
            print("Exists?", os.path.exists(executable_path))

            p = subprocess.Popen([executable_path, pl2_file_path], stdout=tmp_out, stderr=tmp_err, text=True)
            p.wait()

            tmp_out.seek(0)
            tmp_err.seek(0)
            stdout = tmp_out.read()
            stderr = tmp_err.read()
    
    probe_pattern = re.compile(r"Port \d+ probe = \w+")
    timestamp_pattern = re.compile(r"t = (.+)\nbad\: (.+)")

    probe_info = probe_pattern.findall(stdout)
    timestamp_info = [(float(timestamp), [] if bad_channels=="no bad channels" \
                       else [int(bad_channel) for bad_channel in bad_channels.split(",")]) \
                        for timestamp, bad_channels in timestamp_pattern.findall(stdout)]

    return probe_info, timestamp_info