#Peyman Miyandashti 250161
#Loop :  iterate over a sequence (like a list, string, or range) and execute a block of code for each item in that sequence.
#Basic syntax:
#Print numbers 0 to 4
for i in range (5):
    print(i)

#iterate through a list
fruits = ["apple","banana","cherry",]
for fruit in fruits:
    print(f"i like {fruit}".upper())

################################################
# Print numbers from 0 to 4
print("Counting up:")
for i in range(5): # range(5) is 0, 1, 2, 3, 4
    print(i)

# Print numbers from 3 to 7
print("\nCounting from 3 to 7:")
for i in range(3, 8): # range(start, stop) [stop is not included]
    print(i)

# Count even numbers from 2 to 10
print("\nEven numbers:")
for i in range(2, 11, 2): # range(start, stop, step)
    print(i)

# A practical example: Calculate the sum of numbers from 1 to 100
total = 0
for number in range(1, 101):
    total += number # Add each number to the total

print(f"\nThe sum of numbers from 1 to 100 is: {total}")
################################################################
#Iterating Over a String and Using enumerate()
#You can loop through each character in a string. The enumerate() function is a powerful tool that gives you both the index (position) and the value of each item.
message = "Hello"

# Loop through each character in the string
print("Each character:")
for char in message:
    print(char)

# Use enumerate() to get the index AND the character
print("\nEach character with its index:")
for index, char in enumerate(message):
    print(f"Index {index}: '{char}'")

# A more practical example: Find the positions of a specific letter
word = "banana"
letter_to_find = "a"
positions = [] # Create an empty list to store the positions

print(f"\nFinding the letter '{letter_to_find}' in '{word}':")
for index, char in enumerate(word):
    if char == letter_to_find:
        positions.append(index) # Add the index to the list
        print(f"Found '{letter_to_find}' at position {index}")

print(f"All positions: {positions}")
###################################################################
#while Loop : repeat as long as a condition is true. 
count = 5 
while count > 0:
    print(count)
    count-=1 #This is the same as count = count-1
print("blastoff")

