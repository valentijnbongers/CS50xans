import random


def bubble_sort(Array, category):
        for i in range(0, len(Array)):
            for j in range(0, len(Array) - i - 1):
                if Array[j][category] > Array[j + 1][category]:
                    Array[j], Array[j + 1] = Array[j + 1], Array[j]
        return Array

CountriesArray = [{"name": "Andorra", "capital" : "Andorra La Vella", "population" : 84000, "area" : 468.0},
                  {"name": "Netherlands", "capital" : "Amsterdam", "population" : 16645000, "area" : 41526.0},
                  {"name": "Falkland Islands", "capital" : "Stanley", "population" : 2638, "area" : 12173.0}]
#CountriesArray = bubble_sort(CountriesArray, "population")
#print(CountriesArray)



def convert_to_number(value):
    """Convert scientific notation (e.g., '1.71E7') or numeric strings to float or int."""
    try:
        num = float(value)  # Convert to float first
        return int(num) if num.is_integer() else num  # Convert to int if no decimals
    except (ValueError, TypeError):
        return value

print(convert_to_number("11000.7"))

index = random.randint(0, len(CountriesArray)-1)
print(index)
