##
##  Program to identify and fix missing and duplicated road IDs within a QGIS vector layer
##
##  Author: Emmanuel Boisseau for Khmer Water Supply Holding Co.Ltd. (KWSH)
##
##  Version 1.0 - This program does not work for multiple missing or duplicate routes on the same higher order route and on the same side of the route. (example: NR3-001 and NR3-003 or NR3-005-01 and NR3-005-07)
##

##  Import modules
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from math import *
import pprint

##  Initialization of variables
# ⚠️ Write below the exact file paths to the road IDs layers as 'fn' string variable
fn_main_road = "C:/Users/etudiant/Desktop/Work/ENSE3/Stage 2A/SIG/ID Map/Layers/Roads/Roads_ID.shp"
fn_roads1 = "C:/Users/etudiant/Desktop/Work/ENSE3/Stage 2A/SIG/ID Map/Layers/Roads/Branch Roads 1.shp"
fn_roads2 = "C:/Users/etudiant/Desktop/Work/ENSE3/Stage 2A/SIG/ID Map/Layers/Roads/Branch Roads 2.shp"
fn_roads3 = "C:/Users/etudiant/Desktop/Work/ENSE3/Stage 2A/SIG/ID Map/Layers/Roads/Branch Roads 3.shp"
fn_roads4 = "C:/Users/etudiant/Desktop/Work/ENSE3/Stage 2A/SIG/ID Map/Layers/Roads/Branch Roads 4.shp"
# ⚠️ Write below the exact file path to the Customers IDs layer as 'fn' string variable
fn_hhs = "file:///C:/Users/etudiant/Desktop/Work/ENSE3/Stage 2A/SIG/ID Map/Layers/Households/Household IDs.shp"

layer_main_road = QgsVectorLayer(fn_main_road, "Main Road", "ogr")
layer_roads1 = QgsVectorLayer(fn_roads1, "Branch Roads 1", "ogr")
layer_roads2 = QgsVectorLayer(fn_roads2, "Branch Roads 2", "ogr")
layer_roads3 = QgsVectorLayer(fn_roads3, "Branch Roads 3", "ogr")
layer_roads4 = QgsVectorLayer(fn_roads4, "Branch Roads 4", "ogr")
layer_hhs = QgsVectorLayer(fn_hhs, "Household IDs", "ogr")

layers = [layer_main_road, layer_roads1, layer_roads2, layer_roads3, layer_roads4, layer_hhs]

caps0 = layer_main_road.dataProvider().capabilities()
caps1 = layer_roads1.dataProvider().capabilities()
caps2 = layer_roads2.dataProvider().capabilities()
caps3 = layer_roads3.dataProvider().capabilities()
caps4 = layer_roads4.dataProvider().capabilities()
capshhs = layer_hhs.dataProvider().capabilities()

#️ Lists for all the attributes of all the features within the road layers
tab_attr_main_road, tab_attr_roads1, tab_attr_roads2, tab_attr_roads3, tab_attr_roads4 = [], [], [], [], []

tab_attr_hhs = []

roads_with_hhs = []

check_hhs, check_roads, check_digits_roads = 0, 0, 0

#️ Lists of missing road IDs and duplicated road IDs as string variables
duplicated_ids, missing_ids = [], []

#️ Corrected list for missing features and duplicated features
tab_attr_missing_corrected1, tab_attr_missing_corrected2, tab_attr_missing_corrected3, tab_attr_missing_corrected4 = [], [], [], []
tab_attr_missing_corrected2_2, tab_attr_missing_corrected3_2, tab_attr_missing_corrected4_2 = [], [], []
tab_attr_missing_corrected3_3, tab_attr_missing_corrected4_3 = [], []
tab_attr_missing_corrected4_4 = []
tab_attr_duplicated_corrected1, tab_attr_duplicated_corrected2, tab_attr_duplicated_corrected3, tab_attr_duplicated_corrected4 = [], [], [], []
tab_attr_duplicated_corrected2_2, tab_attr_duplicated_corrected3_2, tab_attr_duplicated_corrected4_2 = [], [], []
tab_attr_duplicated_corrected3_3, tab_attr_duplicated_corrected4_3 = [], []
tab_attr_duplicated_corrected4_4 = []

ids_roads1_with_hhs_corrected, ids_roads2_with_hhs_corrected, ids_roads3_with_hhs_corrected, ids_roads4_with_hhs_corrected = [], [], [], []
tab_attr_hhs_corrected  = []

##  Creation of several relevant functions
#️ Function that converts an integer to a string with a chosen number of digits (from 1 to 3)
def digits(int_nbr, nbr_digits):
    if int_nbr < 10:
        return ('0'*(nbr_digits - 1) + str(int_nbr))
    elif int_nbr >= 10 and int_nbr < 100:
        return ('0'*(nbr_digits - 2) + str(int_nbr))
    else:
        return str(int_nbr)

#️ Function that displays a chosen input message to the user with a Yes or No choice
def input_message_yes_no(window_title, main_text):
    return QMessageBox.question(iface.mainWindow(), window_title, main_text, QMessageBox.Yes, QMessageBox.No)

#️ Function that displays a chosen message with a chosen icon to the user
def show_popup_message(window_title, main_text, icon):
    msg = QMessageBox()
    msg.setWindowTitle(window_title)
    msg.setText(main_text)
    if icon == "information":
        msg.setIcon(QMessageBox.Information)
    if icon == "error":
        msg.setIcon(QMessageBox.Critical)
    return msg.exec_()

def has_even(lst):
    for v in lst:
        if v % 2 == 0:
            return True
    return False

def has_odd(lst):
    for v in lst:
        if v % 2 == 1:
            return True
    return False

def maxeven(list):
    return sorted([x for x in list if x % 2 == 0])[-1]
    
def maxodd(list):
    return sorted([x for x in list if x % 2 != 0])[-1]

def duplicated(elem, lst):
    counter = 0
    duplicated_no = []
    seen = set()
    for ele in lst:
        if ele in seen:
            duplicated_no.append(ele)
        else:
            seen.add(ele)
        counter += 1
    if elem in duplicated_no:
        return True
    else:
        return False
        
def check_digits(elem, digits):
    if len(elem) != digits:
        return False
    else:
        return True

##  Filling of the feature attributes and roads lists
#️ Number of features within the layers
fc0 = layer_main_road.featureCount()
fc1 = layer_roads1.featureCount()
fc2 = layer_roads2.featureCount()
fc3 = layer_roads3.featureCount()
fc4 = layer_roads4.featureCount()
fc_hhs = layer_hhs.featureCount()

#️ Loops that adds all the relevant feature attributes to a list of tuples
for i in range(0, fc0):
    feat = layer_main_road.getFeature(i)
    tab_attr_main_road.append((feat['Main Road'], feat.id()))

if len(tab_attr_main_road) != 0:
    main_road = tab_attr_main_road[0][0]
    
for i in range(0, fc1):
    feat = layer_roads1.getFeature(i)
    tab_attr_roads1.append((feat['Main Road'], feat['Branch 1'], feat.id()))

for i in range(0, fc2):
    feat = layer_roads2.getFeature(i)
    tab_attr_roads2.append((feat['Main Road'], feat['Branch 1'], feat['Branch 2'], feat.id()))

for i in range(0, fc3):
    feat = layer_roads3.getFeature(i)
    tab_attr_roads3.append((feat['Main Road'], feat['Branch 1'], feat['Branch 2'], feat['Branch 3'], feat.id()))

for i in range(0, fc4):
    feat = layer_roads4.getFeature(i)
    tab_attr_roads4.append((feat['Main Road'], feat['Branch 1'], feat['Branch 2'], feat['Branch 3'], feat['Branch 4'], feat.id()))

for i in range(0, fc_hhs):
    feat = layer_hhs.getFeature(i)
    tab_attr_hhs.append((feat['Road ID'], feat['Direction'], feat['Side Order'], feat['St Frtg No'], feat['Fam. Name'], feat['No. of Ppl'], feat['Avg Cons'], feat['Start Date'], feat['Connection'], feat['Factory'], feat['Province'], feat['District'], feat['Commune'], feat.id()))


lst_wrong_roads = []

