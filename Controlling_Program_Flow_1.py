#Peyman Miyandashti 250161
#controlling program flow

# 1. Conditional statements(if,elif,else) make decisions in your code !

#learn about  Relational Operators or Comparison Operators :

########################################################################
# > (Greater Than),Checks if the value on the left is larger than the value on the right.
# 8 > 3 → True
########################################################################
# < (Less Than), Checks if the value on the left is smaller than the value on the right.
# 8 < 3 → False
########################################################################
# <= (Less Than or Equal To),Checks if the value on the left is smaller than or equal to the value on the right.
# 5 <= 3 → False
########################################################################
# >= (Greater Than or Equal To),Checks if the value on the left is larger than or equal to the value on the right.
#5 >= 5 → True
########################################################################
# == (equal to),Checks if two values are exactly the same. (Crucial: This is different from the assignment operator =)
# 5 == 5 → True
########################################################################
# != (not equal to), 	Checks if two values are not the same
#5 != 5 → False
########################################################################
# = is the assignment operator. It's used to assign a value to a variable.Example: x = 5 (This sets the variable x to hold the value 5)
# == is the equality operator. It's used to compare two values to see if they are equal.Example: if x == 5: (This checks if the value of x is equal to 5)
#######################################################################
#Examples of comparing variables

# 1. Greater Than (>) , Checks if the left value is larger than the right value.

a = 10
b = 3
result = a > b
print(result)  # Output: True
print(5 > 8)   # Output: False
#######################################################################
# 2. Less Than (<) , Checks if the left value is smaller than the right value.
a = 10
b = 3
result = a < b
print(result)  # Output: False
print(5 < 8)   # Output: True
#######################################################################
# 3. Less Than or Equal To (<=) ,Checks if the left value is smaller than or equal to the right value.
a = 10
b = 10
c = 5

print(c <= a)  # Output: True (because 5 is less than 10)
print(b <= a)  # Output: True (because they are equal)
print(a <= c)  # Output: False
#######################################################################
# 4. Greater Than or Equal To (>=) ,Checks if the left value is larger than or equal to the right value.


a = 10
b = 10
c = 5

print(a >= b)  # Output: True (because they are equal)
print(a >= c)  # Output: True (because 10 is greater than 5)
print(c >= a)  # Output: False
######################################################################
# 5. Equal To (==) , Checks if two values are exactly the same. This is different from = which is for assignment.

password = "secret123"
user_input = "secret123"

print(password == user_input)  # Output: True
print(10 == 10.0)             # Output: True (value is the same, type is different*)
print(10 == 5 + 5)            # Output: True (expression is evaluated first)

# *Note: In Python, 10 (int) and 10.0 (float) are considered equal by value with `==`.
# In some stricter languages like JavaScript, you'd use `===` to also check type.
#######################################################################
# 6. Not Equal To (!=) , Checks if two values are not the same.
user_role = "guest"
required_role = "admin"

print(user_role != required_role) # Output: True (user is NOT an admin)
print(10 != 10)                  # Output: False (they are the same)
#######################################################################
#Practical Example in a Function and return statement (In the function get_ticket_price(age), the return statement does two crucial things:
# 1.It immediately ends the function's execution. As soon as a return statement is run, the function stops. No other code in the function after that point will be executed.
# 2.It sends a value back to the line of code that called the function. This value ("$5", "$8", etc.) takes the place of the function call itself.
#so The return statement first  Exits the function immediately and Sends a value back to the caller.What we call it? Returning a value. The function is a value-returning function. Why it's used ? To compute a result inside a function and make that result available to the rest of your program.
########################################################################
#Example:
def get_ticket_price(age):
    """Determine ticket price based on age."""
    if age <= 12: # Less than or equal to 12
        return "$5"
    elif age < 18: # Less than 18 (but the under-12 case is already handled above)
        return "$8"
    elif age >= 65: # Greater than or equal to 65
        return "$10"
    else: # Everyone else (age 18 to 64)
        return "$12"

# Let's test the function
print(get_ticket_price(10))  # Output: $5  (<=12)
print(get_ticket_price(15))  # Output: $8  (<18)
print(get_ticket_price(35))  # Output: $12 (adult)
print(get_ticket_price(70))  # Output: $10 (>=65)
#####################################################################

a = 10
b = 20
print(a > b)   # Output: False
print(a < b)  # Output:  True
print(a <= b)  # Output: True
print(a >= b)  # Output: False
print(a == b)  # Output: False
print(a != b)  # Output: True
#######################################################################
# Here  are clear examples of if, elif, and else using all the major comparison operators
#1. Greater Than (>)
#Checks if the value on the left is smaller than the value on the right.

temperature = -5
if temperature < 0:
    print("It's freezing! Watch for ice.") # This will run
elif temperature < 15:
    print("It's a bit chilly. Wear a jacket.")
else:
    print("The weather is pleasant.")
