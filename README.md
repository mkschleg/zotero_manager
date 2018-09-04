zotero_manager
===================

Simple python script for copying attachments to another folder.

Requirements
---------------

- Python3


Install
---------------

1. Clone repository
2. Update where your python executable is located.
3. Change `SAVE_LOCATION`, `SQLITE_FILE`, and `STORAGE_LOCATION` to desired values.
4. optional - symlink to your bin so it is available on your shell PATH.


Behavior
---------------

This script will create a directory, and copy ALL attachments to this folder. This is best used with something like
zotfile with pdfs named with titles of papers. On subsequent runs in will update the folder with new attachments (or 
with renamed attachments of PDFs already there).

Planned updates
------------------

This is currently in a good working state for my needs, but there are some nice things that I want to add in the future
to make the management a bit easier with annotated files.

- Annotated file management
- file filter (So you can specify what kind of files you want)
- Database for managing what has been added and what hasn't rather than by file.
- Possibly better way of finding the attachment locations (I'm still unsure how zotero handles this...).
