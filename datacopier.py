#!/usr/bin/env python3

import sys
print(sys.path)

import logging
import multiprocessing
import os
import queue
import threading
import time
import glob
import datetime
import argparse
import glob




if __name__ == "__main__":

    logger = logging.getLogger("RunAnalysis")

    cmdline = argparse.ArgumentParser()
    cmdline.add_argument("--stagedir", dest="staging_directory", default=None,
                         help="staging directory of compressed files")
    cmdline.add_argument("--recursive", dest="recursive", action='store_true',
                         help="also check for files in sub-directories")
    cmdline.add_argument("--targetdir", dest="target_directory", default=None,
                         help="addition to output filename")

    cmdline.add_argument("directory", nargs="+",
                         help="name of directory to monitor")


    args = cmdline.parse_args()

    search_glob = os.path.join(args.directory[0], "**")
    print(search_glob)

    previous_monitor_set = set()
    new_monitor_set = set()

    try:
        while (True):

            for filename in glob.glob(search_glob, recursive=True):
                # print("\n -- ".join(["files:"]+file)
                # print(filename)

                mod_time = os.path.getmtime(filename)
                # print(filename, mod_time)
                new_monitor_set.add((filename, mod_time))

            difference_set = new_monitor_set - previous_monitor_set
            # print(difference_set)


            print("Last check @ %s: Found %d new entries to sync" % (datetime.datetime.now(), len(difference_set)))
            if (len(difference_set) > 0):
                print(difference_set)

            # copy/compress all files to staging directory

            # run rsync to complete transfer

            previous_monitor_set = new_monitor_set

            time.sleep(1)
            # break


    except KeyboardInterrupt:
        print("Shutting down")




