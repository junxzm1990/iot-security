import argparse
import binaryninja as binja


def stack_check(binary):
    bv = binja.BinaryViewType.get_view_of_file_with_options(binary)
    start = bv.start
    str_addr = bv.find_next_text(start, 'stack smashing detected')
    if str_addr == None:
        return False
    func = bv.get_functions_containing(str_addr)[0]
    if len(list(bv.get_code_refs(func.start))) > 0:
        return True
    else:
        return False

def fortify_check(binary):
    bv = binja.BinaryViewType.get_view_of_file_with_options(binary)
    start = bv.start
    str_addr = bv.find_next_text(start, 'buffer overflow detected')
    addr_list = []
    while str_addr != None:
        start = str_addr + 1
        addr_list.append(str_addr)
        str_addr = bv.find_next_text(start, 'buffer overflow detected')
    if len(addr_list) == 0:
        return False
    for addr in addr_list:
        if len(bv.get_functions_containing(addr)) == 0:
            # skip string in data
            continue
        func = bv.get_functions_containing(addr)[0]
        if len(list(bv.get_code_refs(func.start))) > 0:
            return True
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="path to file")
    args = parser.parse_args()
    file_path = args.file

    # check stack canary in staticaly linked binary
    stack_chk = stack_check(file_path)
    if stack_chk:
        print("Protected with Stack Canary: Yes")
    else:
        print("Protected with Stack Canary: No")
    fortify_chk = fortify_check(file_path)
    if fortify_chk:
        print("Protected with Fortify Source: Yes")
    else:
        print("Protected with Fortify Source: No")
    

if __name__ == "__main__":
    main()


