# datacopier

## Purpose: 
Monitors a directory of data, automatically compresses the data and uploads it to a remote destination via 
rsync.


## How to use:
> python3 datacopier.py --stage_dir=some_staging_directory --targetdir=user@server:/some/dir your_data_directory


## What's needed:
- rsync (for data transfer)
- fpack (compression of FITS files)

