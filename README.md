# Photo Import

Simple python script to copy photos from the given directory (e.g an SD card) into another directory. 

Written to bulk import photos into a date based directory structure and for adding useful metadata. 

## How does it work?

You'll need python3, imghdr, click and gexiv2. Then just run it with the source and destination directories as arguments

Example: python photo_import.py /media/sdcard0 ~/MyPhotos

This will copy all images from the sd card into ~/MyPhotos/YYYY/mm/dd/

## Usage

``` shell
Usage: photo_import.py [OPTIONS] SOURCE DESTINATION

Options:
  -k, --keywords TEXT     List of comma separated keywords (tags) to add to
                          XMP metadata
  -r, --credit TEXT       Name of photographer, agency, etc, to add to the XMP
                          metadata
  -d, --description TEXT  Description of the image to add to the XMP metadata
  -c, --copyright TEXT    Name of copyright holder of the image to add to the
                          XMP metadata
  -l, --location TEXT     Where the image was taken to add to the XMP metadata
  --help                  Show this message and exit.
``` 
