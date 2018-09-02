#!/Users/Matt/.ve/general/bin/python

import sqlite3
import shutil
import os
import sys

# black_listed
# The nice thing is I have a list of 

delete_old_dir = False
save_location = "/Users/Matt/Desktop/tmp"
paper_storage_location = "/Users/Matt/Zotero/storage"
paper_annotated_storagel_location = "/Users/Matt/Google Drive/annotated/"
sqlite_file = "/Users/Matt/Zotero/zotero.sqlite"
strg_directory_list = os.listdir(paper_storage_location)

strg_directory_dict = {}
for direct in strg_directory_list:
    # Check for directoryness to ignore .DS_Store
    if os.path.isdir(os.path.join(paper_storage_location, direct)):
        for f in os.listdir(os.path.join(paper_storage_location, direct)):
            strg_directory_dict[f] = direct

# print(strg_directory_dict)




in_place_update = False

if os.path.isdir(save_location):
    if not delete_old_dir:
        print("Told not to delete old directory")
        exit(1)
    else:
        shutil.rmtree(save_location)
        os.makedirs(save_location)
else:
    os.makedirs(save_location)
    print("Directory Created")


conn = sqlite3.connect(sqlite_file, uri=True)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
schema_dict = {}
for table in tables:
    # print(row[0])
    print(table[0])
    c.execute("PRAGMA table_info('%s')" % table[0])
    schema_list = c.fetchall()
    schema = {}
    for row in schema_list:
        schema[row[1]] = row[0]
        print(row)
    schema_dict[table[0]] = schema

c.execute("SELECT * FROM version")
vers = c.fetchall()
print(vers)
if vers[0][1] != 32:
    print("Make sure version is correct")
    exit(0)
# print(c.fetchall())

# c.execute("SELECT * FROM customFields")
# print(c.fetchall())
# exit(0)

c.execute("SELECT * FROM deletedItems")
trash = c.fetchall()
print("TRASH: ", trash)
# c.execute("SELECT * FROM items WHERE itemID=%d" % (trash[0][schema_dict["deletedItems"]["itemID"]]))
# print(c.fetchall())

trash_ids = [item[0] for item in trash]
print(trash_ids)

print("")
c.execute("SELECT * FROM collections")
collections = c.fetchall()
for col in collections:
    print(col)
    os.mkdir(os.path.join(save_location, col[schema_dict["collections"]["collectionName"]]))
    c.execute("SELECT * FROM collectionItems WHERE collectionID=%d" % (col[schema_dict["collections"]["collectionID"]]))
    papers = c.fetchall()
    print("Papers")
    print(len(papers))
    for paper in papers:
    # print(papers)
        c.execute("SELECT * FROM items WHERE itemID=%d" %(paper[schema_dict["collectionItems"]["itemID"]]))
        data = c.fetchall()
        # print("Paper Data")
        # print(data)
        # print("Paper Key")
        # print(data[0][schema_dict["items"]["key"]])

        c.execute("SELECT * FROM itemAttachments WHERE parentItemID=%d" % (paper[schema_dict["collectionItems"]["itemID"]]))
        attachments = c.fetchall()
        # print(attachments)
        # open(attachments[0][schema_dict["itemAttachments"]["path"]])
        
        c.execute("SELECT * FROM itemData WHERE itemID=%d AND fieldID=110" %(paper[schema_dict["collectionItems"]["itemID"]]))
        item_data = c.fetchall()
        # print(data[0][schema_dict["itemData"]["valueID"]])
        if len(item_data) > 0:
            c.execute("SELECT * FROM itemDataValues WHERE valueID=%d" % (item_data[0][schema_dict["itemData"]["valueID"]]))
            name = c.fetchall()
            attachment_file_locations = [strg_directory_dict[attachment[schema_dict["itemAttachments"]["path"]][8:]] if attachment[schema_dict["itemAttachments"]["path"]] is not None else None  for attachment in attachments]
            if data[0][schema_dict["items"]["itemID"]] in trash_ids:
                for attachment_file_location_idx, attachment_file_location in enumerate(attachment_file_locations):
                    print(data[0][schema_dict["items"]["key"]], name[0][1], attachment_file_location, "TRASHED")
            else:
                for attachment_file_location_idx, attachment_file_location in enumerate(attachment_file_locations):
                    if attachments[attachment_file_location_idx][schema_dict["itemAttachments"]["path"]] is not None:
                        print(data[0][schema_dict["items"]["key"]],
                              name[0][1],
                              attachments[attachment_file_location_idx][schema_dict["itemAttachments"]["path"]][8:],
                              attachment_file_location)
                        shutil.copyfile(
                            os.path.join(
                                paper_storage_location,
                                attachment_file_location,
                                attachments[attachment_file_location_idx][schema_dict["itemAttachments"]["path"]][8:]),
                            os.path.join(
                                save_location,
                                col[schema_dict["collections"]["collectionName"]],
                                attachments[attachment_file_location_idx][schema_dict["itemAttachments"]["path"]][8:]
                            ))
        else:
            print("WHAT??", data)
conn.close()

