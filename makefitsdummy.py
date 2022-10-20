#!/usr/bin/env python3

import os
import sys
import astropy.io.fits as pyfits
import numpy
import uuid

if __name__ == "__main__":

    target_dir = sys.argv[1]
    try:
        imgsize = int(sys.argv[2])
    except:
        imgsize = 2048

    random_fn = os.path.join(target_dir, "dummy___%s.fits" % (str(uuid.uuid4().hex)))
    print(random_fn)

    # get random data
    data = numpy.random.randint(0, 65535, size=(imgsize,imgsize), dtype=numpy.uint16)
    print(data.shape)

    print("writing FITS file")
    pyfits.PrimaryHDU(data=data).writeto(random_fn)