#######################################################################
#2. Less Than (<)
#Checks if the value on the left is smaller than the value on the right.

temperature = -5
if temperature < 0:
    print("It's freezing! Watch for ice.") # This will run
elif temperature < 15:
    print("It's a bit chilly. Wear a jacket.")
else:
    print("The weather is pleasant.")
#######################################################################
#3. Less Than or Equal To (<=)
#Checks if the value on the left is smaller than or equal to the value on the right.
score = 90
passing_grade = 90

if score >= 95:
    grade = "A+"
elif score >= 90: # This condition is True (90 <= 90)
    grade = "A"   # This will run
elif score >= 80:
    grade = "B"
else:
    grade = "See teacher"

print(f"Your grade is: {grade}")#Output: Your grade is: A
#######################################################################
#4. Greater Than or Equal To (>=)
#Checks if the value on the left is larger than or equal to the value on the right.

discount_threshold = 100
cart_total = 120

if cart_total >= discount_threshold: # True (120 >= 100)
    print("You qualify for a discount!") # This will run
    final_total = cart_total * 0.9 # Apply 10% discount
    print(f"Your total after discount is ${final_total:.2f}")
else:
    print(f"Add ${discount_threshold - cart_total} more to your cart for a discount.")
    #Output:You qualify for a discount! Your total after discount is $108.00
#######################################################################
# 5. Equal To (==)
#Checks if two values are exactly the same.

password = "secret123"
user_input = "secret123"

if user_input == password: # True
    print("Access granted.") # This will run
elif user_input == "":
    print("Please enter a password.")
else:
    print("Access denied. Incorrect password.")#Output: Access granted.

########################################################################
#6. Not Equal To (!=)
#Checks if two values are not the same.

user_role = "moderator"

if user_role != "guest": # True ("moderator" is not "guest")
    print("You have access to post comments.") # This will run
else:
    print("Please create an account to comment.")

# Example with elif
favorite_pet = "cat"

if favorite_pet == "dog":
    print("Woof!")
elif favorite_pet != "cat": # This is False, so it's skipped
    print("You must like something else.")
else: # The 'catch-all' for any other condition
    print("Meow!") # This will run
#Output:You have access to post comments. Meow!
###################################################################
#def and function plus using all statements with if elif else return for and in at on program ! 

def analyze_grade(score, total_possible=100):
    """
    Analyzes a student's score and returns a detailed report.
    Uses all comparison operators and if/elif/else with return.
    """
    
    # Calculate percentage
    percentage = (score / total_possible) * 100
    
    # 1. Check for invalid score (using < and >)
    if score < 0:
        return "Error: Score cannot be negative!"
    elif score > total_possible:
        return "Error: Score exceeds the total possible points!"
    
    # 2. Check for perfect score (==)
    if percentage == 100:
        return "Perfect score! Outstanding!"
    
    # 3. Check for failing grade (<= and >=)
    if percentage <= 59:
        return f"Grade: F ({percentage:.1f}%). You must retake the exam."
    
    # 4. Main grade classification (multiple elifs with >= and <)
    if percentage >= 90:
        letter_grade = "A"
    elif percentage >= 80: # equivalent to: 80 <= percentage < 90
        letter_grade = "B"
    elif percentage >= 70:
        letter_grade = "C"
    elif percentage >= 60:
        letter_grade = "D"
    else:
        letter_grade = "F" # This else is redundant here but shown for example

    # 5. Add a plus/minus modifier (using multiple conditions)
    # Check for A+ (== 100 already handled above, so this is for high A)
    if letter_grade == "A" and percentage >= 97:
        modifier = "+"
    elif letter_grade == "A" and percentage <= 93:
        modifier = "-"
    # Check for other grades
    elif letter_grade != "F" and (percentage % 10) >= 7: # e.g., 87, 97
        modifier = "+"
    elif letter_grade != "F" and (percentage % 10) <= 3: # e.g., 83, 92
        modifier = "-"
    else:
        modifier = ""

    # 6. Check if they just passed (using == for exact threshold)
    if percentage == 60:
        message = "You just passed! Be careful next time."
    # Check if they barely missed the next grade (!= used in logic)
    elif (percentage + 1) >= (60 if letter_grade == "D" else 70 if letter_grade == "C" else 80 if letter_grade == "B" else 90):
        next_grade = "C" if letter_grade == "D" else "B" if letter_grade == "C" else "A" if letter_grade == "B" else "A+"
        message = f"So close! You were 1 point away from a {next_grade}."
    else:
        message = "Solid performance."

    return f"Grade: {letter_grade}{modifier} ({percentage:.1f}%). {message}"


# Let's test the function with various scores
test_scores = [105, -5, 100, 85, 67, 92, 60, 59, 72]

print("GRADE ANALYSIS RESULTS:")
print("=" * 50)

for score in test_scores:
    result = analyze_grade(score)
    print(f"Score {score}/100: {result}")

########################################################################
