import csv


def csv_dict_writer(path, fieldnames, data):
    with open(path, 'a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    csv_file.close()
