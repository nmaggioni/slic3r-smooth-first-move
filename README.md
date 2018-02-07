# slic3r-smooth-first-move
A Slic3r post-processing script that joins the initial XY &amp; Z movements, producing a smoother initial move and preventing marks/oozes on the bed.

**Currently works with skirts only, if you are not using a skirt then this script won't work for you.** Adding support for other types of first layers is quite trivial anyhow.

```
usage: join_first_xyz.py [-h] <GCode file>

Join the first XY & Z movements in the GCode output of Slic3r and Slic3r PE,
producing a smoother initial move and preventing marks/oozes on the bed.

positional arguments:
  <GCode file>  the GCode file to process

optional arguments:
  -h, --help    show this help message and exit
```
