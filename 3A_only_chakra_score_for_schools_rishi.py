# -*- coding: utf-8 -*-
"""
Created on Wed May 22 14:36:10 2019
Modified on Tue May 04 23:27 2021

@author: Pranbir Sarkar, Rishi Dey (Modification & Optimization)

DESCRIPTION : Calculate Overall similarity of a new user & Calculate Chakra Score Only

TABLE USED :
    achievement_strength_data : store the prepared data of the new user
    achievement_strength_data_group : aggregated data of achievements of users
    chakra_score_each_users : intermidiate table to store chakra wise value of the user
    user_life_strengths : capture user's life strength
    user_achievements : capture user's life achievements
    life_strength : Mapping with the tables to get the ontology CODE
"""

#IMPORTS
import pymysql
import numpy as np
import math
from scipy import spatial
import sys

#DECLARATION
user_id = sys.argv[1]
mydb = pymysql.connect(
                        user = "root",
                        host = "127.0.0.1",
                        db = "lifevitaenew",
                        password = "lifevitae",
                        use_unicode = True
                    )
mycursor = mydb.cursor()

def h_array_to_v_array(arr):
    v_array = []
    for item in arr:
        v_array.append([item])
    return v_array

#INITIALIZATION
code_array = [ "CO1", "CO2", "CO3", "CO4", "CO5", "CO6", "CO7", "IN1", "IN2", "IN3", "IN4", "IN5", "IN6", "IN7", "EM1", "EM2", "EM3", "EM4", "EM5", "EM6", "EM7", "AD1", "AD2", "AD3", "AD4", "AD5", "AD6", "AD7", "CR1", "CR2", "CR3", "CR4", "CR5", "CR6", "CR7", "MO1", "MO2", "MO3", "MO4", "MO5", "MO6", "MO7"]
code_values = {i: 0 for i in code_array}
co_array = [
        [100,90,80,90,80,80,90],
        [90,100,80,90,80,80,90],
        [80,80,100,80,90,90,80],
        [90,90,80,100,80,80,90],
        [80,80,90,80,100,90,80],
        [80,80,90,80,90,100,80],
        [90,90,80,90,80,80,100]
        ]
i_array = [
        [100,90,90,90,80,90,80],
        [90,100,90,90,80,90,80],
        [90,90,100,90,80,90,80],
        [90,90,90,100,80,90,80],
        [80,80,80,80,100,80,90],
        [90,90,90,90,80,100,80],
        [80,80,80,80,90,80,100]
        ]
e_array = [
        [100,80,80,90,80,80,90],
        [80,100,90,80,90,90,80],
        [80,90,100,80,90,90,80],
        [90,80,80,100,80,80,90],
        [80,90,90,80,100,90,80],
        [80,90,90,80,90,100,80],
        [90,80,80,90,80,80,100]
        ]
a_array = [
        [100,80,90,90,80,90,80],
        [80,100,80,80,90,80,90],
        [90,80,100,90,80,90,80],
        [90,80,90,100,80,90,80],
        [80,90,80,80,100,80,90],
        [90,80,90,90,80,100,80],
        [80,90,80,80,90,80,100]
        ]
cr_array = [
        [100,80,80,80,90,90,80],
        [80,100,90,90,80,80,90],
        [80,90,100,90,80,80,90],
        [80,90,90,100,80,80,90],
        [90,80,80,80,100,90,80],
        [90,80,80,80,90,100,80],
        [80,90,90,90,80,80,100]
        ]
m_array = [
        [100,90,90,80,80,80,90],
        [90,100,90,80,80,80,90],
        [90,90,100,80,80,80,90],
        [80,80,80,100,90,90,80],
        [80,80,80,90,100,90,80],
        [80,80,80,90,90,100,80],
        [90,90,90,80,80,80,100]
        ]

co_array_np = np.array(co_array)
i_array_np = np.array(i_array)
e_array_np = np.array(e_array)
a_array_np = np.array(a_array)
cr_array_np = np.array(cr_array)
m_array_np = np.array(m_array)

#PROCESS
mycursor.execute('SELECT a.`user_id`, a.`strengths`, b.`code` FROM `user_life_strengths` a join `life_strength` b ON a.`strengths` = b.`achievements_strength` where `user_id` = %s;', str(user_id))
output = mycursor.fetchall()

update_query_1 = "UPDATE `achievement_strength_data` SET "
code_flags = {i: True for i in code_array}
for x in output:
    user_id_output = x[0]
    strength_text = x[1]
    strength_code = x[2]
    if strength_code in code_array:
        update_query_1 += "`"+strength_code+"` = '1',"
        if code_flags[ strength_code ]:
            code_values[ strength_code ] += 1
            code_flags[ strength_code ] = False
update_query_1 = update_query_1[:-1]
update_query_1 += " WHERE `user_id` = "+str(user_id)+" and `Category` = \"Strength\";"
len_output_1 = len(output)

mycursor.execute('SELECT a.`user_id`, a.`strength`, b.`code` FROM `user_achievements` a join `life_strength` b ON a.`strength` = b.`achievements_strength` where `user_id` = %s;', (str(user_id)) )
output = mycursor.fetchall()

update_query_2 = "UPDATE `achievement_strength_data` SET "
code_flags = {i: True for i in code_array}
for x in output:
    user_id_output = x[0]
    strength_text = x[1]
    strength_code = x[2]
    if strength_code in code_array:
        update_query_2 += "`"+strength_code+"` = '1',"
        if code_flags[ strength_code ]:
            code_values[ strength_code ] += 1
            code_flags[ strength_code ] = False
update_query_2 = update_query_2[:-1]
update_query_2 += " WHERE `user_id` = "+str(user_id)+" and `Category` = \"achievement\";"
len_output_2 = len(output)

