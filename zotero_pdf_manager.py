#!/Users/Matt/.ve/general/bin/python
"""Shell script for copying papers in a zotero database to a desired location (usually a cloud service)"""
import sqlite3
import shutil
import os

# CHANGE THESE TO FIT YOUR NEEDS!!!
## Where you want your new directory to be
SAVE_LOCATION = "/Users/Matt/Desktop/tmp"
## Where your sqlite database is located
SQLITE_FILE = "/Users/Matt/Zotero/zotero.sqlite"
## Where your attachments are located
STORAGE_LOCATION = "/Users/Matt/Zotero/storage"

# DONT CHANGE THIS!!!
CURRENT_DATABASE_VERSION = 32

def query_sqlite(cursor, _select, _from, _where=None):
    """Query the sqlite database"""
    if _where is not None:
        cursor.execute("SELECT %s FROM %s WHERE %s" % (_select, _from, _where))
    else:
        cursor.execute("SELECT %s FROM %s" % (_select, _from))
    results = cursor.fetchall()
    return results

def pragma_sqlite(cursor, _pragma):
    """Get a pragma condition from the database"""
    cursor.execute("PRAGMA %s" % _pragma)
    result = cursor.fetchall()
    return result


def get_schema(cursor):
    """Get the sqlite schema for all the tables"""
    tables = query_sqlite(cursor, "name", "sqlite_master", "type='table'")
    schema_dict = {}
    for table in tables:
        # print(row[0])
        # print(table[0])
        cursor.execute("PRAGMA table_info('%s')" % table[0])
        schema_list = cursor.fetchall()
        schema = {}
        for row in schema_list:
            schema[row[1]] = row[0]
            # print(row)
        schema_dict[table[0]] = schema
    return schema_dict

def copy_file_to_location(src, dest, to_overwrite=False):
    """Handy function fro copying file to location and checking if to overwrite"""
    if os.path.isfile(dest) and not to_overwrite:
        return
    shutil.copyfile(src, dest)

def copy_collection_papers_to_directory(
        cursor,
        collection,
        schema_dict,
        save_location,
        paper_storage_location,
        strg_directory_dict,
        trash_ids):
    """Copy papers in a collection to a save location"""
    collection_id = collection[schema_dict["collections"]["collectionID"]]
    collection_name = collection[schema_dict["collections"]["collectionName"]]

    papers = query_sqlite(cursor, "*", "collectionItems", "collectionID=%d" % collection_id)
    print("Papers")
    print(len(papers))
    paper_item_id_idx = schema_dict["collectionItems"]["itemID"]

    for paper in papers:
        item_id = paper[paper_item_id_idx]

        # data = query_sqlite(cursor, "*", "items", "itemID=%d" % item_id)

        attachments = query_sqlite(
            cursor, "*", "itemAttachments", "parentItemID=%d" % item_id)

        item_data = query_sqlite(
            cursor, "*", "itemData", "itemID=%d AND fieldID=110" % item_id)
        # print(data[0][schema_dict["itemData"]["valueID"]])
        if item_data and item_id not in trash_ids:
            attachment_path_idx = schema_dict["itemAttachments"]["path"]
            attachment_locations = [
                strg_directory_dict[attachment[attachment_path_idx][8:]]
                if attachment[attachment_path_idx] is not None
                else None
                for attachment in attachments]

            for attachment_location_idx, attachment_location in enumerate(attachment_locations):
                path_idx = schema_dict["itemAttachments"]["path"]
                attachment_path = attachments[attachment_location_idx][path_idx]
                if attachment_path is not None:
                    # print(data[0][schema_dict["items"]["key"]],
                    #       name[0][1],
                    #       attachment_path[8:],
                    #       attachment_location)
                    src_file = os.path.join(
                        paper_storage_location,
                        attachment_location,
                        attachment_path[8:])
                    dest_file = os.path.join(
                        save_location,
                        collection_name,
                        attachment_path[8:])
                    copy_file_to_location(src_file, dest_file)
        # else:
        #     print("WHAT??", data)

def main():
    """Main script function"""
    delete_old_dir = False
    # save_location = "/Users/Matt/Google Drive/zotero_papers"
    save_location = SAVE_LOCATION
    paper_storage_location = STORAGE_LOCATION
    sqlite_file = SQLITE_FILE
    paper_annotated_storage_location = "/Users/Matt/Google Drive/annotated/"
    strg_directory_list = os.listdir(paper_storage_location)

    strg_directory_dict = {}
    for direct in strg_directory_list:
        # Check for directoryness to ignore .DS_Store
        if os.path.isdir(os.path.join(paper_storage_location, direct)):
            for f in os.listdir(os.path.join(paper_storage_location, direct)):
                strg_directory_dict[f] = direct

    in_place_update = True

    if os.path.isdir(save_location):
        if delete_old_dir:
            shutil.rmtree(save_location)
            os.makedirs(save_location)
            in_place_update = False
        elif in_place_update:
            print("In place update")
        else:
            raise NameError("Told not to delete location directory AND not to update in place")
    else:
        os.makedirs(save_location)
        print("Directory Created")

    # Connect with the zotero sqlite database, with read only!!
    conn = sqlite3.connect(sqlite_file, uri=True)
    cursor = conn.cursor()
    # Get zotero schema
    schema_dict = get_schema(cursor)

    vers = query_sqlite(cursor, "*", "version")
    if vers[0][1] != CURRENT_DATABASE_VERSION:
        print("Make sure version is correct")
        exit(0)

    trash = query_sqlite(cursor, "*", "deletedItems")
    print("TRASH: ", trash)

    trash_ids = [item[0] for item in trash]
    print(trash_ids)

    collections = query_sqlite(cursor, "*", "collections")
    for col in collections:
        print(col)
        collection_name = col[schema_dict["collections"]["collectionName"]]
        if not in_place_update:
            os.mkdir(os.path.join(save_location, collection_name))
        copy_collection_papers_to_directory(
            cursor,
            col,
            schema_dict,
            save_location,
            paper_storage_location,
            strg_directory_dict,
            trash_ids)
    conn.close()


if __name__ == "__main__":
    main()
