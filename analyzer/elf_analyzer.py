import os
import argparse
from elftools.elf.elffile import ELFFile
import logging
from elftools.elf.sections import SymbolTableSection
from pwnlib.elf.elf import ELF

def get_chk_names(elffile):
    function_names = set()

    symbol_tables = [s for s in elffile.iter_sections() if isinstance(s, SymbolTableSection)]

    for section in symbol_tables:
        if isinstance(section, SymbolTableSection):
            if section['sh_entsize'] != 0:
                for s in section.iter_symbols():
                    if s.name != "" and s.name.endswith('_chk'):
                        function_names.add(s.name)
    return function_names



def get_function_names(elffile):
    function_names = set()

    symbol_tables = [s for s in elffile.iter_sections() if isinstance(s, SymbolTableSection)]

    for section in symbol_tables:
        if isinstance(section, SymbolTableSection):
            if section['sh_entsize'] != 0:
                for s in section.iter_symbols():
                    if s.name != "":
                        function_names.add(s.name)
    return function_names


def analyze_single_file(binary, chk_func):
    file_stats = {"File":binary, "Arch":"", "DYN":"STC", "PIE/PIC":False, "EXEC":False, "Canary":False, "NX":False, "RELRO":"", "FORTIFY":0, "unsafe":0}
    if os.path.isfile(binary):
        fd = open(binary, 'rb')
        file_head = fd.read(4)
    else:
        return False, file_stats
    if 'ELF' in str(file_head):
        try:
            e = ELF(binary)
        except:
            return False, file_stats
        elff = ELFFile(fd)
        if len(chk_func) > 0:
            unsafe_func = set()
            for func in chk_func:
                unsafe_func.add(func.replace("__", "").replace("_chk", ""))
            func_names = get_function_names(elff)
            fortify = func_names.intersection(chk_func)
            unsafe = func_names.intersection(unsafe_func).difference(fortify)
            if len(fortify) > 0:
                file_stats["FORTIFY"] += len(fortify)
            if len(unsafe) > 0:
                file_stats["unsafe"] += len(unsafe)

        #arch = elff.get_machine_arch() 
        file_stats["Arch"] = e.arch + "-" + str(e.bits)
        file_stats["PIE/PIC"] = e.pie
        file_stats["Canary"] = e.canary
        file_stats["EXEC"] = e.executable
        file_stats["NX"] = e.nx
        for segment in elff.iter_segments():
            if segment['p_type'] == "PT_DYNAMIC":
               file_stats["DYN"] = "DYN"
        
        partial, full = False, False
        for segment in elff.iter_segments():
            if segment['p_type'] == 'PT_GNU_RELRO':
                if segment['p_flags'] & 2:
                    print("Warning! GNU_RELRO is Writable")
                    continue
                got_sh = elff.get_section_by_name('.got')
                if got_sh and segment.section_in_segment(got_sh):
                    partial = True
        
        dyn = elff.get_section_by_name('.dynamic')
        if dyn is not None:
            for i in dyn.iter_tags():
                if ((i['d_tag']) == 'DT_FLAGS' and i['d_val'] & 8) or ((i['d_tag']) == 'DT_FLAGS_1' and i['d_val'] & 1):
                    full = True
        if partial and full:
            file_stats["RELRO"] = "Full"
        elif partial:
            file_stats["RELRO"] = "Partial"
        fd.close()
        return True, file_stats
    else:
        fd.close()
        return False, file_stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="path to file")
    args = parser.parse_args()
    file_path = args.file
    
    
    # load all fortify functions from libc-2.31.so
    libc_rd = open("/lib/x86_64-linux-gnu/libc-2.31.so", "rb")        
    elflibc = ELFFile(libc_rd)
    chk_func = get_chk_names(elflibc)
    libc_rd.close()

    # check mitigations used in the file
    elf, file_stats = analyze_single_file(file_path, chk_func)
    if elf:
        print("File name:", file_stats['File'])              
        print("Arch:", file_stats['Arch'])              
        if file_stats['DYN'] == 'DYN':
            print("Dynamic linked: Yes")              
        if file_stats['PIE/PIC']:
            print("PIE/PIC: Yes")
        if file_stats['Canary']:
            print("Protected with Canary: Yes")
        else:
            print("Protected with Canary: No")

        if file_stats['NX']:
            print("Protected with NX: Yes")
        else:
            print("Protected with NX: No")
        if file_stats['RELRO'] == 'Full':
            print("Protected with full RELRO")
        elif file_stats['RELRO'] == 'Partial':
            print("Protected with partial RELRO")
        else:
            print("No RELRO Protection")
        if file_stats['FORTIFY'] > 0:
            print("Protected with Fortify Source: Yes")
        else:
            print("No Fortify Source Protection")
    else:
        print("Skip for None-ELF file")


if __name__ == "__main__":
    main()



