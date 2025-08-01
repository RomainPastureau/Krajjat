from datetime import datetime as dt

unit_dict = {"a": 478, "b": 239, "c": 78166, "d": 2.69, "e": 478.6, "f": 12.3, "g": 7.3, "h": 4.89}
unique_labels = []

time_before = dt.now()

for i in range(100000):
    for key in unit_dict.keys():
        if key not in unique_labels:
            unique_labels.append(key)

print(unique_labels)
print("Time taken: " + str(dt.now() - time_before))

unique_labels = {}

time_before = dt.now()

for i in range(100000):
    for key in unit_dict.keys():
        if key not in unique_labels:
            unique_labels[key] = None

print(list(unique_labels.keys()))
print("Time taken: " + str(dt.now() - time_before))

unique_labels = {}

time_before = dt.now()

for i in range(100000):
    for key in unit_dict.keys():
        unique_labels[key] = None

print(list(unique_labels.keys()))
print("Time taken: " + str(dt.now() - time_before))

