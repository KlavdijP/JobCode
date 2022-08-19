from msilib.schema import Error
from numpy import NaN, empty
import pandas as pd
from csv import DictReader, reader
import csv
import re

#products = "./products_export_1.csv" #"./Shopify-Production-VN47_1-2.csv" 
products = "./Shopify-Production-VN47_1-2.csv"


path_sifr = {
    "brand": "./Sifranti/update_glasses.brand.csv",
    "type": "./Sifranti/update_glasses.type.csv",
    "shape": "./Sifranti/update_glasses.shape.csv",
    "frame_thickness": "./Sifranti/update_glasses.frame_thickness.csv",
    "pattern": "./Sifranti/update_glasses.pattern.csv",
    "material": "./Sifranti/update_glasses.material.csv",
    "color": "./Sifranti/update_glasses.color.csv",
}

sifr = {
    "brand" : set(),
    "type" : set(),
    "shape" : set(),
    "frame_thickness" : set(),
    "pattern" : set(),
    "material" : set(),
    "color" : set(),
}

array_ocal = list()
array_failed_ocal = list()


def getFromReader(fileName):
    return DictReader(open(fileName, 'rt', encoding='utf-8'))

def refreshSifr():
    for key, file in path_sifr.items():
        with open(file, 'r', encoding="utf-8") as read_obj:
            csv_reader = reader(read_obj)
            header = next(csv_reader)
            for row in csv_reader:
                sifr[key].add(row[0])# = sifr.get(key).union(row)

refreshSifr()

df = pd.read_csv(products, encoding='utf8')
grouped_handle = df.groupby("Handle")
gb = grouped_handle.groups

header = df.columns.tolist()
def get_indexOf(header_key):
    try:
        return header.index(header_key)
    except ValueError:
        return -1


#glasses uses the same pattern as update_glasses form
glasses = {
    "ean": "",
    "brand": "",
    "model": "",
    "variant": "",
    "gender": "",
    "quarter": "",
    "type": "",
    "description": "",
    "shape": "",
    "frame_thickness": "",
    "pattern": "",
    "pattern_2": "",
    "clip": "",
    "progression": "",
    "material": "",
    "material_2": "",
    "material_extra": "",
    "color": "",
    "color_2": "",
    "color_extra": "",
    "lens_color_type": "",
    "lens_color": "",
    "polarization": "",
    "dimension_L": "",
    "dimension_M": "",
    "dimension_R": "",
}

def getFromHTML(html, key):
    html = str(html)
    key = key.lower()
    key_to_label = {
        "barva":'Barva</span><b class="data">',
        "znamka":'Znamka</span><b class="data">',
        "model":'Model</span><b class="data">',
        "dodatna oznaka":'Dodatna oznaka</span><b class="data">',
        "varianta":'Dodatna oznaka</span><b class="data">',
        "oblika":'Oblika</span><b class="data">',
        "kolekcija":'Kolekcija</span><b class="data">',
        "spol":'Kolekcija</span><b class="data">',
        "velikost":'Velikost</span><b class="data">',
        "debelina":'Debelina</span><b class="data">',
        "clip":'Clip on</span><b class="data">',
        "progresiva":'Progresiva</span><b class="data">',
        "material":'Material</span><b class="data">',
        "barva_stekla":'<h3>Lastnosti stekel</h3>\n  <li><span class="label">Barva</span><b class="data">',
        "polarization":'Polarizacija</span><b class="data">',
        "vzorec":'Obdelava</span><b class="data">',
    }
    if key not in key_to_label.keys() or html.find(key_to_label[key]) < 0:
        return ""
    
    index = html.find(key_to_label[key]) + len(key_to_label[key])
    
    i = 0
    strr = ""
    while html[index+i] != "<":
        strr += str(html[index+i])
        i += 1
    return strr

def isInTags(key, tags):
    for v in tags:
        if v == key:
            return True
    return False
    return True if tags.intersection({key}) else False

def findSifrInTag(sifr_key, tags, exc={}):
    for v in sifr[sifr_key]:
        if v not in exc:
            if isInTags(v, tags):
                return v
    return ""
    
    for value in sifr[sifr_key].difference(exc):
        if isInTags(value, tags):
            return value
    return "" #"custom_error_NOT_IN_SIFRANTI_%s" % sifr_key

