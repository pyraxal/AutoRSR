def calculate_result(total_score, month, percentile=5):
    try:
        month = int(month)
        total_score = float(total_score)
    except ValueError:
        return "N/A"

    if month < 0:
        return "N/A"

    result = ""
    age = month // 12
    month = month % 12

    if age == 5:
        if 0 <= month <= 5:
            if percentile == 15 and total_score > 8.9:
                result = "Pass"
            elif percentile == 10 and total_score > 5.0:
                result = "Pass"
            elif percentile == 5 and total_score > 1.3:
                result = "Pass"
            else:
                result = "Fail"
        elif 6 <= month <= 11:
            if percentile == 15 and total_score > 9.0:
                result = "Pass"
            elif percentile == 10 and total_score > 8.0:
                result = "Pass"
            elif percentile == 5 and total_score > 3.95:
                result = "Pass"
            else:
                result = "Fail"

    elif age == 6:
        if 0 <= month <= 5:
            if percentile == 15 and total_score > 10.05:
                result = "Pass"
            elif percentile == 10 and total_score > 9.7:
                result = "Pass"
            elif percentile == 5 and total_score > 6.0:
                result = "Pass"
            else:
                result = "Fail"
        elif 6 <= month <= 11:
            if percentile == 15 and total_score > 16.0:
                result = "Pass"
            elif percentile == 10 and total_score > 14.0:
                result = "Pass"
            elif percentile == 5 and total_score > 12.0:
                result = "Pass"
            else:
                result = "Fail"

    elif age == 7:
        if 0 <= month <= 5:
            if percentile == 15 and total_score > 13.25:
                result = "Pass"
            elif percentile == 10 and total_score > 11.5:
                result = "Pass"
            elif percentile == 5 and total_score > 5.25:
                result = "Pass"
            else:
                result = "Fail"
        elif 6 <= month <= 11:
            if percentile == 15 and total_score > 19.0:
                result = "Pass"
            elif percentile == 10 and total_score > 16.0:
                result = "Pass"
            elif percentile == 5 and total_score > 14.1:
                result = "Pass"
            else:
                result = "Fail"

    elif age == 8:
        if 0 <= month <= 5:
            if percentile == 15 and total_score > 21.75:
                result = "Pass"
            elif percentile == 10 and total_score > 18.5:
                result = "Pass"
            elif percentile == 5 and total_score > 15.25:
                result = "Pass"
            else:
                result = "Fail"
        elif 6 <= month <= 11:
            if percentile == 15 and total_score > 20.1:
                result = "Pass"
            elif percentile == 10 and total_score > 18.4:
                result = "Pass"
            elif percentile == 5 and total_score > 15.7:
                result = "Pass"
            else:
                result = "Fail"

    elif age == 9:
        if 0 <= month <= 5:
            if percentile == 15 and total_score > 23.05:
                result = "Pass"
            elif percentile == 10 and total_score > 23.0:
                result = "Pass"
            elif percentile == 5 and total_score > 22.35:
                result = "Pass"
            else:
                result = "Fail"

    else:
        result = "N/A"

    return result

def score(a_list):
    sum = 0    
    for element in a_list:
        if element == 0:
            sum+=2
        elif element < 4:
            sum+=1    
    return sum


'''
Sample:
a_list = [2,2,2,1,0,2,1,1,2,2] #List of Raw Error Scores
print(calculate_result(score(a_list),60)) #Calulating the pass/fail
'''