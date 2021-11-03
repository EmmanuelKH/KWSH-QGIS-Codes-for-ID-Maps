##
##  Program to identify and fix missing and duplicated household IDs within a QGIS vector layer
##
##  Author: Emmanuel Boisseau for Khmer Water Supply Holding Co.Ltd. (KWSH)
##
##  Version 1.0 - This program only works for single missing or single duplicated features 
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
# ⚠️ Write below the exact file path to the Customers IDs layer as 'fn' string variable
fn = "C:/Users/etudiant/Desktop/Work/ENSE3/Stage 2A/SIG/Tram Khnar ID Map - 013 - for recording/Layers/Households/Household IDs.shp"
layer = QgsVectorLayer(fn, "Households", "ogr")
caps = layer.dataProvider().capabilities()

#️ List for all the attributes of all the features within the layer
tab_attr = []

#️ Lists of missing households IDs and duplicated households IDs as string variables
duplicated_ids, missing_ids = [], []
duplicated_ids_display = []

#️ Corrected list for missing features and duplicated features
tab_attr_missing_corrected, tab_attr_duplicated_corrected = [], []

#️ List for listing the IDs of all the roads to which the households are attached
roads = []

check_digits_all = 0

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
    
def check_digits(elem, digits):
    if len(elem) != digits:
        return False
    else:
        return True

##  Filling of the feature attributes and roads lists
#️ Number of features within the layer
fc = layer.featureCount()

#️ Loop that adds all the relevant feature attributes to a list of tuples
for i in range(0, fc):
    feat = layer.getFeature(i)
    tab_attr.append((feat['Road ID'], feat['Direction'], feat['Side Order'], feat['St Frtg No'], feat.id()))
    
