"""
Created on Fri May 17 02:02:37 2021
Modified on Tue Mar 29 02:34
@author: Rishi Dey

Version: 4.0

DESCRIPTION : Generate top LP for B2C students based on their profile and subject chosen on B2C platform
Results stored on: `user_jobs`
"""
import pymysql
import statistics
import sys
from scipy import spatial
import numpy as np

######################### THRESHOLD #########################
threshold_safety = 57.2
threshold_likely = 44.7
max_safety = 0.5
min_safety = 0.2
max_likely = 0.6
min_likely = 0.3
min_reach = 0.2
######################### THRESHOLD #########################

if len(sys.argv) != 2:
    sys.exit('Argument Error\nCall it like\npython3 %s <user_id>' % sys.argv[0])

user_id = sys.argv[1]
str_id = str(user_id)

db = pymysql.connect(
                        user = "root",
                        host = "127.0.0.1",
                        db = "lifevitaenew",
                        password = "lifevitae",
                        use_unicode = True
                    )
cr = db.cursor()

temp = cr.execute('SELECT `COGNITIVE`, `INTERACTIVE`, `EMOTIVE`, `ADAPTIVE`, `CREATIVE`, `MOTIVE` FROM `chakra_score_each_users` WHERE `user_id` = %s', str_id)
if temp == 0:
    db.close()
    sys.exit('No chakra score is available for user_id = %s' % (str_id))

record = cr.fetchall()

user_values = []
count_non_zero = 0

for i in record[0]:
    user_values.append( float(i) )
    if i != 0:
        count_non_zero += 1

if count_non_zero == 0:
    db.close()
    sys.exit('Chakra score is entirely 0 for user_id = %s' % (str_id))

chakra_type = ['COGNITIVE', 'INTERACTIVE', 'EMOTIVE', 'ADAPTIVE', 'CREATIVE', 'MOTIVE']
strength = {}
strength['COGNITIVE'] = ['Problem Solving', 'Decisiveness', 'Originality', 'Simplifying the Complex', 'Connecting the Dots', 'Thinking ahead', 'Sense Making']
strength['INTERACTIVE'] = ['Collaborating', 'Valuing Relationships', 'Engagement', 'Diplomacy', 'Eloquence', 'Social Flexibility', 'Being Persuasive']
strength['EMOTIVE'] = ['Empathy', 'Self Awareness', 'Calmness', 'Trust', 'Patience', 'Gratitude', 'Compassion']
strength['ADAPTIVE'] = ['Resilience', 'Dealing with Adversity', 'Will Power', 'Self Discipline', 'Persistence', 'Humility', 'Agility']
strength['CREATIVE'] = ['Curiosity', 'Critical Thinking', 'Taking Risk', 'Entrepreneurship', 'Exploring', 'Pioneering', 'Challenging the Norm']
strength['MOTIVE'] = ['Drive', 'Passion', 'Confidence', 'Integrity', 'Dependability', 'Objectivity', 'Sense of Purpose']

temp = cr.execute('SELECT `subject_1`, `subject_2`, `subject_3`, `subject_4`, `subject_5`, `subject_6` FROM `user_b2c_elective` WHERE `user_id` = %s', (str_id))
if temp == 0:
    db.close()
    sys.exit('No entry in `user_b2c_elective` for user_id = %s' % (str_id))

record = cr.fetchall()

elective_ids = ','.join( map(str, filter(lambda temp: temp != None, record[0]) ))

if elective_ids == '':
    db.close()
    sys.exit('No proper subject entry in `user_b2c_elective` for user_id = %s' % (str_id))

query = 'SELECT `job_ids`, `top_job_ids` FROM `b2c_elective` WHERE `id` IN (' + elective_ids + ')'
_ = cr.execute(query)
record = cr.fetchall()

temp = set()
current_top_job_ids = set()

for i in record:
    temp = temp.union( set(i[0].split(',')) )
    if i[1] == '' or i[1] == None:
        continue
    current_top_job_ids = current_top_job_ids.union( set(i[1].split(',')) )


current_top_job_ids = list( map(str, current_top_job_ids) )
temp = temp.union(current_top_job_ids)
job_ids = ','.join(temp)

query = 'SELECT `id`, `COGNITIVE`, `INTERACTIVE`, `EMOTIVE`, `ADAPTIVE`, `CREATIVE`, `MOTIVE`, `top_chakra` FROM `job_details` WHERE `id` IN (' + job_ids + ');'
_ = cr.execute(query)
record = cr.fetchall()

job_similarity_score = {}
job_chakra_values = {}
job_record_top_chakra = {}
maxx = 0
avg = 0.0
old_job_similarity_score = {}

for i in record:
    temp = list(map(float, i[1: 7]))
    x = (1 - spatial.distance.cosine(temp , user_values)) * 78
    job_similarity_score[ int(i[0]) ] = x
    job_chakra_values[ int(i[0]) ] = temp
    job_record_top_chakra[ int(i[0]) ] = i[7]

len_record = len(record)
max_safety = round(max_safety * len_record)
min_safety = round(min_safety * len_record)
max_likely = round(max_likely * len_record)
min_likely = round(min_reach * len_record)
min_reach = round(min_reach * len_record)

count_safety = 0
count_likely = 0
count_reach = 0

maxx = max(job_similarity_score.values())

# 0-25th, 1-50th, 2-75th percentile
#avg = statistics.quantiles(job_similarity_score.values())[2]

# Using 75th percentile
avg = np.percentile( list(job_similarity_score.values()) , 75)

x = (maxx - avg) / 5.0

