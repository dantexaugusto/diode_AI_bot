import time
import json

#reference_file = "diode_main_site_links.json" #path to file
#files_to_compare = ["diode_DOCS_about_sublinks.json", "diode_DOCS_app_sublinks.json", 
#                    "diode_DOCS_cli_sublinks.json", "diode_DOCS_network_sublinks.json",
#                    "diode_DOCS_vaults_sublinks.json"]

reference_file = "diode_DOCS_about_sublinks.json"

files_to_compare = ["diode_DOCS_app_sublinks.json", 
                    "diode_DOCS_network_sublinks.json", 
                    "diode_DOCS_vaults_sublinks.json",
                    "diode_DOCS_cli_sublinks.json"]


files_to_dicts = []

with open(reference_file, "r") as fileRef:
    dictRef = json.load(fileRef)
    reference_file_display = f"O arquivo referência de comparação é: {reference_file} \n \n"
    print(reference_file_display)
    with open("Repeated_link_seek_response.txt", "a") as file_response:
        file_response.write(reference_file_display) 
    reference_file = dictRef
    print(type(dictRef))

for i in files_to_compare:
    with open(i, "r") as jsonFile:
        files_to_dicts.append(json.load(jsonFile))

for i in reference_file:
    compare = reference_file[i]
    for x in files_to_dicts:
        json2write = files_to_compare[files_to_dicts.index(x)]
        print(f"type of json2write = {type(json2write)} \n \n")
        print(f"Variável json2write é {json2write} \n \n")
        clean_json_dest_n_name = "clean_jsons/"+"clean_"+json2write
        print(clean_json_dest_n_name, "\n \n" )

        new_cleanJson = {}
        new_cleanIndex = 0

        for y in x:
            if x[y] == compare:
                seek_response = f"Link repetido no arquivo: {files_to_compare[files_to_dicts.index(x)]}  => {x[y]} = {compare} Chave Json = {y} \n"
                print(seek_response)
                #with open("Repeated_link_seek_response.txt", "a") as file_response:
                    #file_response.write(seek_response) 

            elif x[y] != compare:
                new_cleanJson[new_cleanIndex] = str(x[y])
                print(new_cleanJson[new_cleanIndex])
                new_cleanIndex += 1

        with open(clean_json_dest_n_name, "w", encoding="utf-8") as cleanJson:
            json.dump(new_cleanJson, cleanJson, indent=4, ensure_ascii=False)

    
        

