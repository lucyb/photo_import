#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Lucy B
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import click
from photoimport.PhotoImport import Metadata, PhotoImport

@click.command()
@click.argument('source',      type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.argument('destination', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.option('-k', '--keywords',    help='List of comma separated keywords (tags) to add to XMP metadata')
@click.option('-r', '--credit',      help='Name of photographer, agency, etc, to add to the XMP metadata')
@click.option('-d', '--description', help='Description of the image to add to the XMP metadata')
@click.option('-c', '--copyright',   help='Name of copyright holder of the image to add to the XMP metadata')
@click.option('-l', '--location',    help='The location of the image to add to the XMP metadata')
def run(source, destination, keywords, credit, description, copyright, location):
    metadata             = Metadata()
    metadata.credit      = credit
    metadata.description = description
    metadata.copyright   = copyright
    metadata.location    = location
    if keywords != None:
        metadata.keywords = keywords.split(',')

    PhotoImport(source, destination, metadata)