for i in record:
    y = int(i[0])
    if str(i[0]) in current_top_job_ids:
        old_job_similarity_score[y] = job_similarity_score[y]    
        job_similarity_score[y] = maxx + ((job_similarity_score[y] - avg) / x)
    
    z = job_similarity_score[y]
    if z >= threshold_safety:
        count_safety += 1
    elif z >= threshold_likely:
        count_likely += 1
    else:
        count_reach += 1

# Experimental, can also be done using If, but may not always work
if count_safety > max_safety:
    count_likely += (count_safety - max_safety)
    count_safety = max_safety

while count_safety < min_safety and count_likely > min_likely:
    count_safety += 1
    count_likely -= 1

while count_likely < min_likely and count_safety > 0 and count_reach > 0:
    count_likely += 1
    if count_safety > count_reach:
        count_safety -= 1
    else:
        count_reach -= 1

while (count_reach < min_reach or count_likely > max_likely) and count_likely > 0:
    count_likely -= 1
    count_reach += 1

job_similarity_score_sort = sorted(job_similarity_score.items(), key = lambda x: x[1], reverse = True)
count = 0

_ = cr.execute('DELETE FROM `user_jobs` WHERE `user_id` = %s;', str_id)
flag = cr.execute('SELECT `strengths` FROM `user_unlocked_life_strengths` WHERE `user_id` = %s;', str_id)
if flag == 0:
    db.close()
    sys.exit('No strength is unlocked for user_id = %s' % (str_id))

record = cr.fetchall()
strengths_unlocked = [ i[0] for i in record ]

query = 'INSERT INTO `user_jobs` (`user_id`, `job_id`, `percentage_similarity`, `strength`, `develop_strength`, `id_user_achievements`, `id_user_passion`, `id_user_moment`, `lp_level`, `created_at`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());'

for i in job_similarity_score_sort:
    index = int(i[0])
    top_strengths = ''
    develop_strength = ''

    temp = list(map(int, job_record_top_chakra[ index ].split(',') ))

    freq_strength = [0] * 6
    different_values = [0] * 6
    count_can_be_changed = 0

    for k in temp:
        ratio = user_values[k] / job_chakra_values[ index ][k]
        new_user_value = [ max(ratio * job_chakra_values[index][l], user_values[l]) for l in range(6) ]
        new_similarity_score = (1 - spatial.distance.cosine(job_chakra_values[index] , new_user_value) ) * 100
        if index in old_job_similarity_score:
            if new_similarity_score <= old_job_similarity_score[index]:
                continue
        else:
            if new_similarity_score <= i[1]:
                continue

        count_can_be_changed += 1

        for l in range(6):
            if new_user_value[l] > user_values[l]:
                freq_strength[l] += 1
                different_values[l] += new_user_value[l] - user_values[l]

    count_develop_strength = 0

    for l in freq_strength:
        if freq_strength[l] / count_can_be_changed < 0.67:
            different_values[l] = 0

    different_values_score = [(j, different_values[j]) for j in range(6)]
    different_values_score = sorted(different_values_score, key = lambda x:x[1], reverse = True)

    for l in different_values_score:
        chakra = chakra_type[l[0]]
        for k in strength[chakra]:
            if k not in strengths_unlocked:
                develop_strength = develop_strength + k + ','
                count_develop_strength += 1
            if count_develop_strength >= 6:
                break
        if count_develop_strength >= 6:
            break

    if count_develop_strength < 5:
        chakra = chakra_type[ different_values_score[0][0] ]
        for k in strength[chakra]:
            if k not in develop_strength:
                develop_strength = develop_strength + k + ','
                count_develop_strength += 1
            if count_develop_strength >= 6:
                break

    score = [ (j, user_values[j] * job_chakra_values[ index ][j]) for j in temp ]
    
    score = sorted(score, key = lambda x: x[1], reverse = True)

    top_range = 2
    for j in score[:top_range]:
        chakra = chakra_type[ j[0] ]
        for k in strength[chakra]:
            if k in strengths_unlocked:
                top_strengths = top_strengths + k + ','

    top_strengths = top_strengths[:-1]

    develop_strength = develop_strength[:-1]

    set_top_strengths = set(top_strengths.split(','))
    set_develop_strength = set(develop_strength.split(','))

    _ = cr.execute('SELECT `id`, `type`, `strength` FROM `user_achievements` WHERE `user_id` = %s;', str_id)
    record = cr.fetchall()
    id_user_achievement = ''
    id_user_passion = ''
    for j in record:
        if j[2] in set_top_strengths:
            if j[1] == 0:
                id_user_passion = id_user_passion + str(j[0]) + ','
            else:
                id_user_achievement = id_user_achievement + str(j[0]) + ','

    id_user_achievement = id_user_achievement[:-1]
    id_user_passion = id_user_passion[:-1]

    _ = cr.execute('SELECT `answers`.`id`, `strength` FROM `answers` INNER JOIN `question_details` ON `question_details`.`question_id` = `answers`.`question_id` WHERE `user_id` = %s;', str_id)
    record = cr.fetchall()
    id_user_moment = ''
    for j in record:
        k = set( j[1].split(',') )
        if set_top_strengths.intersection(k) == set():
            continue
        id_user_moment = id_user_moment + str(j[0]) + ','

    id_user_moment = id_user_moment[:-1]

    percentage_similarity = round(i[1])

    if count < count_safety:
        lp_level = 'Safety'
    elif count < count_safety + count_likely:
        lp_level = 'Likely'
    else:
        lp_level = 'Reach'

    cr.execute(query, (str_id, str(i[0]), str(percentage_similarity), str(top_strengths), str(develop_strength), str(id_user_achievement), str(id_user_passion), str(id_user_moment), lp_level))
    count += 1

db.commit()
db.close()