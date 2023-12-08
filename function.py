# Import all installs
# import excel file data

import pandas as pd
import openpyxl
import numpy as np
import tellurium as te

def get_data(excel_file):
    """
    acquired data from spreadsheet file
    args:
        excel_file: str
    returns:
        array of float (COD)
        array of float (BOD)
    """
    df = pd.read_excel(excel_file)
    #Select methane potential data
    #This part is testing how to select specific column
    COD = df['COD'].values
    BOD = df['BOD'].values
    return COD,BOD

#excel_file = 'Reactor 1.xlsx'
#df = pd.read_excel(excel_file)
#print(df)

#Select methane potential data
#This part is testing how to select specific column
#COD = df['COD']
#BOD = df['BOD']
COD,BOD = get_data("Reactor 1.xlsx")

def methane_production(BOD):
    """
    calculating methane production from BOD
    args:
        BOD: array of float
    returns:
        array of float (methane)
    """
    # 0.35 is because 1g of COD = 0.35L methane.
    methane_production = np.array([bod * 0.35 for bod in BOD])
    return methane_production

def get_data_for_Bunsen_coefficient(excel_file):
    """
    acquired data from spreadsheet file
    args:
        excel_file: str
    returns:
        array of float (temperature)
        array of float (salinity)
    """
    df = pd.read_excel(excel_file)
    #Select methane potential data
    #This part is testing how to select specific column
    Temperature = df['temperature ave'].values
    Salinity = df['Salinity %'].values
    return Temperature,Salinity

Temperature,Salinity = get_data_for_Bunsen_coefficient("Reactor 1.xlsx")
#print("check salinity")
#print(type(Salinity)) 

def Temperature_conversion(Temperature):
    """
    calculating temperature conversion from temperature
    args:
        Temperature: array of float
    returns:
        array of float (temperature_kelvin)
    """
    Temperature_conversion = np.array([temperature + 273.15 for temperature in Temperature])
    return Temperature_conversion

# Call the Temperature_conversion function with the Temperature data
# This line is necessary because it calls the Temperature_conversion function and stores the result in a new variable (converted_temperature).
converted_temperature_values = Temperature_conversion(Temperature)
# Ensure converted_temperature_values is a NumPy array
converted_temperature_np = np.array(converted_temperature_values)

def Bunsen_coefficient(salinity, converted_temperature_np):
    """
    A function that takes salinity (numpy.ndarray) and temperature (numpy.ndarray) as input. 
    Calculate Bunsen coefficient based on temperature and salinity.

    Args:
        salinity (numpy.ndarray): Array of salinity values.
        converted_temperature_np (numpy.ndarray): Array of Temperature (Kelvin) values.

    Returns:
        numpy.ndarray: Calculated Bunsen coefficient.
    """
    #print("salinity type:", type(salinity))
    #print("converted_temperature_np type:", type(converted_temperature_np))
    #print("converted_temperature_np shape:", converted_temperature_np.shape)

    Bunsen_coefficient = np.exp(
        -67.1962 + 99.1624 * (100 / converted_temperature_np) +
        27.9015 * np.log(converted_temperature_np / 100) +
        salinity * (-0.072909 + 0.041674 * (converted_temperature_np / 100) - 0.0064603 * ((converted_temperature_np / 100) ** 2))
    )
    return Bunsen_coefficient
result_of_Bunsen_coefficient = Bunsen_coefficient(Salinity, converted_temperature_np)
result_of_Bunsen_coefficient_input = np.array(result_of_Bunsen_coefficient)
#print(type(result_of_Bunsen_coefficient))

def dissolved_methane(result_of_Bunsen_coefficient_input,methane_production):
#Combine Bunsen coefficient and calculate dissolved methane (ml CH4/ ml water)
    """
    calculating dissolved_methane from Bunsen_coefficient and methane_production
    args:
        result_of_Bunsen_coefficient: array of float
        methane_production: array of float
    returns:
        array of float (dissolved_methane)
    """
    dissolved_methane = result_of_Bunsen_coefficient_input * methane_production
    return dissolved_methane

# Calculate the molar concentration of dissolved methane in the liquid. Ideal gas equation is used. 
def molar_dissolved_methane(dissolved_methane, converted_temperature):
    """
    calculating molar_dissolved_methane from dissolved_methane
    args:
        dissolved_methane: array of float
        temperature_kelvin: array of float
    returns:
        array of float (molar_dissolved_methane)
    """
    molar_dissolved_methane = dissolved_methane / (0.082 * converted_temperature)
    return molar_dissolved_methane
# In the ideal gas equation, 1 atm of reactor headspace pressure is assumed. 
# The unit of molar_dissolved_methane is now mmol/L of methane
# Give suggestion if we should use N-DAMO process:
def check_N_DAMO_process(minimum_DM_value):
    """
    Check if N-DAMO process exists based on the minimum value in the DM array.

    Args:
        minimum_DM_value: float.

    Returns:
        str: Message indicating the existence of the N-DAMO process.
    """
    if minimum_DM_value > 1:
        return "N-DAMO process exists."
    else:
        return "N-DAMO process does not exist."
    
# Example usage:
# Get the required data from the Excel file
COD, BOD = get_data("Reactor test.xlsx")
Temperature, Salinity = get_data_for_Bunsen_coefficient("Reactor test.xlsx")

# Calculate relevant parameters using your functions
methane_production_values = methane_production(BOD)
converted_temperature_values = Temperature_conversion(Temperature)
bunsen_coefficient_values = Bunsen_coefficient(Salinity, converted_temperature_values)
dissolved_methane_values = dissolved_methane(bunsen_coefficient_values, methane_production_values)
molar_dissolved_methane_values = molar_dissolved_methane(dissolved_methane_values, converted_temperature_values)

# Calculate minimum DM value
minimum_DM_value = np.min(molar_dissolved_methane_values)

# Check if N-DAMO process exists based on the calculated minimum DM value
result = check_N_DAMO_process(minimum_DM_value)
print("N-DAMO Process Check Result:", result)

def DM_inf(minimum_DM_value):
    """
    Calculate different ratio of wastewater by using the minimum value in the DM array 

    Args:
        minimum_DM_value: float.

    Returns:
        float: calculated minimum value in the DM array.
    """
    # Adjust wastewater ratio 
    ratio = 0.3 
    DM_inf_value = minimum_DM_value * ratio
    return DM_inf_value
DM_inf_value = DM_inf(minimum_DM_value)
print("DM influent value:", DM_inf_value)

model_str = f"""
CH4 + NO3 -> NO2; k1*(14/4)*NO3/(k2+NO3)
CH4 + NO2 -> N2; (8/3)*CH4/(CH4+k3)*NO2/(NO2+k4)
#k1 is N-DAMO archaea rate constant, k2 is N-DAMO archaea nitrate affinity
#k3 is N-DAMO bacteria methane affinity, k4 is N-DAMO bacteria nitrite affinity
k1 = 0.019
k2 = 0.15
k3 = 0.092
k4 = 0.91
CH4 = {DM_inf_value}  # Assigning the calculated DM_inf_value to CH4
NO3 = 2.5
NO2 = 0
"""

def plot_model(model_str):
    """
    Creates a roadrunner object and plots the model.

    Parameters
    ----------
    model_str: str
    """
    rr = te.loada(model_str)
    data = rr.simulate(0, 24, 200)
    rr.plot(data, title="N-DAMO process")

# N-DAMO test
plot_model(model_str)


