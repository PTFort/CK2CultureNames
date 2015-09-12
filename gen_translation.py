import re
from os import listdir
from os.path import isfile, join

from collections import defaultdict

class TranslationPrinter:

    def __init__(self):
        self.last_name = ''
        self.last_type = ''

        self.e_translations = defaultdict(list)
        self.k_translations = defaultdict(list)
        self.d_translations = defaultdict(list)
        self.c_translations = defaultdict(list)
        self.b_translations = defaultdict(list)

        self.empire_names = {}
        self.kingdom_names = {}
        self.duchy_names = {}
        self.province_names = {}
        self.barony_names = {}


    def lookup_name(self, line, d, title_type):
        try:
            #print("ID")
            prov_id = re.match('\s*([_\-\w]+)', line).group()
            try:
                prov_id = prov_id.strip()
                #print("ID " + prov_id)
                name = d[prov_id]
                #print("Name " + name)
                #indent_string = ""
                #for i in range(indent):
                #    indent_string += "\t"
                self.last_name = name
                self.last_type = title_type

                #translations[name] = []

                #print(indent_string + name)
            except Exception:
                print("Could not find: " + prov_id)
        except AttributeError:
            print("Something wrong with: " + line)

    def load_province_names(self):
        province_dir = "../../history/provinces"

        local_files = [ f for f in listdir(province_dir) if isfile(join(province_dir,f)) ]

        for file_name in local_files:
            f = open(join(province_dir,file_name), "rb")
            for b in f:
                line = b.decode('latin-1', 'replace')

                if "title = " in line:
                    prov_title = line.split("=")[1].strip()

                    prov_name = file_name.split("-")[1].replace(".txt", "").strip()
                    #\print(prov_title + " : " + prov_name)
                    self.province_names[prov_title] = prov_name
                #print(line)


    def load_other_names(self):
        localisation_dir = "../../localisation/"

        local_files = [ f for f in listdir(localisation_dir) if isfile(join(localisation_dir,f)) ]



        for file_name in local_files:
            f = open(join(localisation_dir,file_name), "rb")
            for b in f:
                line = b.decode('latin-1', 'replace')
                #print(line)

                empire_match = re.match("^e_", line)
                kingdom_match = re.match("^k_", line)
                duchy_match = re.match("^d_", line)
                barony_match = re.match("^b_", line)

                names = line.split(";")

                if not empire_match is None:
                    self.empire_names[names[0]] = names[1]
                elif not kingdom_match is None:
                    self.kingdom_names[names[0]] = names[1]
                elif not duchy_match is None:
                    self.duchy_names[names[0]] = names[1]
                elif not barony_match is None:
                    self.barony_names[names[0]] = names[1]


    def find_translations(self):
        f = open("landed_titles.txt", "rb")

        lines_to_skip = ["title = ","title_female = ","foa = ",\
                         "title_prefix = ","religion = ","rebel = ", \
                         "pirate = ", "tribe = ","capital","short_name = ", \
                         "dynasty_title_names = ","caliphate = ", "landless = ", \
                         "primary", "culture = ", "mercenary = ", "independent = ", \
                         "mercenary_type = ", "strength_growth_per_century = ", "holy_site = ", \
                         "dignity = ", "always = ", "piety = ", "num_of_holy_sites = ", \
                         "is_republic = ", "character = ", "is_liege_or_above = ", "text = ",\
                         "trait = ", "has_holder = ", "is_heresy_of = ", "religion_group = ",\
                         "tier = ", "culture_group = ", "ai = ", "Crusade target weight", \
                         "color = ", "emblem = ", "texture_internal = ", "texture = ",\
                         "reformed", "template = ", "used_for_dynasty_names = ", "pentarchy = ", \
                         "prestige = ", "holy_order = ", "monthly_income = ", "year = ", \
                         "duchy_revokation = ", "purple_born_heirs = ", "muslim = ", "catholic = ",\
                         "orthodox = ", "assimilate = ", "in_revolt = ", "jewish_group = ", "set_global_flag = "]


        for b in f:

            line = b.decode('latin-1', 'replace')
            line = line.strip()

            if line in ["", "{", "}"] or line.startswith("#"):
                continue

            #print(line)

            empire_match = re.match("^e_", line)
            kingdom_match = re.match("^k_", line)
            duchy_match = re.match("^d_", line)
            county_match = re.match("^c_", line)
            barony_match = re.match("^b_", line)

            if not empire_match is None:
                self.lookup_name(line, self.empire_names, 'e')

            elif not kingdom_match is None:
                self.lookup_name(line, self.kingdom_names, 'k')

            elif not duchy_match is None:
                self.lookup_name(line, self.duchy_names, 'd')

            elif not county_match is None:
                self.lookup_name(line, self.province_names, 'c')

            elif not barony_match is None:
                self.lookup_name(line, self.barony_names, 'b')

            else:
                translation_match = re.match("\s*\w+\s=\s\w+", line)
                translation_match2 = re.match("\s*\w+\s=\s\"\w+\"", line)
                if translation_match is None and translation_match2 is None:
                    continue

                #print(line)

                skip_bool = False
                for skip in lines_to_skip:
                    if skip in line:
                        skip_bool = True
                        break

                if skip_bool:
                    continue

                #print(line)

                if self.last_type == 'e':
                    print(self.last_name + " : " + line)
                    self.e_translations[self.last_name].append(line)
                elif self.last_type == 'k':
                    self.k_translations[self.last_name].append(line)
                elif self.last_type == 'd':
                    self.d_translations[self.last_name].append(line)
                elif self.last_type == 'c':
                    self.c_translations[self.last_name].append(line)
                elif self.last_type == 'b':
                    self.b_translations[self.last_name].append(line)

    def print_translations(self, translations):
        for i in sorted(translations.keys()):
            print(i)
            unique_names = {}

            for t in translations[i]:
                s = t.split("=")
                lang = s[0].replace("_arabic", "").strip().capitalize()

                new_name = s[1].replace("\"", "").strip()

                if not new_name in unique_names:
                    unique_names[new_name] = lang
                else:
                    unique_names[new_name] += ", " + lang

            for un in unique_names.keys():
                print("\t" + un + ": " + unique_names[un])

if __name__ == "__main__":
    tp = TranslationPrinter()
    tp.load_province_names()
    tp.load_other_names()
    tp.find_translations()

    print("Empires:")
    tp.print_translations(tp.e_translations)

    print("\n\nKingdoms:")
    tp.print_translations(tp.k_translations)

    print("\n\nDuchies:")
    tp.print_translations(tp.d_translations)

    print("\n\nCounties:")
    tp.print_translations(tp.c_translations)

    print("\n\nBaronies:")
    tp.print_translations(tp.b_translations)