mycursor.execute('SELECT `CO1`, `CO2`, `CO3`, `CO4`, `CO5`, `CO6`, `CO7`, `IN1`, `IN2`, `IN3`, `IN4`, `IN5`, `IN6`, `IN7`, `EM1`, `EM2`, `EM3`, `EM4`, `EM5`, `EM6`, `EM7`, `AD1`, `AD2`, `AD3`, `AD4`, `AD5`, `AD6`, `AD7`, `CR1`, `CR2`, `CR3`, `CR4`, `CR5`, `CR6`, `CR7`, `MO1`, `MO2`, `MO3`, `MO4`, `MO5`, `MO6`, `MO7` FROM achievement_strength_data_group where user_id = %s;', (str(user_id)) )
output = mycursor.fetchall()

if len(output) > 0 and list(code_values.values()) == list(output[0]):
    #print('No Change required')
    mydb.close()
    exit()
#print('Change required')
#Calculation
mycursor.execute("delete from achievement_strength_data where user_id = %s;", (str(user_id)) )
mycursor.execute("delete from achievement_strength_data_group where user_id = %s;", (str(user_id)) )
mycursor.execute("delete from chakra_score_each_users where user_id = %s;", (str(user_id)) )

mycursor.execute('INSERT INTO `achievement_strength_data` (`user_id` , `Category`) VALUES (%s, \"Strength\");', str(user_id))
if len_output_1 > 0:
    mycursor.execute(update_query_1)

mycursor.execute('INSERT INTO `achievement_strength_data` ( `user_id` , `Category`) VALUES (%s , \"achievement\");', str(user_id))
if len_output_2 > 0:
    mycursor.execute(update_query_2)

query = 'INSERT INTO `achievement_strength_data_group`( `user_id`, `CO1`, `CO2`, `CO3`, `CO4`, `CO5`, `CO6`, `CO7`, `IN1`, `IN2`, `IN3`, `IN4`, `IN5`, `IN6`, `IN7`, `EM1`, `EM2`, `EM3`, `EM4`, `EM5`, `EM6`, `EM7`, `AD1`, `AD2`, `AD3`, `AD4`, `AD5`, `AD6`, `AD7`, `CR1`, `CR2`, `CR3`, `CR4`, `CR5`, `CR6`, `CR7`, `MO1`, `MO2`, `MO3`, `MO4`, `MO5`, `MO6`, `MO7`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
mycursor.execute(query, (str(user_id), code_values['CO1'], code_values['CO2'], code_values['CO3'], code_values['CO4'], code_values['CO5'], code_values['CO6'], code_values['CO7'], code_values['IN1'], code_values['IN2'], code_values['IN3'], code_values['IN4'], code_values['IN5'], code_values['IN6'], code_values['IN7'], code_values['EM1'], code_values['EM2'], code_values['EM3'], code_values['EM4'], code_values['EM5'], code_values['EM6'], code_values['EM7'], code_values['AD1'], code_values['AD2'], code_values['AD3'], code_values['AD4'], code_values['AD5'], code_values['AD6'], code_values['AD7'], code_values['CR1'], code_values['CR2'], code_values['CR3'], code_values['CR4'], code_values['CR5'], code_values['CR6'], code_values['CR7'], code_values['MO1'], code_values['MO2'], code_values['MO3'], code_values['MO4'], code_values['MO5'], code_values['MO6'], code_values['MO7']) )

insert_query = "INSERT INTO `chakra_score_each_users` ( `user_id`, `COGNITIVE`, `INTERACTIVE`, `EMOTIVE`, `ADAPTIVE`, `CREATIVE`, `MOTIVE`) VALUES "

x = [user_id] + list(code_values.values())

user_id_output = x[0]
user_co_vals = [x[1],x[2],x[3],x[4],x[5],x[6],x[7]]
user_i_vals = [x[8],x[9],x[10],x[11],x[12],x[13],x[14]]
user_e_vals = [x[15],x[16],x[17],x[18],x[19],x[20],x[21]]
user_a_vals = [x[22],x[23],x[24],x[25],x[26],x[27],x[28]]
user_cr_vals = [x[29],x[30],x[31],x[32],x[33],x[34],x[35]]
user_m_vals = [x[36],x[37],x[38],x[39],x[40],x[42],x[42]]

co_sim = np.array(user_co_vals).dot(co_array_np).dot(np.array(h_array_to_v_array(user_co_vals)))
i_sim = np.array(user_i_vals).dot(i_array_np).dot(np.array(h_array_to_v_array(user_i_vals)))
e_sim = np.array(user_e_vals).dot(e_array_np).dot(np.array(h_array_to_v_array(user_e_vals)))
a_sim = np.array(user_a_vals).dot(a_array_np).dot(np.array(h_array_to_v_array(user_a_vals)))
cr_sim = np.array(user_cr_vals).dot(cr_array_np).dot(np.array(h_array_to_v_array(user_cr_vals)))
m_sim = np.array(user_m_vals).dot(m_array_np).dot(np.array(h_array_to_v_array(user_m_vals)))

user_1_vals = np.sqrt([co_sim[0] , i_sim[0] , e_sim[0], a_sim[0], cr_sim[0], m_sim[0]])
insert_query += "('"+str(user_id_output)+"', '"+str(user_1_vals[0])+"' , '"+str(user_1_vals[1])+"' , '"+str(user_1_vals[2])+"' , '"+str(user_1_vals[3])+"' , '"+str(user_1_vals[4])+"' , '"+str(user_1_vals[5])+"' );"

mycursor.execute(insert_query)

mydb.commit()
mydb.close()