class Glasses:
    def __init__(self):
        self.ean= ""
        self.brand= ""
        self.model= ""
        self.variant= ""
        self.gender= ""
        self.quarter = ""
        self.type= ""
        self.description= ""
        self.shape= ""
        self.frame_thickness= ""
        self.pattern= ""
        self.pattern_2= ""
        self.clip= ""
        self.progression= ""
        self.material= ""
        self.material_2= ""
        self.material_extra= ""
        self.color= ""
        self.color_2= ""
        self.color_extra= ""
        self.lens_color_type= ""
        self.lens_color= ""
        self.polarization= ""
        self.dimension_L= ""
        self.dimension_M= ""
        self.dimension_R= ""

    def izpis(cls):
        return [value for name, value in vars(cls).items()]

for key, items in grouped_handle:
    i = 0
    for item in items.values:
        #print("PRVI: \n\n\n\n", item)
        item = [str(x) for x in item]
        #print("DRUGI: \n\n\n\n", item)
        ocala = Glasses()
        try:
            if item[get_indexOf("Handle")].split("-")[0] in {"okvirji", "soncna", "sončna"}:
                if i == 0:
                    ocala.ean = item[get_indexOf("Variant Barcode")].replace("'", "")
                    ocala.brand = item[get_indexOf("Vendor")]
                    if len({ocala.brand}.intersection(sifr["brand"])) == 0:
                        for brand in sifr["brand"]:
                            if str(brand).lower() == ocala.brand.lower():
                                ocala.brand = str(brand)
                                break
                    ocala.model = item[get_indexOf("Title")]
                    ocala.variant = getFromHTML(item[get_indexOf("Body (HTML)")], "varianta")
                    #GENDER PICKER
                    tags = [i for i in item[get_indexOf("Tags")].split(", ")]
                    if isInTags("ženska", tags):
                        if isInTags("moška", tags):
                            ocala.gender = "unisex"
                        else:
                            ocala.gender = "ženska"
                    elif isInTags("moška", tags):
                        ocala.gender = "moška"
                    else:
                        ocala.gender = "otroška"
                    #-----------
                    ocala.quarter = "Q3 2022"#re.findall(r'[Qq][1-4][ ][0-9]{4}', tags)[0]

                    if isInTags("sončna očala", tags):
                        ocala.type = "sončna očala"
                    elif isInTags("okvirji", tags):
                        ocala.type = "okvirji"
                    #ocala.description = ""
                    ocala.shape = findSifrInTag("shape", tags)
                    ocala.frame_thickness = findSifrInTag("frame_thickness", tags)

                    if getFromHTML(item[get_indexOf("Body (HTML)")], "vzorec") != "":
                        pattern = getFromHTML(item[get_indexOf("Body (HTML)")], "vzorec")
                        if len(pattern.split(",")) > 1:
                            ocala.pattern = pattern.split(",")[0].strip()
                            ocala.pattern_2 = pattern.split(",")[1].strip()
                        else:
                            ocala.pattern = pattern
                    else:
                        ocala.pattern = findSifrInTag("pattern", tags)
                        ocala.pattern_2 = findSifrInTag("pattern", tags, {ocala.pattern})
                    ocala.clip = "1" if isInTags("clip", tags) else "0"
                    ocala.progression= "1" if isInTags("progresiv", tags) else "0"
                    ocala.material = findSifrInTag("material", tags)
                    if ocala.material == "":
                        ocala.material["material"] = getFromHTML(item[get_indexOf("Body (HTML)")], "material")
                    if getFromHTML(item[get_indexOf("Body (HTML)")], "barva") != "":
                        barva = getFromHTML(item[get_indexOf("Body (HTML)")], "barva").replace("-", " ")
                        if len(barva.split(",")) > 1:
                            ocala.color = barva.split(",")[0].strip()
                            ocala.color_2 = barva.split(",")[1].strip()
                        else:
                            ocala.color = barva
                    else:
                        ocala.color = findSifrInTag("color", tags).replace("-"," ")
                        ocala.color_2 = findSifrInTag("color", tags, {ocala.color}).replace("-"," ")
                    for v in tags:
                        if v.find("gls-") != -1:
                            ocala.lens_color = v.replace("gls-", "").replace("-", " ")
                    if getFromHTML(item[get_indexOf("Body (HTML)")], "barva_stekla") != "":
                        barva_stekla =  getFromHTML(item[get_indexOf("Body (HTML)")], "barva_stekla")
                        if barva_stekla.find(", ") != -1:
                            ocala.lens_color_type = barva_stekla.split(",")[1].strip()
                    ocala.polarization = "1" if isInTags("polarizirana", tags) else "0"
                    dimensions = getFromHTML(item[get_indexOf("Body (HTML)")], "velikost")
                    ocala.dimension_L, ocala.dimension_M, ocala.dimension_R = dimensions.split(" ")[1].strip("()").split("-")
                    array_ocal.append(ocala.izpis())
                    i += 1
        except:
            array_failed_ocal.append(item)
        #reset glasses  value
        """
        glasses = {
            "ean": "",
            "brand": "",
            "model": "",
            "variant": "",
            "gender": "",
            "type": "",
            "description": "",
            "shape": "",
            "frame_thickness": "",
            "pattern": "",
            "pattern_2": "",
            "clip": "",
            "progression": "",
            "material": "",
            "material_2": "",
            "material_extra": "",
            "color": "",
            "color_2": "",
            "color_extra": "",
            "lens_color_type": "",
            "lens_color": "",
            "polarization": "",
            "dimension_L": "",
            "dimension_M": "",
            "dimension_R": "",
        }
        

    
        if(str(item[0]).split("-")[0] in {"okvirji", "soncna", "sončna"}):
            #print(item[0])
            if i == 0 and item[25] == 1.0:
                glasses["ean"] = str(item[23])[1:]
                if glasses["ean"] == "an":
                    print(item)
                glasses["brand"] = str(item[3])
                if len({glasses["brand"]}.intersection(sifr["brand"])) == 0:
                    for brand in sifr["brand"]:
                        if str(brand).lower() == glasses["brand"].lower():
                            glasses["brand"] = str(brand)
                            break
                glasses["model"] = str(item[1])
                glasses["variant"] = getFromHTML(item[2], "dodatna oznaka")
                glasses["gender"] = getFromHTML(item[2], "spol").lower()
                if glasses.get("gender").find(",") != -1:# == "ženska, moška"):
                    glasses["gender"] = "unisex"
                elif glasses.get("gender").find("m") != -1:
                    glasses["gender"] = "moška"
                elif glasses.get("gender").find("ž") != -1:
                    glasses["gender"] = "ženska"
                else:
                    glasses["gender"] = "otroška"
                glasses["type"] = item[5]
                glasses["description"] = "" ## DONT KNOW WHAT COLUMN IT IS
                glasses["shape"] = getFromHTML(item[2], "oblika")
                glasses["frame_thickness"] = getFromHTML(item[2], "debelina")
                glasses["pattern"] = getFromHTML(item[2], "vzorec")
                if glasses["pattern"].find(", ") != -1:
                    glasses["pattern_2"] = glasses["pattern"].split(", ")[1]
                    if len({glasses["pattern_2"]}.intersection(sifr["pattern"])) == 0:
                        glasses["pattern_2"] = ""
                    glasses["pattern"] = glasses["pattern"].split(", ")[0]
                glasses["clip"] = "1" if getFromHTML(item[2], "clip") == "da" else "0"
                glasses["progression"] = "1" if getFromHTML(item[2], "progresiva") == "da" else "0"
                glasses["material"] = getFromHTML(item[2], "material")
                if glasses["material"].find(" jeklo") != -1:# and glasses["material"] != "nerjaveče jeklo":
                    glasses["material"] = "nerjaveče jeklo"
                glasses["color"] = str(item[9]).replace("-", " ")
                if glasses["color"].find("matt") != -1:
                    glasses["color"] = glasses["color"].replace("matt ", "")
                    if glasses["pattern"] == "mat":
                        glasses["pattern"] = "mat"
                    elif glasses["pattern_2"] == "":
                        if glasses["pattern"] == "":
                            glasses["pattern"] = "mat"
                        else:
                            glasses["pattern_2"] = "mat"
                glasses["lens_color"] = getFromHTML(item[2], "barva_stekla")
                if glasses.get("lens_color").find(", ") != -1:
                    glasses["lens_color_type"] = glasses.get("lens_color").split(", ")[1]
                    glasses["lens_color"] = glasses.get("lens_color").split(", ")[0].replace("-", " ")
                glasses["polarization"] = "1" if getFromHTML(item[2], "polarization") == "da" else "0"
                #print("asdasdasd", glasses.get("ean"), getFromHTML(item[2], "velikost"))
                dimensions = getFromHTML(item[2], "velikost")
                if dimensions != "":
                    glasses["dimension_L"], glasses["dimension_M"], glasses["dimension_R"] = dimensions.split(" ")[1].strip("()").split("-")
                # TODO
                # Image source and position array
                #print([v for c,v in glasses.items()])
                array_ocal.append([v for c,v in glasses.items()])
                i += 1
            elif item[2] is not NaN:
                array_failed_ocal.append(item)
        else:
            array_failed_ocal.append(item)
        """


with open("Completed_%s.csv" % products.split(".")[1].strip("/"), "w", encoding='utf-8', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(glasses.keys())
    csvwriter.writerows(array_ocal)
with open("Failed_%s.csv" % products.split(".")[1].strip("/"), "w", encoding='utf-8', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(header)
    csvwriter.writerows(array_failed_ocal)