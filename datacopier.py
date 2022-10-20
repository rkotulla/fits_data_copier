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

import watchdog
import watchdog.observers
import watchdog.events


def update_and_compress(source_dir, stage_dir, target_dir=None, filelist=None, overwrite=True):

    # print("Updating and compressing")

    # strip source path and get destination path
    src = os.path.abspath(source_dir)
    # print("source:", src)
    # print("stage:", stage_dir)

    for filename in filelist:
        src_relative = os.path.abspath(filename)[len(src)+1:]
        if (src_relative == ''):
            continue

        _,extension = os.path.splitext(src_relative) #.lower()
        if (extension.lower() == ".fits"):
            # run fpack
            dest_filename = os.path.join(stage_dir, src_relative)+".fz"
            if (overwrite or not os.path.isfile(dest_filename)):
                fpack_cmd = 'fpack -Y -S %s > %s' % (filename, dest_filename)
                print("FPACK'ING  %s --> %s (%s)" % (src_relative, dest_filename, fpack_cmd))
                retval = os.system(fpack_cmd)
                # print(retval)
                if (retval != 0):
                    dest_filename = os.path.join(stage_dir, src_relative)
                    print("### FPACK FAILED, COPYING   ", src_relative, "-->", dest_filename)
                    copy_cmd = "cp %s %s" % (filename, dest_filename)
                    os.system(copy_cmd)
            else:
                print("SKIPPING   %s --> %s" % (filename, dest_filename))
            pass
        else:
            dest_filename = os.path.join(stage_dir, src_relative)
            print("COPYING   ", src_relative, "-->", dest_filename)
            copy_cmd = "cp %s %s" % (filename, dest_filename)
            os.system(copy_cmd)

    # now that all files are copied/compressed, upload data to target destination
    if (target_dir is not None):
        rsync_cmd = "rsync -au %s/ %s" % (stage_dir, target_dir)
        print("Updating files on target destination (%s)" % (target_dir))
        os.system(rsync_cmd)

    return


class FileCopierWatchdog(watchdog.events.FileSystemEventHandler):

    def __init__(self, source_dir, stage_dir, target_dir=None, overwrite=True):
        super().__init__()
        self.source_dir = source_dir
        self.stage_dir = stage_dir
        self.target_dir = target_dir
        self.overwrite = overwrite

    # def on_any_event(self, event):
    #     print(event.event_type, event.src_path)

    def on_closed(self, event):
        print("Found newly created file:", event.src_path)
        # print("on_created", event.src_path)
        # print(event.src_path.strip())
        update_and_compress(
            source_dir=self.source_dir,
            stage_dir=self.stage_dir,
            target_dir=self.target_dir,
            overwrite=self.overwrite,
            filelist=[event.src_path]
        )
        # if((event.src_path).strip() == ".\test.xml"):
        # print("Execute your logic here!")


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
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

    print("Running initial sync")
    search_glob = os.path.join(args.directory[0], "**")
    initial_list = glob.glob(search_glob, recursive=True)
    update_and_compress(source_dir=args.directory[0],
                        stage_dir=args.staging_directory,
                        target_dir=args.target_directory,
                        filelist=initial_list,
                        overwrite=False)

    print("Setting up directory watchdog")
    # event_handler = watchdog.events.LoggingEventHandler()
    event_handler = FileCopierWatchdog(
        source_dir=args.directory[0],
        stage_dir=args.staging_directory,
        target_dir=args.target_directory,
        overwrite=True,
    )
    observer = watchdog.observers.Observer()
    observer.schedule(
        event_handler=event_handler,
        path=args.directory[0],
        recursive=True,
    )
    observer.start()


    try:
        while (True):
            sys.stdout.write("\rCurrent time: %s" % (datetime.datetime.now()))
            sys.stdout.flush()
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        print("\nFinishing up work and shutting down")
        observer.join()
        print("All done, good bye")


    # print(search_glob)
    #
    # previous_monitor_set = set()
    # new_monitor_set = set()
    #
    #
    #
    #
    # try:
    #     while (True):
    #
    #         for filename in glob.glob(search_glob, recursive=True):
    #             # print("\n -- ".join(["files:"]+file)
    #             # print(filename)
    #
    #             mod_time = os.path.getmtime(filename)
    #             # print(filename, mod_time)
    #             new_monitor_set.add((filename, mod_time))
    #
    #         difference_set = new_monitor_set - previous_monitor_set
    #         # print(difference_set)
    #
    #
    #         print("Last check @ %s: Found %d new entries to sync" % (datetime.datetime.now(), len(difference_set)))
    #         if (len(difference_set) > 0):
    #             print(difference_set)
    #
    #         # copy/compress all files to staging directory
    #
    #         # run rsync to complete transfer
    #
    #         previous_monitor_set = new_monitor_set
    #
    #         time.sleep(1)
    #         # break
    #
    #
    # except KeyboardInterrupt:
    #     print("Shutting down")
    #



