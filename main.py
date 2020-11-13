import re


def read_file(path):
    with open(path, 'r') as f:
        s = f.read()
    return s


if __name__ == "__main__":
    csText = read_file('SEBSettings.cs')
    csKeys = re.findall('\w+\s+=\s+\"(\w+)\";', csText)  # tìm các chuoi

    attrText = read_file('attributes.txt')
    attrKeys = re.findall("\(\d+,\s'(\w+)'", attrText)  # tìm các chuoi
    a = list(set(csKeys) - set(attrKeys))  # so sanh cac chuoi
    print(a)
