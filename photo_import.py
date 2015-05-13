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
import imghdr
import os.path
import os
import stat
import shutil

from datetime import datetime
from gi.repository import GExiv2
	
class Metadata(object):
	# For more info about photo metadata, see http://www.photometadata.org/META-101-metadata-Q-and-A
	# TODO something like title probably isn't relevant for bulk import, but something like setting a UUID might be..
	keywords    = []
	credit      = ""
	description = ""
	copyright   = ""
	location    = ""

	# EXIF TAGs
	TAG_EXIF = "Exif.Image."
	TAG_EXIF_PHOTO = "Exif.Photo."
	
	TAG_EXIF_DATETIME = TAG_EXIF_PHOTO + "DateTimeOriginal"
	
	#XMP TAGS
	TAG_XMP_IPTC = "Xmp.iptc."
	
	##See suggested fields from: http://www.controlledvocabulary.com/imagedatabases/iptc_naa.html
	
	##List of subject data by descrete words/phrases
	TAG_XMP_KEYWORDS    = TAG_XMP_IPTC + "Keywords"
	##Photographer's name, agency name, etc
	TAG_XMP_CREDIT      = TAG_EXIF + "Artist"
	##similar to filename; may include unique identifier
	TAG_XMP_TITLE       = TAG_XMP_IPTC + "Title"
	##Long form description of Subject and related subject data in a Natural Language caption
	TAG_XMP_DESCRIPTION = TAG_XMP_IPTC + "Description"
	##Photographers name, agency name, rights
	TAG_XMP_COPYRIGHT   = TAG_EXIF + "Copyright"
	##Location of image
	TAG_XMP_LOCATION    = TAG_XMP_IPTC + "Location"
	
	
class Photo(object):
	def __init__(self, currentLocation, filename):
		self.currentLocation = currentLocation
		self.filename	     = filename

	def getCreatedDate(self):
		try:
			md = GExiv2.Metadata()
			md.open_path(os.path.join(self.currentLocation, self.filename))
			if md.has_tag(Metadata.TAG_EXIF_DATETIME):
				createdDate = md.get_tag_string(Metadata.TAG_EXIF_DATETIME)
				try:
					return datetime.strptime(createdDate, "%Y:%m:%d %H:%M:%S")
				except Exception as ex:
					click.echo("Unable to parse the created date " + createdDate + " for " + self.filename)
					click.echo(ex)	
		except Exception as ex2:
			click.echo("Unable to parse metadata for "+self.filename)
			click.echo(ex2)
		
		return None    

	def save(self, destinationPath, metadata):
		if destinationPath == None or destinationPath == "":
			return False
		
		destinationFullPath = os.path.join(destinationPath, self.filename)
		sourceFullPath      = os.path.join(self.currentLocation, self.filename)
		
		#Ignore existing photos, even if it's a broken symlink (for those of us using git annex)
		if os.path.lexists(destinationFullPath):
			click.echo("Photo " + self.filename + " already exists. Skipping..")
			return False
		
		#Copy photo
		click.echo("Copying photo " + self.filename + " ..")
		shutil.copy2(sourceFullPath, destinationPath, follow_symlinks=True)
		#Chmod photo to 644, so that we have permission to update the metadata
		os.chmod(destinationFullPath, mode = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH))
					
		try:
			#Update the file we've just written
			self.updateMetadata(metadata, destinationFullPath)
		except Exception as ex:
			click.echo("Unable to write metadata for " + self.filename)	
			click.echo(ex)	

		return True

	def updateMetadata(self, metadata, fullFilePath):
		md = GExiv2.Metadata()
		md.open_path(fullFilePath)
		if metadata.keywords:
			md[Metadata.TAG_XMP_KEYWORDS]    = ",".join(metadata.keywords)
		if metadata.credit:
			md[Metadata.TAG_XMP_CREDIT]      = metadata.credit
		if metadata.description:
			md[Metadata.TAG_XMP_DESCRIPTION] = metadata.description
		if metadata.copyright:
			md[Metadata.TAG_XMP_COPYRIGHT]   = metadata.copyright
		if metadata.location:
			md[Metadata.TAG_XMP_LOCATION]    = metadata.location
		
		#TODO figure out what's changed and update sensibly
		#TODO should we update things that are already set or just blank things - need bool param?
		
		md.save_file()
		
	def prettyPrint(self):
		click.echo(self.currentLocation)
		click.echo(self.filename)
		click.echo(self.getCreatedDate().year)
		click.echo(self.getCreatedDate().month)
		click.echo(self.getCreatedDate().day)
		
class PhotoImport(object):			
	def __init__(self, source, destination, metadata):
		self.photos      = PhotoImport.getPhotos(source)
		self.destination = destination
		self.metadata    = metadata
		self.processPhotos()

	def processPhotos(self):
		for photo in self.photos:
			if photo.getCreatedDate() == None:
				#Throw a real error somewhere sensible
				click.echo("Photo " + photo.filename + " does not have a created date. Skipping..")
				continue
				
			photo.save(self.createDirectoryStructure(photo), self.metadata)

	def createDirectoryStructure(self, photo):
		datetime = photo.getCreatedDate()
		#Create the appropriate directory if it doesn't already exist and throw an error if the attempt fails
		#Directory structure is 'destination/yyyy/MM/dd/'
		folderYear  = str(datetime.year)
		folderMonth = str(datetime.month).zfill(2)
		folderDay   = str(datetime.day).zfill(2)
		destinationAbsPath = os.path.join(os.path.join(os.path.join(PhotoImport.absolutePath(self.destination), folderYear), folderMonth), folderDay)
		try:
			os.makedirs(destinationAbsPath, mode=0o755, exist_ok=True)
		except OSError as oserror:
			if oserror.errno == oserror.EEXIST and os.path.isdir(destinationAbsPath):
				pass
			else: raise
		return destinationAbsPath

	@staticmethod
	def getPhotos(source):
		files = []
		for (dirpath, dirnames, filenames) in os.walk(source):
			for filename in filenames:
				absfilename = PhotoImport.absolutePath(os.path.join(dirpath, filename))
				if PhotoImport.isPhoto(absfilename):
					files.append(Photo(dirpath, filename))
			break
		return files
	
	@staticmethod
	def isPhoto(filename):
		# Check the filetype - imghdr detects raws as well as jpegs, etc, but 
		# falls over if the file is a symlink 
		# See https://docs.python.org/3/library/imghdr.html
		return (not(os.path.islink(filename)) and (imghdr.what(filename) != None or filename.endswith(".RAF")))

	@staticmethod
	def absolutePath(path):
		return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


@click.command()
@click.argument('source',      type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.argument('destination', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.option('-k', '--keywords',    help='List of comma separated keywords (tags) to add to XMP metadata')
@click.option('-r', '--credit',      help='Name of photographer, agency, etc, to add to the XMP metadata')
@click.option('-d', '--description', help='Description of the image to add to the XMP metadata')
@click.option('-c', '--copyright',   help='Name of copyright holder of the image to add to the XMP metadata')
@click.option('-l', '--location',    help='The location of the image to add to the XMP metadata')
def doPhotoImport(source, destination, keywords, credit, description, copyright, location):
	metadata             = Metadata()
	metadata.credit      = credit
	metadata.description = description
	metadata.copyright   = copyright
	metadata.location	 = location
	if keywords != None:
		metadata.keywords = keywords.split(',')
	
	photoImport = PhotoImport(source, destination, metadata)
	
if __name__ == '__main__':
	doPhotoImport()