ctr = 0
lst_index_wrong_main_road = []
res_main_road = []
for elem in tab_attr_main_road:
    if elem[0] != NULL:
        if check_digits(elem[0], 3) == False:
            lst_index_wrong_main_road.append(ctr)
    else:
        lst_index_wrong_main_road.append(ctr)
    ctr += 1
    
[res_main_road.append(x) for x in lst_index_wrong_main_road if x not in res_main_road]
for i in res_main_road:
    lst_wrong_roads.append(tab_attr_main_road[i][0])

ctr = 0
lst_index_wrong_roads1 = []
res_roads1 = []
for elem in tab_attr_roads1:
    if elem[0] != NULL and elem[1] != NULL:
        if check_digits(elem[0], 3) == False or check_digits(elem[1], 3) == False:
            lst_index_wrong_roads1.append(ctr)
    else:
        lst_index_wrong_roads1.append(ctr)
    ctr += 1
    
[res_roads1.append(x) for x in lst_index_wrong_roads1 if x not in res_roads1]
for i in res_roads1:
    lst_wrong_roads.append(tab_attr_roads1[i][:-1])

ctr = 0
lst_index_wrong_roads2 = []
res_roads2 = []
for elem in tab_attr_roads2:
    if elem[0] != NULL and elem[1] != NULL and elem[2] != NULL:
        if check_digits(elem[0], 3) == False or check_digits(elem[1], 3) == False or check_digits(elem[2], 2) == False:
            lst_index_wrong_roads2.append(ctr)
    else:
        lst_index_wrong_roads2.append(ctr)
    ctr += 1
    
[res_roads2.append(x) for x in lst_index_wrong_roads2 if x not in res_roads2]
for i in res_roads2:
    lst_wrong_roads.append(tab_attr_roads2[i][:-1])

ctr = 0
lst_index_wrong_roads3 = []
res_roads3 = []
for elem in tab_attr_roads3:
    if elem[0] != NULL and elem[1] != NULL and elem[2] != NULL and elem[3] != NULL:
        if check_digits(elem[0], 3) == False or check_digits(elem[1], 3) == False or check_digits(elem[2], 2) == False or check_digits(elem[3], 2) == False:
            lst_index_wrong_roads3.append(ctr)
    else:
        lst_index_wrong_roads3.append(ctr)
    ctr += 1
    
[res_roads3.append(x) for x in lst_index_wrong_roads3 if x not in res_roads3]
for i in res_roads3:
    lst_wrong_roads.append(tab_attr_roads3[i][:-1])

ctr = 0
lst_index_wrong_roads4 = []
res_roads4 = []
for elem in tab_attr_roads4:
    if elem[0] != NULL and elem[1] != NULL and elem[2] != NULL and elem[3] != NULL and elem[4] != NULL:
        if check_digits(elem[0], 3) == False or check_digits(elem[1], 3) == False or check_digits(elem[2], 2) == False or check_digits(elem[3], 2) == False or check_digits(elem[4], 2) == False:
            lst_index_wrong_roads4.append(ctr)
    else:
        lst_index_wrong_roads4.append(ctr)
    ctr += 1
    
[res_roads4.append(x) for x in lst_index_wrong_roads4 if x not in res_roads4]
for i in res_roads4:
    lst_wrong_roads.append(tab_attr_roads4[i][:-1])

lst_wrong_roads_fixed = []
for i in range(len(lst_wrong_roads)):
    lst_wrong_roads_fixed.append('-'.join(filter(None, lst_wrong_roads[i])))

if len(lst_wrong_roads_fixed) == 0:
    print("All road IDs are written with the correct number of digits.\n")
    check_digits_roads = 1
else:
    print("There is a problem with the number of digits regarding the following roads:")
    print("\t", *sorted(lst_wrong_roads_fixed, key=len), sep = "\n\t. ")
    print("\nReminder: Road IDs should be entered as follows:")
    print("\t-3 digits for the main road\n\t-3 digits for branch roads 1\n\t-2 digits for branch roads 2, 3 and 4")
    print("e.g: NR3-065 ; NR3-075-01 ; NR3-002-04-03 ; NR3-002-01-04-05")
    print("\nPlease correct the road IDs previously indicated and then rerun the program to determine the potential missing and duplicate road IDs.")
    show_popup_message("Error", "There is a problem with the number of digits regarding the following roads:\n\t. " + '\n\t. '.join('{}'.format(item) for item in lst_wrong_roads_fixed) + "\n\n\n\n\nReminder: Road IDs should be entered as follows:"+ "\n\t-3 digits for the main road\n\t-3 digits for branch roads 1\n\t-2 digits for branch roads 2, 3 and 4" + "\n\ne.g: NR3-065 ; NR3-075-01 ; NR3-002-04-03 ; NR3-002-01-04-05" + "\n\nPlease correct the road IDs previously indicated and then rerun the program to determine the potential missing and duplicate road IDs." , "error")
    check_digits_roads = 2
    

