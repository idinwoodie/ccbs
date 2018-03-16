"""
Scrubs duplicates from raw data.

Criteria to update existing response:
    - The updated response must not replace a complete entry for a specific dog
      with an incomplete entry.
    - The updated response must not replace a complete entry for a specific dog
      with an entry for a different dog.
    - The updated response must not detract from the existing data of a complete
      entry for a specific dog.

Criteria to dispose subsequent response:
    - The updated response replaces a complete entry for a specific dog with an
      incomplete entry.
    - The updated response replaces a complete entry for a specific dog with an
      entry for a different dog.
    - The updated response detracts from the existing data of a complete entry
      for a specific dog.

Criteria to keep existing and subsequent responses:
    - Both the existing and updated responses contain complete dog-specific
      entries.
    - No complete entry for the same specific dog is shared in both responses.
"""

import argparse
import csv
import os
import shutil


# Parse the input file from the command-line arguments.
parser = argparse.ArgumentParser(description='Scrub duplicates from raw data.')
parser.add_argument('filename')
args = parser.parse_args()
infile = args.filename

# Verify the file to be scrubbed.
if not os.path.isfile(infile):
    print('Error: entered file does not exist')
    quit()

# Verify the output file.
base = os.path.splitext(os.path.basename(infile))[0]
outfile = base + '.data'
tempfile = ''
if infile == outfile:
    tempfile = outfile
    outfile = outfile + '.temp'

# Parse the raw data with relevant filters.
status_sum_dict = {}
dupe_cnt = 0
status_dict = {}
data_dict = {}
dog_dict = {}
with open(infile, 'r') as fin:
    with open(outfile, 'w') as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        first_row = True
        for row in csv.reader(fin, delimiter=','):
            write_row = False
            if not first_row:
                user_hash = row[8]
                status = [int(row[10]), int(row[145]), int(row[280]),
                          int(row[415]), int(row[550]), int(row[688])
                ]
                status_sum = sum(status)
                dogs = [row[11], row[146], row[281], row[416], row[551]]
                dogs = [x for x in dogs if x != '']
                if user_hash in status_dict:
                    dupe_cnt += 1
                    if status[5] == 0:
                        print('Duplicate found: updated entry is incomplete, '
                              'discard updated')
                    elif status_dict[user_hash][5] == 0:
                        print('Duplicate found: existing entry is incomplete, '
                              'save updated')
                        write_row = True
                    else:
                        old_dogs = set(dog_dict[user_hash])
                        new_dogs = set(dogs)
                        if not bool(old_dogs.symmetric_difference(new_dogs)):
                            print('Duplicate found: same set of dogs, ', end='')
                            if status_sum_dict[user_hash] <= status_sum:
                                print('but more complete data, save updated')
                                write_row = True
                            else:
                                print('but less complete data, discard updated')
                        elif bool(new_dogs.intersection(old_dogs)):
                            print('Duplicate found: at least one dog shared, ', end='')
                            if status_sum_dict[user_hash] <= status_sum:
                                print('but more complete data, save updated')
                                write_row = True
                            else:
                                print('but less complete data, discard updated')
                        else:
                            print('Duplicate found: no shared data, save both')
                            write_row = True
                else:
                    write_row = True
            else:
                first_row = False
            if write_row:
                data_dict[user_hash] = row
                status_dict[user_hash] = status
                dog_dict[user_hash] = dogs
                status_sum_dict[user_hash] = status_sum
                writer.writerow(row)

# If a temp file was used, move the results back to the requested destination.
if not tempfile == '':
    shutil.move(outfile, tempfile)

# Let the user know the script has finished.
print('Duplicates scrubbing complete.')
