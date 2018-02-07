#! /usr/bin/env python

import argparse
import os
import re
import shutil
import tempfile


class TermColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def find_lines(lines):
    z_line, skirt_line = "", ""
    for line in lines:
        if "; move to next layer (0)" in line:
            if line[0] is ';':
                print(TermColors.FAIL + "File seems to have already been patched." + TermColors.ENDC)
                quit(2)
            z_line = line
        elif "; move to first skirt point" in line and not skirt_line:
            skirt_line = line
    return (z_line, skirt_line)


def patch_lines(f, lines, z_line, skirt_line, joined_line):
    for i, line in enumerate(lines):
        if line == z_line:
            lines[i] = '; ' + line
        elif line == skirt_line:
            lines[i] = joined_line
    f.seek(0)
    f.truncate()
    f.writelines(lines)


def backup_file(original_path):
    temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(original_path) + '.bak')
    shutil.copy2(original_path, temp_path)
    return temp_path


def process(gcode_path):
    with open(gcode_path, "r+") as f:
        lines = f.readlines()
        z_line, skirt_line = find_lines(lines)
        if z_line and skirt_line:
            z_line_trimmed = z_line[:z_line.find(';') - 1]
            skirt_line_trimmed = skirt_line[:skirt_line.find(';') - 1]
            print(("Joining lines " +
                   TermColors.HEADER + "\"{}\"" + TermColors.ENDC + " & " +
                   TermColors.HEADER + "\"{}\"" + TermColors.ENDC + "...").format(z_line_trimmed, skirt_line_trimmed))
            z_line_coord = re.search('Z[0-9\.]+', z_line_trimmed).group()
            z_line_speed = re.search('F[0-9\.]+', z_line_trimmed).group()
            skirt_line_coords = re.search('X[0-9\.]+ Y[0-9\.]+', skirt_line_trimmed).group()
            joined_line = "G1 {} {} {} ; move to next layer (0) and to first skirt point\n".format(
                skirt_line_coords,
                z_line_coord,
                z_line_speed
            )
            print(("Joined line is: " + TermColors.OKBLUE + "\"{}\"" + TermColors.ENDC + ".").format(joined_line.strip()))
            print("Backing up GCode file to new copy...", end='\r')
            temp_path = backup_file(gcode_path)
            print("Backing up GCode file to new copy: {}".format(temp_path))
            print("Writing changes to original GCode file...")
            patch_lines(f, lines, z_line, skirt_line, joined_line)
            print(TermColors.OKGREEN + "Done!" + TermColors.ENDC)
        else:
            print(TermColors.FAIL + "Needed lines not found, nothing to join." + TermColors.ENDC)
            quit(1)


parser = argparse.ArgumentParser(description="""
Join the first XY & Z movements in the GCode output of Slic3r and Slic3r PE,
producing a smoother initial move and preventing marks/oozes on the bed.
""")
parser.add_argument('gcode', metavar='<GCode file>',
                    help='the GCode file to process')
args = parser.parse_args()
process(args.gcode)