if check_digits_roads == 1:
    #️ Loop that adds all the road IDs to a list without duplicated values
    for i in tab_attr_hhs:
        if roads_with_hhs.count(i[0]) == 0:
            roads_with_hhs.append(i[0])
            
            
    main_road_with_hhs, roads1_with_hhs, roads2_with_hhs, roads3_with_hhs, roads4_with_hhs = [], [], [], [], []
    ids_main_road_with_hhs, ids_roads1_with_hhs, ids_roads2_with_hhs, ids_roads3_with_hhs, ids_roads4_with_hhs = [], [], [], [], []

    main_road_with_hhs = [ele for ele in roads_with_hhs if len(ele.split("-")) == 1]
    roads1_with_hhs = [ele for ele in roads_with_hhs if len(ele.split("-")) == 2]
    roads2_with_hhs = [ele for ele in roads_with_hhs if len(ele.split("-")) == 3]
    roads3_with_hhs = [ele for ele in roads_with_hhs if len(ele.split("-")) == 4]
    roads4_with_hhs = [ele for ele in roads_with_hhs if len(ele.split("-")) == 5]

    for i in tab_attr_main_road:
        if str('-'.join(i[:-1])) in main_road_with_hhs:
            ids_main_road_with_hhs.append(('-'.join(i[:-1]), i[-1]))
            
    main_road_with_hhs.sort(key=lambda x: x[1])

    for i in [elem[0] for elem in main_road_with_hhs]:
        if any([elem[0] for elem in main_road_with_hhs].count(i) == 2 for i in [elem[0] for elem in main_road_with_hhs]) == True:
            del main_road_with_hhs[-1]

    for i in tab_attr_roads1:
        if str('-'.join(i[:-1])) in roads1_with_hhs:
            ids_roads1_with_hhs.append(('-'.join(i[:-1]), i[-1]))

    ids_roads1_with_hhs.sort(key=lambda x: x[1])
            
    for i in [elem[0] for elem in ids_roads1_with_hhs]:
        if any([elem[0] for elem in ids_roads1_with_hhs].count(i) == 2 for i in [elem[0] for elem in ids_roads1_with_hhs]) == True:
            del ids_roads1_with_hhs[-1]

    for i in tab_attr_roads2:
        if str('-'.join(i[:-1])) in roads2_with_hhs:
            ids_roads2_with_hhs.append(('-'.join(i[:-1]), i[-1]))
            
    ids_roads2_with_hhs.sort(key=lambda x: x[1])

    for i in [elem[0] for elem in ids_roads2_with_hhs]:
        if any([elem[0] for elem in ids_roads2_with_hhs].count(i) == 2 for i in [elem[0] for elem in ids_roads2_with_hhs]) == True:
            del ids_roads2_with_hhs[-1]

    for i in tab_attr_roads3:
        if str('-'.join(i[:-1])) in roads3_with_hhs:
            ids_roads3_with_hhs.append(('-'.join(i[:-1]), i[-1]))
            
    ids_roads3_with_hhs.sort(key=lambda x: x[1])

    for i in [elem[0] for elem in ids_roads3_with_hhs]:
        if any([elem[0] for elem in ids_roads3_with_hhs].count(i) == 2 for i in [elem[0] for elem in ids_roads3_with_hhs]) == True:
            del ids_roads3_with_hhs[-1]

    for i in tab_attr_roads4:
        if str('-'.join(i[:-1])) in roads4_with_hhs:
            ids_roads4_with_hhs.append(('-'.join(i[:-1]), i[-1]))
            
    ids_roads4_with_hhs.sort(key=lambda x: x[1])
            
    for i in [elem[0] for elem in ids_roads4_with_hhs]:
        if any([elem[0] for elem in ids_roads4_with_hhs].count(i) == 2 for i in [elem[0] for elem in ids_roads4_with_hhs]) == True:
            del ids_roads4_with_hhs[-1]

    if len(ids_main_road_with_hhs) != len(main_road_with_hhs) or len(ids_roads1_with_hhs) != len(roads1_with_hhs) or len(ids_roads2_with_hhs) != len(roads2_with_hhs) or len(ids_roads3_with_hhs) != len(roads3_with_hhs) or len(ids_roads4_with_hhs) != len(roads4_with_hhs):
        print("One of the households has a road attribute that does not exist on the road layers\nMake sure that you use the correct number of digits for each type of road\n\nIf you have deleted a road before running this program, make sure that the corresponding households have also been deleted.\n")
        show_popup_message("Warning", "One of the households has a road attribute that does not exist on the road layers\nMake sure that you use the correct number of digits for each type of road\n\nIf you have deleted a road before running this program, make sure that the corresponding households have also been deleted.", "error")
        check_hhs = 1
    else:
        check_hhs = 2

    ##  Identification and change of road IDs with a value greater than the missing ID if a missing ID exists
    #️ Loop that fills a list with the corrected ID for roads with an ID greater than the missing one
    #️ Lists containing the missing IDs for a given road for both left and right sides
    missing_left_1, missing_right_1 = [], []
    duplicated_left_1, duplicated_right_1 = [], []

    if has_odd([int(ele[1]) for ele in tab_attr_roads1]) == True:
        missing_left_1 = [ele for ele in range(1, maxodd([int(ele[1]) for ele in tab_attr_roads1]) + 1) if ele not in ([int(ele[1]) for ele in tab_attr_roads1]) and ele%2 != 0]
        duplicated_left_1 = [ele for ele in range(1, maxodd([int(ele[1]) for ele in tab_attr_roads1]) + 1) if duplicated(ele, [int(ele[1]) for ele in tab_attr_roads1]) == True and ele%2 != 0]
    if has_even([int(ele[1]) for ele in tab_attr_roads1]) == True:
        missing_right_1 = [ele for ele in range(1, maxeven([int(ele[1]) for ele in tab_attr_roads1]) + 1) if ele not in ([int(ele[1]) for ele in tab_attr_roads1]) and ele%2 == 0]
        duplicated_right_1 = [ele for ele in range(1, maxeven([int(ele[1]) for ele in tab_attr_roads1]) + 1) if duplicated(ele, [int(ele[1]) for ele in tab_attr_roads1]) == True and ele%2 == 0]
        
    if len(missing_left_1) != 0 or len(missing_right_1) != 0 or len(duplicated_left_1) != 0 or len(duplicated_right_1) != 0:
        for i in missing_left_1:
            missing_ids.append(main_road + "-" + digits(i, 3))
        for i in missing_right_1:
            missing_ids.append(main_road + "-" + digits(i, 3))
        for i in duplicated_left_1:
            duplicated_ids.append(main_road + "-" + digits(i, 3))
        for i in duplicated_right_1:
            duplicated_ids.append(main_road + "-" + digits(i, 3))
            
    for i in [int(ele[1]) for ele in tab_attr_roads1]:
        local_lst_2 = []
        missing_left_2 = []
        missing_right_2 = []
        duplicated_left_2 = []
        duplicated_right_2 = []
        for elem in tab_attr_roads2:
            if int(elem[1]) == i:
                local_lst_2.append(int(elem[2]))
        if len(local_lst_2)>0:
            if has_odd(local_lst_2) == True:
                missing_left_2 = [ele for ele in range(1, maxodd(local_lst_2) + 1) if ele not in (local_lst_2) and ele%2 != 0]
                duplicated_left_2 = [ele for ele in range(1, maxodd(local_lst_2) + 1) if duplicated(ele, local_lst_2) == True and ele%2 != 0]
                for w in missing_left_2:
                    missing_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(w, 2))
                for x in duplicated_left_2:
                    duplicated_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(x, 2))
            if has_even(local_lst_2) == True:
                missing_right_2 = [ele for ele in range(1, maxeven(local_lst_2) + 1) if ele not in (local_lst_2) and ele%2 == 0]
                duplicated_right_2 = [ele for ele in range(1, maxeven(local_lst_2) + 1) if duplicated(ele, local_lst_2) == True and ele%2 == 0]
                for u in missing_right_2:
                    missing_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(u, 2))
                for y in duplicated_right_2:
                    duplicated_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(y, 2))
                    
        for j in local_lst_2:
            local_lst_3 = []
            missing_left_3 = []
            missing_right_3 = []
            duplicated_left_3 = []
            duplicated_right_3 = []
            for elem in tab_attr_roads3:
                if int(elem[1]) == i and int(elem[2]) == j:
                    local_lst_3.append(int(elem[3]))

            if len(local_lst_3)>0:
                if has_odd(local_lst_3) == True:
                    missing_left_3 = [ele for ele in range(1, maxodd(local_lst_3) + 1) if ele not in (local_lst_3) and ele%2 != 0]
                    duplicated_left_3 = [ele for ele in range(1, maxodd(local_lst_3) + 1) if duplicated(ele, local_lst_3) == True and ele%2 != 0]
                    for w in missing_left_3:
                        missing_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(j, 2) + "-" + digits(w, 2))
                    for x in duplicated_left_3:
                        duplicated_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(j, 2) + "-" + digits(x, 2))
                if has_even(local_lst_3) == True:
                    missing_right_3 = [ele for ele in range(1, maxeven(local_lst_3) + 1) if ele not in (local_lst_3) and ele%2 == 0]
                    duplicated_right_3 = [ele for ele in range(1, maxeven(local_lst_3) + 1) if duplicated(ele, local_lst_3) == True and ele%2 == 0]
                    for u in missing_right_3:
                        missing_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(j, 2) + "-" + digits(u, 2))
                    for y in duplicated_right_3:
                        duplicated_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(j, 2) + "-" + digits(y, 2))
                        
            for k in local_lst_3:
                local_lst_4 = []
                missing_left_4 = []
                missing_right_4 = []
                duplicated_left_4 = []
                duplicated_right_4 = []
                for elem in tab_attr_roads4:
                    if int(elem[1]) == i and int(elem[2]) == j and int(elem[3]) == k:
                        local_lst_4.append(int(elem[4]))

                if len(local_lst_4)>0:
                    if has_odd(local_lst_4) == True:
                        missing_left_4 = [ele for ele in range(1, maxodd(local_lst_4) + 1) if ele not in (local_lst_4) and ele%2 != 0]
                        duplicated_left_4 = [ele for ele in range(1, maxodd(local_lst_4) + 1) if duplicated(ele, local_lst_4) == True and ele%2 != 0]
                        for w in missing_left_4:
                            missing_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(j, 2) + "-" + digits(k, 2) + "-" + digits(w, 2))
                        for x in duplicated_left_4:
                            duplicated_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(j, 2) + "-" + digits(k, 2) + "-" + digits(x, 2))
                    if has_even(local_lst_4) == True:
                        missing_right_4 = [ele for ele in range(1, maxeven(local_lst_4) + 1) if ele not in (local_lst_4) and ele%2 == 0]
                        duplicated_right_4 = [ele for ele in range(1, maxeven(local_lst_4) + 1) if duplicated(ele, local_lst_4) == True and ele%2 == 0]
                        for u in missing_right_4:
                            missing_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(j, 2) + "-" + digits(k, 2) + "-" + digits(u, 2))
                        for y in duplicated_right_4:
                            duplicated_ids.append(main_road + "-" + digits(i, 3) + "-" + digits(j, 2) + "-" + digits(k, 2) + "-" + digits(y, 2))
                        
        

    if len(missing_left_1) != 0:
        for i in missing_left_1:
            for elem in tab_attr_roads1:
                if int(elem[1])%2 != 0 and int(elem[1]) > i:
                    tab_attr_missing_corrected1.append((elem[0], digits(int(elem[1]) - 2, 3), elem[-1]))
            for elem in tab_attr_roads2:
                if int(elem[1])%2 != 0 and int(elem[1]) > i:
                    tab_attr_missing_corrected2.append((elem[0], digits(int(elem[1]) - 2, 3), elem[2], elem[-1]))
            for elem in tab_attr_roads3:
                if int(elem[1])%2 != 0 and int(elem[1]) > i:
                    tab_attr_missing_corrected3.append((elem[0], digits(int(elem[1]) - 2, 3), elem[2], elem[3], elem[-1]))
            for elem in tab_attr_roads4:
                if int(elem[1])%2 != 0 and int(elem[1]) > i:
                    tab_attr_missing_corrected4.append((elem[0], digits(int(elem[1]) - 2, 3), elem[2], elem[3], elem[4], elem[-1]))
         
    if len(missing_right_1) != 0:
        for i in missing_right_1:
            for elem in tab_attr_roads1:
                if int(elem[1])%2 == 0 and int(elem[1]) > i:
                    tab_attr_missing_corrected1.append((elem[0], digits(int(elem[1]) - 2, 3), elem[-1]))
            for elem in tab_attr_roads2:
                if int(elem[1])%2 == 0 and int(elem[1]) > i:
                    tab_attr_missing_corrected2.append((elem[0], digits(int(elem[1]) - 2, 3), elem[2], elem[-1]))
            for elem in tab_attr_roads3:
                if int(elem[1])%2 == 0 and int(elem[1]) > i:
                    tab_attr_missing_corrected3.append((elem[0], digits(int(elem[1]) - 2, 3), elem[2], elem[3], elem[-1]))
            for elem in tab_attr_roads4:
                if int(elem[1])%2 == 0 and int(elem[1]) > i:
                    tab_attr_missing_corrected4.append((elem[0], digits(int(elem[1]) - 2, 3), elem[2], elem[3], elem[4], elem[-1]))


    ###########################################################################################################


    #️ Loop that adds all the household IDs that have a different feature number and that have not been previously changed to the corrected list
    counter = 0
    for elem in (x[-1:] for x in tab_attr_roads1):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected1):
            tab_attr_missing_corrected1.append(tab_attr_roads1[counter])
        counter += 1

    counter = 0
    for elem in (x[-1:] for x in tab_attr_roads2):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected2):
            tab_attr_missing_corrected2.append(tab_attr_roads2[counter])
        counter += 1
        
    counter = 0
    for elem in (x[-1:] for x in tab_attr_roads3):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected3):
            tab_attr_missing_corrected3.append(tab_attr_roads3[counter])
        counter += 1
        
    counter = 0
    for elem in (x[-1:] for x in tab_attr_roads4):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected4):
            tab_attr_missing_corrected4.append(tab_attr_roads4[counter])
        counter += 1
                 

    ###########################################################################################################
     
            
    for i in [int(ele[1]) for ele in tab_attr_missing_corrected1]:
        local_lst_2 = []
        missing_left_2 = []
        missing_right_2 = []
        for elem in tab_attr_missing_corrected2:
            if int(elem[1]) == i:
                local_lst_2.append(int(elem[2]))

        if len(local_lst_2)>0:
            if has_odd(local_lst_2) == True:
                missing_left_2 = [ele for ele in range(1, maxodd(local_lst_2) + 1) if ele not in (local_lst_2) and ele%2 != 0]
                
            if has_even(local_lst_2) == True:
                missing_right_2 = [ele for ele in range(1, maxeven(local_lst_2) + 1) if ele not in (local_lst_2) and ele%2 == 0]
        
        if len(missing_left_2) != 0:
            for a in missing_left_2:
                for elem in tab_attr_missing_corrected2:
                    if int(elem[2])%2 != 0 and int(elem[2]) > a and int(elem[1]) == i:
                        tab_attr_missing_corrected2_2.append((elem[0], elem[1], digits(int(elem[2]) - 2, 2), elem[-1]))
                for elem in tab_attr_missing_corrected3:
                    if int(elem[2])%2 != 0 and int(elem[2]) > a and int(elem[1]) == i:
                        tab_attr_missing_corrected3_2.append((elem[0], elem[1], digits(int(elem[2]) - 2, 2), elem[3], elem[-1]))
                for elem in tab_attr_missing_corrected4:
                    if int(elem[2])%2 != 0 and int(elem[2]) > a and int(elem[1]) == i:
                        tab_attr_missing_corrected4_2.append((elem[0], elem[1], digits(int(elem[2]) - 2, 2), elem[3], elem[4], elem[-1]))
             
        if len(missing_right_2) != 0:
            for b in missing_right_2:
                for elem in tab_attr_missing_corrected2:
                    if int(elem[2])%2 == 0 and int(elem[2]) > b and int(elem[1]) == i:
                        tab_attr_missing_corrected2_2.append((elem[0], elem[1], digits(int(elem[2]) - 2, 2), elem[-1]))
                for elem in tab_attr_missing_corrected3:
                    if int(elem[2])%2 == 0 and int(elem[2]) > b and int(elem[1]) == i:
                        tab_attr_missing_corrected3_2.append((elem[0], elem[1], digits(int(elem[2]) - 2, 2), elem[3], elem[-1]))
                for elem in tab_attr_missing_corrected4:
                    if int(elem[2])%2 == 0 and int(elem[2]) > b and int(elem[1]) == i:
                        tab_attr_missing_corrected4_2.append((elem[0], elem[1], digits(int(elem[2]) - 2, 2), elem[3], elem[4], elem[-1]))


    #️ Loop that adds all the household IDs that have a different feature number and that have not been previously changed to the corrected list
    counter1, counter2, counter3 = 0, 0, 0

    for elem in (x[-1:] for x in tab_attr_missing_corrected2):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected2_2):
            tab_attr_missing_corrected2_2.append(tab_attr_missing_corrected2[counter1])
        counter1 += 1

    for elem in (x[-1:] for x in tab_attr_missing_corrected3):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected3_2):
            tab_attr_missing_corrected3_2.append(tab_attr_missing_corrected3[counter2])
        counter2 += 1
        
    for elem in (x[-1:] for x in tab_attr_missing_corrected4):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected4_2):
            tab_attr_missing_corrected4_2.append(tab_attr_missing_corrected4[counter3])
        counter3 += 1
            
        
    ###########################################################################################################


    for i in [int(ele[1]) for ele in tab_attr_missing_corrected1]:
        local_lst_2 = []
        for elem in tab_attr_missing_corrected2_2:
            if int(elem[1]) == i:
                local_lst_2.append(int(elem[2]))
        for j in local_lst_2:
            local_lst_3 = []
            missing_left_3 = []
            missing_right_3 = []
            for elem in tab_attr_missing_corrected3_2:
                if int(elem[2]) == j and int(elem[1]) == i:
                    local_lst_3.append(int(elem[3]))
            
            if len(local_lst_3)>0:
                if has_odd(local_lst_3) == True:
                    missing_left_3 = [ele for ele in range(1, maxodd(local_lst_3) + 1) if ele not in (local_lst_3) and ele%2 != 0]
                    
                if has_even(local_lst_3) == True:
                    missing_right_3 = [ele for ele in range(1, maxeven(local_lst_3) + 1) if ele not in (local_lst_3) and ele%2 == 0]
            
            if len(missing_left_3) != 0:
                for a in missing_left_3:
                    for elem in tab_attr_missing_corrected3_2:
                        if int(elem[3])%2 != 0 and int(elem[3]) > a and int(elem[1]) == i and int(elem[2]) == j:
                            tab_attr_missing_corrected3_3.append((elem[0], elem[1], elem[2], digits(int(elem[3]) - 2, 2), elem[-1]))
                    for elem in tab_attr_missing_corrected4_2:
                        if int(elem[3])%2 != 0 and int(elem[3]) > a and int(elem[1]) == i and int(elem[2]) == j:
                            tab_attr_missing_corrected4_3.append((elem[0], elem[1], elem[2], digits(int(elem[3]) - 2, 2), elem[4], elem[-1]))
                 
            if len(missing_right_3) != 0:
                for b in missing_right_3:
                    for elem in tab_attr_missing_corrected3_2:
                        if int(elem[3])%2 == 0 and int(elem[3]) > b and int(elem[1]) == i and int(elem[2]) == j:
                            tab_attr_missing_corrected3_3.append((elem[0], elem[1], elem[2], digits(int(elem[3]) - 2, 2), elem[-1]))
                    for elem in tab_attr_missing_corrected4_2:
                        if int(elem[3])%2 == 0 and int(elem[3]) > b and int(elem[1]) == i and int(elem[2]) == j:
                            tab_attr_missing_corrected4_3.append((elem[0], elem[1], elem[2], digits(int(elem[3]) - 2, 2), elem[4], elem[-1]))

    #Loop that adds all the household IDs that have a different feature number and that have not been previously changed to the corrected list
    counter1, counter2 = 0, 0

    for elem in (x[-1:] for x in tab_attr_missing_corrected3_2):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected3_3):
            tab_attr_missing_corrected3_3.append(tab_attr_missing_corrected3_2[counter1])
        counter1 += 1
        
    for elem in (x[-1:] for x in tab_attr_missing_corrected4_2):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected4_3):
            tab_attr_missing_corrected4_3.append(tab_attr_missing_corrected4_2[counter2])
        counter2 += 1


    ###########################################################################################################


    for i in [int(ele[1]) for ele in tab_attr_missing_corrected1]:
        local_lst_2 = []
        for elem in tab_attr_missing_corrected2_2:
            if int(elem[1]) == i:
                local_lst_2.append(int(elem[2]))
                
        for j in local_lst_2:
            local_lst_3 = []
            for elem in tab_attr_missing_corrected3_3:
                if int(elem[2]) == j and int(elem[1]) == i:
                    local_lst_3.append(int(elem[3]))
            
            for k in local_lst_3:
                    local_lst_4 = []
                    missing_left_4 = []
                    missing_right_4 = []
                    for elem in tab_attr_missing_corrected4_3:
                        if int(elem[2]) == j and int(elem[1]) == i and int(elem[3]) == k:
                            local_lst_4.append(int(elem[4]))
                    
                    if len(local_lst_4)>0:
                        if has_odd(local_lst_4) == True:
                            missing_left_4 = [ele for ele in range(1, maxodd(local_lst_4) + 1) if ele not in (local_lst_4) and ele%2 != 0]
                            
                        if has_even(local_lst_4) == True:
                            missing_right_4 = [ele for ele in range(1, maxeven(local_lst_4) + 1) if ele not in (local_lst_4) and ele%2 == 0]
                    
                    if len(missing_left_4) != 0:
                        for a in missing_left_4:
                            for elem in tab_attr_missing_corrected4_3:
                                if int(elem[4])%2 != 0 and int(elem[4]) > a and int(elem[1]) == i and int(elem[2]) == j and int(elem[3]) == k:
                                    tab_attr_missing_corrected4_4.append((elem[0], elem[1], elem[2], elem[3], digits(int(elem[4]) - 2, 2), elem[-1]))
                         
                    if len(missing_right_4) != 0:
                        for b in missing_right_4:
                            for elem in tab_attr_missing_corrected4_3:
                                if int(elem[4])%2 == 0 and int(elem[4]) > b and int(elem[1]) == i and int(elem[2]) == j and int(elem[3]) == k:
                                    tab_attr_missing_corrected4_4.append((elem[0], elem[1], elem[2], elem[3], digits(int(elem[4]) - 2, 2), elem[-1]))
            
    #Loop that adds all the household IDs that have a different feature number and that have not been previously changed to the corrected list  
    counter = 0
    for elem in (x[-1:] for x in tab_attr_missing_corrected4_3):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected4_4):
            tab_attr_missing_corrected4_4.append(tab_attr_missing_corrected4_3[counter])
        counter += 1
        
     
    ###########################################################################################################

    ###########################################################################################################
 
    if has_odd([int(ele[1]) for ele in tab_attr_missing_corrected1]) == True:
        duplicated_left_1 = [ele for ele in range(1, maxodd([int(ele[1]) for ele in tab_attr_missing_corrected1]) + 1) if duplicated(ele, [int(ele[1]) for ele in tab_attr_missing_corrected1]) == True and ele%2 != 0]
    if has_even([int(ele[1]) for ele in tab_attr_missing_corrected1]) == True:
        duplicated_right_1 = [ele for ele in range(1, maxeven([int(ele[1]) for ele in tab_attr_missing_corrected1]) + 1) if duplicated(ele, [int(ele[1]) for ele in tab_attr_missing_corrected1]) == True and ele%2 == 0]

    #️ Counter used to browse all elements in the feature attributes list
    counter1, counter2, counter3, counter4 = 0, 0, 0, 0
    #️ Variable containing the feat number of the duplicated household ID
    id_dupl_1, id_dupl_2, id_dupl_3, id_dupl_4 = [], [], [], []
    #️ List containing all household IDs that have been seen while browsing the attribute table
    seen1, seen2, seen3, seen4 = set(), set(), set(), set()

    for elem in (x[:-1] for x in tab_attr_missing_corrected1):
        if elem in seen1:
            id_dupl_1.append(tab_attr_missing_corrected1[counter1][-1])
        else:
            seen1.add(elem)
        counter1 += 1

    for elem in (x[:-1] for x in tab_attr_missing_corrected2_2):
        if elem in seen2:
            id_dupl_2.append(tab_attr_missing_corrected2_2[counter2][-1])
        else:
            seen2.add(elem)
        counter2 += 1

    for elem in (x[:-1] for x in tab_attr_missing_corrected3_3):
        if elem in seen3:
            id_dupl_3.append(tab_attr_missing_corrected3_3[counter3][-1])
        else:
            seen3.add(elem)
        counter3 += 1

    for elem in (x[:-1] for x in tab_attr_missing_corrected4_4):
        if elem in seen4:
            id_dupl_4.append(tab_attr_missing_corrected4_4[counter4][-1])
        else:
            seen4.add(elem)
        counter4 += 1

    ###########################################################################################################


    if len(duplicated_left_1) != 0:
        for i in duplicated_left_1:
            for elem in tab_attr_missing_corrected1:
                if int(elem[1])%2 != 0 and int(elem[1]) >= i and elem[-1] not in id_dupl_1:
                    tab_attr_duplicated_corrected1.append((elem[0], digits(int(elem[1]) + 2, 3), elem[-1]))
            for elem in tab_attr_missing_corrected2_2:
                if int(elem[1])%2 != 0 and int(elem[1]) >= i:
                    tab_attr_duplicated_corrected2.append((elem[0], digits(int(elem[1]) + 2, 3), elem[2], elem[-1]))
            for elem in tab_attr_missing_corrected3_3:
                if int(elem[1])%2 != 0 and int(elem[1]) >= i:
                    tab_attr_duplicated_corrected3.append((elem[0], digits(int(elem[1]) + 2, 3), elem[2], elem[3], elem[-1]))
            for elem in tab_attr_missing_corrected4_4:
                if int(elem[1])%2 != 0 and int(elem[1]) >= i:
                    tab_attr_duplicated_corrected4.append((elem[0], digits(int(elem[1]) + 2, 3), elem[2], elem[3], elem[4], elem[-1]))
         
    if len(duplicated_right_1) != 0:
        for i in duplicated_right_1:
            for elem in tab_attr_missing_corrected1:
                if int(elem[1])%2 == 0 and int(elem[1]) >= i and elem[-1] not in id_dupl_1:
                    tab_attr_duplicated_corrected1.append((elem[0], digits(int(elem[1]) + 2, 3), elem[-1]))
            for elem in tab_attr_missing_corrected2_2:
                if int(elem[1])%2 == 0 and int(elem[1]) >= i:
                    tab_attr_duplicated_corrected2.append((elem[0], digits(int(elem[1]) + 2, 3), elem[2], elem[-1]))
            for elem in tab_attr_missing_corrected3_3:
                if int(elem[1])%2 == 0 and int(elem[1]) >= i:
                    tab_attr_duplicated_corrected3.append((elem[0], digits(int(elem[1]) + 2, 3), elem[2], elem[3], elem[-1]))
            for elem in tab_attr_missing_corrected4_4:
                if int(elem[1])%2 == 0 and int(elem[1]) >= i:
                    tab_attr_duplicated_corrected4.append((elem[0], digits(int(elem[1]) + 2, 3), elem[2], elem[3], elem[4], elem[-1]))

            
    ###########################################################################################################

    #️ Loop that adds all the household IDs that have a different feature number and that have not been previously changed to the corrected list
    #️ Counter used to browse all elements in the feature attributes list
    counter1, counter2, counter3, counter4 = 0, 0, 0, 0

    for elem in (x[-1:] for x in tab_attr_missing_corrected1):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected1):
            tab_attr_duplicated_corrected1.append(tab_attr_missing_corrected1[counter1])
        counter1 += 1

    for elem in (x[-1:] for x in tab_attr_missing_corrected2_2):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected2):
            tab_attr_duplicated_corrected2.append(tab_attr_missing_corrected2_2[counter2])
        counter2 += 1
        
    for elem in (x[-1:] for x in tab_attr_missing_corrected3_3):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected3):
            tab_attr_duplicated_corrected3.append(tab_attr_missing_corrected3_3[counter3])
        counter3 += 1
        
    for elem in (x[-1:] for x in tab_attr_missing_corrected4_4):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected4):
            tab_attr_duplicated_corrected4.append(tab_attr_missing_corrected4_4[counter4])
        counter4 += 1


    ###########################################################################################################

    for i in [int(ele[1]) for ele in tab_attr_duplicated_corrected1]:
        local_lst_2 = []
        duplicated_left_2 = []
        duplicated_right_2 = []
        for elem in tab_attr_duplicated_corrected2:
            if int(elem[1]) == i:
                local_lst_2.append(int(elem[2]))

        if len(local_lst_2)>0:
            if has_odd(local_lst_2) == True:
                duplicated_left_2 = [ele for ele in range(1, maxodd(local_lst_2) + 1) if duplicated(ele, local_lst_2) == True and ele%2 != 0]
                
            if has_even(local_lst_2) == True:
                duplicated_right_2 = [ele for ele in range(1, maxeven(local_lst_2) + 1) if duplicated(ele, local_lst_2) == True and ele%2 == 0]
        
        if len(duplicated_left_2) != 0:
            for a in duplicated_left_2:
                for elem in tab_attr_duplicated_corrected2:
                    if int(elem[2])%2 != 0 and int(elem[2]) >= a and int(elem[1]) == i and elem[-1] not in id_dupl_2:
                        tab_attr_duplicated_corrected2_2.append((elem[0], elem[1], digits(int(elem[2]) + 2, 2), elem[-1]))
                for elem in tab_attr_duplicated_corrected3:
                    if int(elem[2])%2 != 0 and int(elem[2]) >= a and int(elem[1]) == i:
                        tab_attr_duplicated_corrected3_2.append((elem[0], elem[1], digits(int(elem[2]) + 2, 2), elem[3], elem[-1]))
                for elem in tab_attr_duplicated_corrected4:
                    if int(elem[2])%2 != 0 and int(elem[2]) >= a and int(elem[1]) == i:
                        tab_attr_duplicated_corrected4_2.append((elem[0], elem[1], digits(int(elem[2]) + 2, 2), elem[3], elem[4], elem[-1]))
             
        if len(duplicated_right_2) != 0:
            for b in duplicated_right_2:
                for elem in tab_attr_duplicated_corrected2:
                    if int(elem[2])%2 == 0 and int(elem[2]) >= b and int(elem[1]) == i and elem[-1] not in id_dupl_2:
                        tab_attr_duplicated_corrected2_2.append((elem[0], elem[1], digits(int(elem[2]) + 2, 2), elem[-1]))
                for elem in tab_attr_duplicated_corrected3:
                    if int(elem[2])%2 == 0 and int(elem[2]) >= b and int(elem[1]) == i:
                        tab_attr_duplicated_corrected3_2.append((elem[0], elem[1], digits(int(elem[2]) + 2, 2), elem[3], elem[-1]))
                for elem in tab_attr_duplicated_corrected4:
                    if int(elem[2])%2 == 0 and int(elem[2]) >= b and int(elem[1]) == i:
                        tab_attr_duplicated_corrected4_2.append((elem[0], elem[1], digits(int(elem[2]) + 2, 2), elem[3], elem[4], elem[-1]))


    #️ Loop that adds all the household IDs that have a different feature number and that have not been previously changed to the corrected list
    counter1, counter2, counter3 = 0, 0, 0

    for elem in (x[-1:] for x in tab_attr_duplicated_corrected2):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected2_2):
            tab_attr_duplicated_corrected2_2.append(tab_attr_duplicated_corrected2[counter1])
        counter1 += 1

    for elem in (x[-1:] for x in tab_attr_duplicated_corrected3):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected3_2):
            tab_attr_duplicated_corrected3_2.append(tab_attr_duplicated_corrected3[counter2])
        counter2 += 1
        
    for elem in (x[-1:] for x in tab_attr_duplicated_corrected4):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected4_2):
            tab_attr_duplicated_corrected4_2.append(tab_attr_duplicated_corrected4[counter3])
        counter3 += 1
            
        
    ###########################################################################################################


    for i in [int(ele[1]) for ele in tab_attr_duplicated_corrected1]:
        local_lst_2 = []
        for elem in tab_attr_duplicated_corrected2_2:
            if int(elem[1]) == i:
                local_lst_2.append(int(elem[2]))
        for j in local_lst_2:
            local_lst_3 = []
            duplicated_left_3 = []
            duplicated_right_3 = []
            for elem in tab_attr_duplicated_corrected3_2:
                if int(elem[2]) == j and int(elem[1]) == i:
                    local_lst_3.append(int(elem[3]))
            
            if len(local_lst_3)>0:
                if has_odd(local_lst_3) == True:
                    duplicated_left_3 = [ele for ele in range(1, maxodd(local_lst_3) + 1) if duplicated(ele, local_lst_3) == True and ele%2 != 0]
                    
                if has_even(local_lst_3) == True:
                    duplicated_right_3 = [ele for ele in range(1, maxeven(local_lst_3) + 1) if duplicated(ele, local_lst_3) == True and ele%2 == 0]
            
            if len(duplicated_left_3) != 0:
                for a in duplicated_left_3:
                    for elem in tab_attr_duplicated_corrected3_2:
                        if int(elem[3])%2 != 0 and int(elem[3]) >= a and int(elem[1]) == i and int(elem[2]) == j and elem[-1] not in id_dupl_3:
                            tab_attr_duplicated_corrected3_3.append((elem[0], elem[1], elem[2], digits(int(elem[3]) + 2, 2), elem[-1]))
                    for elem in tab_attr_duplicated_corrected4_2:
                        if int(elem[3])%2 != 0 and int(elem[3]) >= a and int(elem[1]) == i and int(elem[2]) == j:
                            tab_attr_duplicated_corrected4_3.append((elem[0], elem[1], elem[2], digits(int(elem[3]) + 2, 2), elem[4], elem[-1]))
                 
            if len(duplicated_right_3) != 0:
                for b in duplicated_right_3:
                    for elem in tab_attr_duplicated_corrected3_2:
                        if int(elem[3])%2 == 0 and int(elem[3]) >= b and int(elem[1]) == i and int(elem[2]) == j and elem[-1] not in id_dupl_3:
                            tab_attr_duplicated_corrected3_3.append((elem[0], elem[1], elem[2], digits(int(elem[3]) + 2, 2), elem[-1]))
                    for elem in tab_attr_duplicated_corrected4_2:
                        if int(elem[3])%2 == 0 and int(elem[3]) >= b and int(elem[1]) == i and int(elem[2]) == j:
                            tab_attr_duplicated_corrected4_3.append((elem[0], elem[1], elem[2], digits(int(elem[3]) + 2, 2), elem[4], elem[-1]))

    #Loop that adds all the household IDs that have a different feature number and that have not been previously changed to the corrected list
    counter1, counter2 = 0, 0

    for elem in (x[-1:] for x in tab_attr_duplicated_corrected3_2):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected3_3):
            tab_attr_duplicated_corrected3_3.append(tab_attr_duplicated_corrected3_2[counter1])
        counter1 += 1
        
    for elem in (x[-1:] for x in tab_attr_duplicated_corrected4_2):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected4_3):
            tab_attr_duplicated_corrected4_3.append(tab_attr_duplicated_corrected4_2[counter2])
        counter2 += 1


    ###########################################################################################################


    for i in [int(ele[1]) for ele in tab_attr_duplicated_corrected1]:
        local_lst_2 = []
        for elem in tab_attr_duplicated_corrected2_2:
            if int(elem[1]) == i:
                local_lst_2.append(int(elem[2]))
                
        for j in local_lst_2:
            local_lst_3 = []
            for elem in tab_attr_duplicated_corrected3_3:
                if int(elem[2]) == j and int(elem[1]) == i:
                    local_lst_3.append(int(elem[3]))
            
            for k in local_lst_3:
                    local_lst_4 = []
                    duplicated_left_4 = []
                    duplicated_right_4 = []
                    for elem in tab_attr_duplicated_corrected4_3:
                        if int(elem[2]) == j and int(elem[1]) == i and int(elem[3]) == k:
                            local_lst_4.append(int(elem[4]))
                    
                    if len(local_lst_4)>0:
                        if has_odd(local_lst_4) == True:
                            duplicated_left_4 = [ele for ele in range(1, maxodd(local_lst_4) + 1) if duplicated(ele, local_lst_4) == True and ele%2 != 0]
                            
                        if has_even(local_lst_4) == True:
                            duplicated_right_4 = [ele for ele in range(1, maxeven(local_lst_4) + 1) if duplicated(ele, local_lst_4) == True and ele%2 == 0]
                    
                    if len(duplicated_left_4) != 0:
                        for a in duplicated_left_4:
                            for elem in tab_attr_duplicated_corrected4_3:
                                if int(elem[4])%2 != 0 and int(elem[4]) >= a and int(elem[1]) == i and int(elem[2]) == j and int(elem[3]) == k and elem[-1] not in id_dupl_4:
                                    tab_attr_duplicated_corrected4_4.append((elem[0], elem[1], elem[2], elem[3], digits(int(elem[4]) + 2, 2), elem[-1]))
                         
                    if len(duplicated_right_4) != 0:
                        for b in duplicated_right_4:
                            for elem in tab_attr_duplicated_corrected4_3:
                                if int(elem[4])%2 == 0 and int(elem[4]) >= b and int(elem[1]) == i and int(elem[2]) == j and int(elem[3]) == k and elem[-1] not in id_dupl_4:
                                    tab_attr_duplicated_corrected4_4.append((elem[0], elem[1], elem[2], elem[3], digits(int(elem[4]) + 2, 2), elem[-1]))
            
    #Loop that adds all the household IDs that have a different feature number and that have not been previously changed to the corrected list  
    counter = 0
    for elem in (x[-1:] for x in tab_attr_duplicated_corrected4_3):
        if elem not in (x[-1:] for x in tab_attr_duplicated_corrected4_4):
            tab_attr_duplicated_corrected4_4.append(tab_attr_duplicated_corrected4_3[counter])
        counter += 1
        
     
    ###########################################################################################################


     
    #️ If statement for displaying a message to the user and changing attribute values depending on whether there is an houselhold ID missing or not 
    if (len(missing_ids)!=0 or len(duplicated_ids)!=0) and check_hhs == 2:
        print("Missing road IDs:")
        if len(missing_ids)!=0:
            for elem in sorted(missing_ids):
                print("\t●", elem)   
        else:
            print("\t● None")
        print("\nDuplicate road IDs:")
        if len(duplicated_ids)!=0:
            for elem in sorted(duplicated_ids):
                print("\t●", elem)   
        else:
            print("\t● None")
            
        if len(missing_ids)!=0:
            reply_missing = 'The IDs of the following roads are missing on the map:\n\t● {0}'.format("\n\t● ".join(missing_ids)) + "\nDo you want to decrement the IDs above the missing ones?\n\n\n"
        else:
            reply_missing = "No missing road IDs on the map\n\n\n"
        if len(duplicated_ids) != 0:
            reply_duplicated = 'The IDs of the following roads are duplicated on the map:\n\t● {0}'.format("\n\t● ".join(duplicated_ids)) + "\nDo you want to increment the IDs above the duplicated ones?\n"
        else:
            reply_duplicated = "No duplicate road IDs on the map\n\n"
        reply = input_message_yes_no('Continue?', reply_missing + reply_duplicated)
        if reply == QMessageBox.Yes:
            for i in range(0, fc1):
                if caps1 & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs1 = {0: tab_attr_missing_corrected1[i][0], 1: tab_attr_missing_corrected1[i][1]}
                    layer_roads1.dataProvider().changeAttributeValues({ tab_attr_missing_corrected1[i][-1] : attrs1 })
            for i in range(0, fc2):
                if caps2 & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs2 = {0: tab_attr_missing_corrected2_2[i][0], 1: tab_attr_missing_corrected2_2[i][1], 2: tab_attr_missing_corrected2_2[i][2]}
                    layer_roads2.dataProvider().changeAttributeValues({ tab_attr_missing_corrected2_2[i][-1] : attrs2 })
            for i in range(0, fc3):
                if caps3 & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs3 = {0: tab_attr_missing_corrected3_3[i][0], 1: tab_attr_missing_corrected3_3[i][1], 2: tab_attr_missing_corrected3_3[i][2], 3: tab_attr_missing_corrected3_3[i][3]}
                    layer_roads3.dataProvider().changeAttributeValues({ tab_attr_missing_corrected3_3[i][-1] : attrs3 })
            for i in range(0, fc4):
                if caps4 & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs4 = {0: tab_attr_missing_corrected4_4[i][0], 1: tab_attr_missing_corrected4_4[i][1], 2: tab_attr_missing_corrected4_4[i][2], 3: tab_attr_missing_corrected4_4[i][3], 4: tab_attr_missing_corrected4_4[i][4]}
                    layer_roads4.dataProvider().changeAttributeValues({ tab_attr_missing_corrected4_4[i][-1] : attrs4 })
            
            ###  Updating and reloading layer data
            for i in layers:
                i.dataProvider().forceReload()
                i.triggerRepaint()
                iface.mapCanvas().refreshAllLayers()
                
            for i in range(0, fc1):
                if caps1 & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs1 = {0: tab_attr_duplicated_corrected1[i][0], 1: tab_attr_duplicated_corrected1[i][1]}
                    layer_roads1.dataProvider().changeAttributeValues({ tab_attr_duplicated_corrected1[i][-1] : attrs1 })
            for i in range(0, fc2):
                if caps2 & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs2 = {0: tab_attr_duplicated_corrected2_2[i][0], 1: tab_attr_duplicated_corrected2_2[i][1], 2: tab_attr_duplicated_corrected2_2[i][2]}
                    layer_roads2.dataProvider().changeAttributeValues({ tab_attr_duplicated_corrected2_2[i][-1] : attrs2 })
            for i in range(0, fc3):
                if caps3 & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs3 = {0: tab_attr_duplicated_corrected3_3[i][0], 1: tab_attr_duplicated_corrected3_3[i][1], 2: tab_attr_duplicated_corrected3_3[i][2], 3: tab_attr_duplicated_corrected3_3[i][3]}
                    layer_roads3.dataProvider().changeAttributeValues({ tab_attr_duplicated_corrected3_3[i][-1] : attrs3 })
            for i in range(0, fc4):
                if caps4 & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs4 = {0: tab_attr_duplicated_corrected4_4[i][0], 1: tab_attr_duplicated_corrected4_4[i][1], 2: tab_attr_duplicated_corrected4_4[i][2], 3: tab_attr_duplicated_corrected4_4[i][3], 4: tab_attr_duplicated_corrected4_4[i][4]}
                    layer_roads4.dataProvider().changeAttributeValues({ tab_attr_duplicated_corrected4_4[i][-1] : attrs4 })
                    
            ###  Updating and reloading layer data
            for i in layers:
                i.dataProvider().forceReload()
                i.triggerRepaint()
                iface.mapCanvas().refreshAllLayers()
             
            print("\nRoads fixed") 
            show_popup_message("Success", "Missing and Duplicate road IDs have been changed on the map.", "information")
            check_roads = 1
        else:
            print("\nRoads not fixed")
            show_popup_message("Information", "Missing and Duplicate road IDs are still present on the map.", "information")
    elif check_hhs == 2:
        print("Missing road IDs:\n\t● None")
        print("Duplicate road IDs:\n\t● None")
        show_popup_message("Information", "No missing or duplicate road IDs on the map.", "information")
        check_roads = 2
          
    ###########################################################################################################
    if check_hhs == 2:
        for i in tab_attr_duplicated_corrected1:
            for j in ids_roads1_with_hhs:
                if i[-1] == j[-1]:
                    ids_roads1_with_hhs_corrected.append(('-'.join(i[:-1]), i[-1]))
        for i in tab_attr_duplicated_corrected2_2:
            for j in ids_roads2_with_hhs:
                if i[-1] == j[-1]:
                    ids_roads2_with_hhs_corrected.append(('-'.join(i[:-1]), i[-1]))
        for i in tab_attr_duplicated_corrected3_3:
            for j in ids_roads3_with_hhs:
                if i[-1] == j[-1]:
                    ids_roads3_with_hhs_corrected.append(('-'.join(i[:-1]), i[-1]))
        for i in tab_attr_duplicated_corrected4_4:
            for j in ids_roads4_with_hhs:
                if i[-1] == j[-1]:
                    ids_roads4_with_hhs_corrected.append(('-'.join(i[:-1]), i[-1]))

        for i in tab_attr_hhs:
            
            for j in main_road_with_hhs:
                if i[0] == j:
                    tab_attr_hhs_corrected.append(i)
                            
            for j in ids_roads1_with_hhs:
                if i[0] == j[0]:
                    for k in ids_roads1_with_hhs_corrected:
                        if j[-1] == k[-1]:
                            tab_attr_hhs_corrected.append((k[0],) + (i[1:]))
                            
            for j in ids_roads2_with_hhs:
                if i[0] == j[0]:
                    for k in ids_roads2_with_hhs_corrected:
                        if j[-1] == k[-1]:
                            tab_attr_hhs_corrected.append((k[0],) + (i[1:]))
                            
            for j in ids_roads3_with_hhs:
                if i[0] == j[0]:
                    for k in ids_roads3_with_hhs_corrected:
                        if j[-1] == k[-1]:
                            tab_attr_hhs_corrected.append((k[0],) + (i[1:]))
                            
            for j in ids_roads4_with_hhs:
                if i[0] == j[0]:
                    for k in ids_roads4_with_hhs_corrected:
                        if j[-1] == k[-1]:
                            tab_attr_hhs_corrected.append((k[0],) + (i[1:]))

    #pprint.pprint(sorted(tab_attr_hhs_corrected, key=len))

    ###########################################################################################################

    #️ If statement for changing attribute values depending on whether there is an houselhold ID missing or not 
    if check_hhs == 2 and check_roads == 1:
            for i in range(0, fc_hhs):
                if capshhs & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs_hhs = {0: tab_attr_hhs_corrected[i][0], 1: tab_attr_hhs_corrected[i][1], 2: tab_attr_hhs_corrected[i][2], 3: tab_attr_hhs_corrected[i][3], 4: tab_attr_hhs_corrected[i][4], 5: tab_attr_hhs_corrected[i][5], 6: tab_attr_hhs_corrected[i][6], 7: tab_attr_hhs_corrected[i][7], 8: tab_attr_hhs_corrected[i][8], 9: tab_attr_hhs_corrected[i][9]}
                    layer_hhs.dataProvider().changeAttributeValues({ tab_attr_hhs_corrected[i][-1] : attrs_hhs })
            
            ###  Updating and reloading layer data
            for i in layers:
                i.dataProvider().forceReload()
                i.triggerRepaint()
                iface.mapCanvas().refreshAllLayers()
                
            show_popup_message("Success", "Household IDs have been updated on the map as a result of the changes applied to the road IDs.", "information")
            print("Household IDs fixed")
    elif check_roads != 2 and check_hhs == 2:
        show_popup_message("Information", "Household IDs have not been changed on the map.", "information")
        print("Household IDs not fixed")
        
    ###########################################################################################################
    count0, count1, count2, count3, count4 = [], [], [], [], []
    tab_hhs_attr_road = [ele[0] for ele in tab_attr_hhs_corrected]
    list_all_roads = []
    roads_with_hhs2 = []

    for i in tab_hhs_attr_road:
        if roads_with_hhs2.count(i) == 0:
            roads_with_hhs2.append(i)
            
    main_road_with_hhs2 = [ele for ele in roads_with_hhs2 if len(ele) < 7]
    roads1_with_hhs2 = [ele for ele in roads_with_hhs2 if len(ele) == 7]
    roads2_with_hhs2 = [ele for ele in roads_with_hhs2 if len(ele) == 10]
    roads3_with_hhs2 = [ele for ele in roads_with_hhs2 if len(ele) == 13]
    roads4_with_hhs2 = [ele for ele in roads_with_hhs2 if len(ele) == 16]

    for i in main_road_with_hhs2:
        count0.append(tab_hhs_attr_road.count(i))
    #for i in range(len(main_road_with_hhs2)):
    #    print(main_road_with_hhs2[i], "\t", count0[i], "HHs")

    for i in roads1_with_hhs2:
        count1.append(tab_hhs_attr_road.count(i))
    #for i in range(len(roads1_with_hhs2)):
    #    print(roads1_with_hhs2[i], "\t", count1[i], "HHs")

    for i in roads2_with_hhs2:
        count2.append(tab_hhs_attr_road.count(i))
    #for i in range(len(roads2_with_hhs2)):
    #    print(roads2_with_hhs2[i], "\t", count2[i], "HHs")

    for i in roads3_with_hhs2:
        count3.append(tab_hhs_attr_road.count(i))
    #for i in range(len(roads3_with_hhs2)):
    #    print(roads3_with_hhs2[i], "\t", count3[i], "HHs")

    for i in roads4_with_hhs2:
        count4.append(tab_hhs_attr_road.count(i))
    #for i in range(len(roads4_with_hhs2)):
    #    print(roads4_with_hhs2[i], "\t", count4[i], "HHs")

    for i in tab_attr_main_road:
        list_all_roads.append(('-'.join(i[:-1]), i[-1]))

    for i in tab_attr_duplicated_corrected1:
        list_all_roads.append(('-'.join(i[:-1]), i[-1]))
        
    for i in tab_attr_duplicated_corrected2_2:
        list_all_roads.append(('-'.join(i[:-1]), i[-1]))

    for i in tab_attr_duplicated_corrected3_3:
        list_all_roads.append(('-'.join(i[:-1]), i[-1]))

    for i in tab_attr_duplicated_corrected4_4:
        list_all_roads.append(('-'.join(i[:-1]), i[-1]))

    if check_roads == 1 or check_roads == 2:
        counter = 0
        for i in list_all_roads:
            counter0 = 0
            for j in main_road_with_hhs2:
                if j == i[0]:
                    if caps0 & QgsVectorDataProvider.ChangeAttributeValues:
                        attrs0 = {1: count0[counter0]}
                        layer_main_road.dataProvider().changeAttributeValues({ i[-1] : attrs0 })
                counter0 += 1
            counter1 = 0
            for j in roads1_with_hhs2:
                if j == i[0]:
                    if caps1 & QgsVectorDataProvider.ChangeAttributeValues:
                        attrs1 = {2: count1[counter1]}
                        layer_roads1.dataProvider().changeAttributeValues({ i[-1] : attrs1 })
                counter1 += 1
            counter2 = 0
            for j in roads2_with_hhs2:
                if j == i[0]:
                    if caps2 & QgsVectorDataProvider.ChangeAttributeValues:
                        attrs2 = {3: count2[counter2]}
                        layer_roads2.dataProvider().changeAttributeValues({ i[-1] : attrs2 })
                counter2 += 1
            counter3 = 0
            for j in roads3_with_hhs2:
                if j == i[0]:
                    if caps3 & QgsVectorDataProvider.ChangeAttributeValues:
                        attrs3 = {4: count3[counter3]}
                        layer_roads3.dataProvider().changeAttributeValues({ i[-1] : attrs3 })
                counter3 += 1
            counter4 = 0
            for j in roads4_with_hhs2:
                if j == i[0]:
                    if caps4 & QgsVectorDataProvider.ChangeAttributeValues:
                        attrs4 = {5: count4[counter4]}
                        layer_roads4.dataProvider().changeAttributeValues({ i[-1] : attrs4 })
                counter4 += 1
            counter += 1
        
        ###  Updating and reloading layer data
        for i in layers:
            i.dataProvider().forceReload()
            i.triggerRepaint()
            iface.mapCanvas().refreshAllLayers()
        
print("\n")