if len(tab_attr) != 0:
    #️ Copy each element of the tuples for all the tuples within the list into a single lists for each attribute/element
    road_id, direction, side_order, st_frtg_no, feature_no = zip(*tab_attr)

    #️ Loop that adds all the road IDs to a list without duplicated values
    for i in road_id:
        if roads.count(i) == 0:
            roads.append(i)
        
    ##  Identification and change of household IDs with a value greater than the missing ID if a missing ID exists
    #️ Loop that fills a list with the corrected ID for households with an ID greater than the missing one

    ctr = 0
    lst_index_wrong = []
    res = []
    lst_roads_wrong = []
    for elem in tab_attr:
        if check_digits(elem[0].split("-")[0], 3) == False:
            lst_index_wrong.append(ctr)
        if len(elem[0].split("-")) > 1 and check_digits(elem[0].split("-")[1], 3) == False:
                lst_index_wrong.append(ctr)
        if len(elem[0].split("-")) > 2 and check_digits(elem[0].split("-")[2], 2) == False:
                lst_index_wrong.append(ctr)
        if len(elem[0].split("-")) > 3 and check_digits(elem[0].split("-")[3], 2) == False:
                lst_index_wrong.append(ctr)
        if len(elem[0].split("-")) > 4 and check_digits(elem[0].split("-")[4], 2) == False:
                lst_index_wrong.append(ctr)
        if check_digits(elem[2], 3) == False:
            lst_index_wrong.append(ctr)
        if elem[3] != NULL and check_digits(elem[3], 1) == False:
            lst_index_wrong.append(ctr)
        ctr += 1

    [res.append(x) for x in lst_index_wrong if x not in res]
    for i in res:
        lst_roads_wrong.append("-".join(filter(None,tab_attr[i][:-1])))
    if len(res) != 0:
        print("There is a problem with the number of digits regarding the following households:")
        print("\t", *sorted(lst_roads_wrong, key=len), sep = "\n\t. ")
        print("\nReminder: Household IDs should be entered as follows:")
        print("-Road ID:\n\t-3 digits for the main road\n\t-3 digits for branch roads 1\n\t-2 digits for branch roads 2, 3 and 4")
        print("-Side Order: 3 digits")
        print("-Street Frontage Number: 1 digit or NULL value")
        print("e.g.: NR3-002-01-04-05-L-001-B1 ; NR3-065-08-11-15-R-023-B2")
        print("\nPlease correct the household IDs previously indicated and then rerun the program to determine the potential missing and duplicate household IDs.")
        show_popup_message("Error", "There is a problem with the number of digits regarding the following households:\n\t. " + '\n\t. '.join('{}'.format(item) for item in lst_roads_wrong) + "\n\n\n\n\nReminder: Household IDs should be entered as follows:"+ "\n-Road ID:\n\t-3 digits for the main road\n\t-3 digits for branch roads 1\n\t-2 digits for branch roads 2, 3 and 4" + "\n-Side Order: 3 digits" + "\n-Street Frontage Number: 1 digits or NULL value"+ "\n\ne.g.: NR3-002-01-04-05-L-001-B1 ; NR3-065-08-11-15-L-023-B2" + "\n\nPlease correct the household IDs previously indicated and then rerun the program to determine the potential missing and duplicate household IDs." , "error")
        check_digits_all = 1
    else:
        print("All household IDs contain road IDs, side order numbers and street frontage numbers written with the correct number of digits.")

    ##  Identification and change of household IDs with a value greater than the missing ID if a missing ID exists
    #️ Loop that fills a list with the corrected ID for households with an ID greater than the missing one
    for elem in roads:
        
        #️ Counters used to browse all elements in the feature attributes list
        counter1, counter2, counter3 = 0, 0, 0
        
        #️ Lists containing all the IDs for a given road for both left and right sides
        lst_side_order_left, lst_side_order_right = [], []
        
        #️ Lists containing the missing IDs for a given road for both left and right sides
        missing_left, missing_right = [], []
        
        #️ Loop that fills the lists with all the IDs for a given road for both left and right sides
        while (counter1 != len(tab_attr)):
            if road_id[counter1] == elem:
                if direction[counter1] == "L":
                    lst_side_order_left.append(int(side_order[counter1]))
                if direction[counter1] == "R":
                    lst_side_order_right.append(int(side_order[counter1]))
            counter1 += 1
         
        #️ Loop that fills the lists with the missing IDs for a given road for both left and right sides
        if len(lst_side_order_left) != 0:
            missing_left = [ele for ele in range(1, max(lst_side_order_left) + 1) if ele not in lst_side_order_left]
        if len(lst_side_order_right) != 0:
            missing_right = [ele for ele in range(1, max(lst_side_order_right) + 1) if ele not in lst_side_order_right]
        
        #️ Loop that fills a list with the corrected ID for households with an ID greater than the missing one for a given road
        if len(missing_left) != 0 or len(missing_right) != 0:
            
            for i in missing_left:
                missing_ids.append(elem + "-L-" + digits(i, 3))
                while (counter2 != len(tab_attr)):
                    #️ If statement for only decreasing side order number of households with the same road ID, left direction and a side order number above the missing household side order
                    if (road_id[counter2] == elem) and (direction[counter2] == "L") and (int(side_order[counter2]) > i):
                        tab_attr_missing_corrected.append((road_id[counter2], direction[counter2], digits(int(side_order[counter2]) - 1, 3), st_frtg_no[counter2], feature_no[counter2]))
                    counter2 += 1
                    
            for j in missing_right:
                missing_ids.append(elem + "-R-" + digits(j, 3))
                while (counter3 != len(tab_attr)):
                    #️ If statement for only decreasing side order number of households with the same road ID, right direction and a side order number above the missing household side order
                    if (road_id[counter3] == elem) and (direction[counter3] == "R") and (int(side_order[counter3]) > j):
                        tab_attr_missing_corrected.append((road_id[counter3], direction[counter3], digits(int(side_order[counter3]) - 1, 3), st_frtg_no[counter3], feature_no[counter3]))
                    counter3 += 1

    #️ Counter used to browse all elements in the feature attributes list
    counter4 = 0

    #️ Loop that adds all the household IDs that have a different feature number and that have not been previously changed to the corrected list
    for elem in (x[-1:] for x in tab_attr):
        if elem not in (x[-1:] for x in tab_attr_missing_corrected):
            tab_attr_missing_corrected.append(tab_attr[counter4])
        counter4 += 1

    #️ Copy each element of the tuples for all the tuples within the list into a single lists for each corrected attribute/element
    road_id_corr_missing, direction_corr_missing, side_order_corr_missing, st_frtg_no_corr_missing, feature_no_corr_missing = zip(*tab_attr_missing_corrected)

    #️ If statement for displaying a message to the user and changing attribute values depending on whether there is an houselhold ID missing or not 
    if check_digits_all == 0:
        print("\nMissing household IDs:")
        if len(missing_ids)!=0:
            for elem in sorted(missing_ids):
                print("\t●", elem)   
        else:
            print("\t● None")
            
        if len(missing_ids)!=0:
            reply_missing = input_message_yes_no('Continue?', 'The IDs of the following households are missing on the map:\n\t● {0}'.format("\n\t● ".join(missing_ids)) + "\n\nDo you want to decrement the IDs above the missing ones?")
            if reply_missing == QMessageBox.Yes:
                for i in range(0, fc):
                    if caps & QgsVectorDataProvider.ChangeAttributeValues:
                        attrs = {0: road_id_corr_missing[i], 1: direction_corr_missing[i], 2: side_order_corr_missing[i], 3: st_frtg_no_corr_missing[i]}
                        layer.dataProvider().changeAttributeValues({ feature_no_corr_missing[i] : attrs })
                print("Missing households fixed\n")
                show_popup_message("Success", "Missing household IDs have been changed on the map.", "information")
            else:
                print("Missing households not fixed\n")
                show_popup_message("Information", "Missing household IDs are still present on the map.", "information")
        else:
            show_popup_message("Information", "No missing HH IDs on the map.", "information")
        


    ##  Identification and change of household IDs with a value greater than the duplicated IDs if duplicated IDs exist
    #️ Counter used to browse all elements in the feature attributes list
    counter5 = 0
    #️ Variable containing the feat number of the duplicated household ID
    id_dupl = []
    #️ List containing all household IDs that have been seen while browsing the attribute table
    seen = set()
    #️ Loop that adds all the duplicated households IDs within a list
    for elem in (x[:-1] for x in tab_attr):
        if elem in seen:
            duplicated_ids.append(elem)
            id_dupl.append(feature_no[counter5])
        else:
            seen.add(elem)
        counter5 += 1

    for i in duplicated_ids:
        duplicated_ids_display.append('-'.join([str(ele) for ele in i if ele != NULL]))

    #️ Counter used to browse all elements in the feature attributes list
    counter6 = 0
    #️ If statement for displaying a message to the user and changing attribute values depending on whether there is an houselhold ID duplicated or not 
    if check_digits_all == 0:
        print("Duplicate household IDs:")
        if len(duplicated_ids)!=0:
            for elem in sorted(duplicated_ids_display):
                print("\t●", elem)   
        else:
            print("\t● None")
        
        if len(duplicated_ids) == 0:
            show_popup_message("Information", "No duplicate HH IDs on the map.", "information")
        else:
            for elem in duplicated_ids:
                #️ Counter used to browse all elements in the feature attributes list
                counter7 = 0
                while (counter7 != len(tab_attr)):
                    if ((road_id[counter7] == elem[0]) and (direction[counter7] == elem[1]) and (side_order[counter7] >= elem[2]) and (feature_no[counter7] != id_dupl[counter6])):
                        tab_attr_duplicated_corrected.append((road_id[counter7], direction[counter7], digits(int(side_order[counter7]) + 1, 3), st_frtg_no[counter7], feature_no[counter7]))
                    else:
                        tab_attr_duplicated_corrected.append((road_id[counter7], direction[counter7], side_order[counter7], st_frtg_no[counter7], feature_no[counter7]))
                    counter7 += 1
                counter6 += 1
                
            road_id_corr_duplicated, direction_corr_duplicated, side_order_corr_duplicated, st_frtg_no_corr_duplicated, feature_no_corr_duplicated = zip(*tab_attr_duplicated_corrected)

            reply = input_message_yes_no('Continue?', 'The IDs of the following households are duplicated on the map:\n\t● {0}'.format("\n\t● ".join(duplicated_ids_display)) + '\n\nDo you want to increment the IDs above the duplicated ones?')
            if reply == QMessageBox.Yes:
                for i in range(0, fc):
                    if caps & QgsVectorDataProvider.ChangeAttributeValues:
                        attrs = {0: road_id_corr_duplicated[i], 1: direction_corr_duplicated[i], 2: side_order_corr_duplicated[i], 3: st_frtg_no_corr_duplicated[i]}
                        layer.dataProvider().changeAttributeValues({ feature_no_corr_duplicated[i] : attrs })
                print("Duplicate households fixed")
                show_popup_message("Success", "Duplicate household IDs have been changed on the map.", "information")
            else:
                print("Duplicate households not fixed")
                show_popup_message("Information", "Duplicate household IDs are still present on the map.", "information")

    ##  Updating and reloading layer data
    layer.dataProvider().forceReload()
    layer.triggerRepaint()
    iface.mapCanvas().refreshAllLayers()

    print("\n")