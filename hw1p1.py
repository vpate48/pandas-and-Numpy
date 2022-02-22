import pandas as pd
import numpy as np

# Question 1.1

def extract_hour(time):
    """
    Extracts hour information from military time.
    
    Args: 
        time (float64): array of time given in military format.  
          Takes on values in 0.0-2359.0 due to float64 representation.
    
    Returns:
        array (float64): array of input dimension with hour information.  
          Should only take on integer values in 0-23
    """
    # Replace NaN for all invalid values
    search = time.where(time <= 2359.0)
    search = search.where(search >= 0.0)
    
    # This replaces the valid values to the hour format
    replace = search.where(search > 2359.0, search//100.0)
    
    # Verify that all of the replaced values are valid
    answer = replace.where(replace <= 23.0)
    answer = answer.where(answer >= 0)
    
    #finally return the answer
    return answer 
    
def extract_mins(time):
    """
    Extracts minute information from military time
    
    Args: 
        time (float64): array of time given in military format.  
          Takes on values in 0.0-2359.0 due to float64 representation.
    
    Returns:
        array (float64): array of input dimension with hour information.  
          Should only take on integer values in 0-59
    """
    # Replace NaN for all invalid values
    #search = time.where(time <= 2359.0)
    search = time.where(time >= 0.0)
    
    replace = search.where(search > 10000.0, search %100)
    
    # Verify that all of the replaced values are valid
    answer1 = replace.where(replace <= 59.0)
    answer1 = answer1.where(answer1 >= 0)
    print(time)
    print(answer1)
    
    #finally return the answer
    return answer1

    
 

# Question 1.2

def convert_to_minofday(time):
    """
    Converts military time to minute of day
    
    Args:
        time (float64): array of time given in military format.  
          Takes on values in 0.0-2359.0 due to float64 representation.
    
    Returns:
        array (float64): array of input dimension with minute of day
    
    Example: 1:03pm is converted to 783.0
    >>> convert_to_minofday(1303.0)
    783.0
    """
    # This replaces the valid values to the minutes format
    replace = extract_hour(time)*60
    replace = replace + extract_mins(time)
    
    
    #finally return the answer
    return replace
    
    
def calc_time_diff(x, y):
    """
    Calculates delay times y - x
    
    Args:
        x (float64): array of scheduled time given in military format.  
          Takes on values in 0.0-2359.0 due to float64 representation.
        y (float64): array of same dimensions giving actual time
    
    Returns:
        array (float64): array of input dimension with delay time
    """
    scheduled = convert_to_minofday(x)
    actual = convert_to_minofday(y)
    
    return actual - scheduled

    ### write code to test your functions here and execute it. 
    ### your printed results should show the values of the following two variables

    #delay = pd.Series([1203, 1310, 1300, 110, 1350], dtype='float64')
    delay = calc_time_diff(flights['sched_dep_time'], flights['actual_dep_time'])
    delayed15 = pd.DataFrame(flights.loc[i,:] for i, val in enumerate(delay) if val >= 15)
    #delayed15 = pd.Series([1210, 1350, 1259, 100, 1375], dtype='float64')
    print(delay)
    print(delayed15)
    
    delayed_airports = delayed15[delayed15['origin'].isin(["SFO", "OAK"])]
    delayed_destinations = delayed_airports['destination'].sort_values(ascending=True).drop_duplicates()
    delayed_destinations
