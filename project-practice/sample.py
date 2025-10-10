# def double_and_return(x):
#     return x * 2

# result = double_and_return(5)
# print(result)

# def double_and_print(x):
#     print(x * 2)

# result = double_and_print(5)
# print(result)

# def triple_and_display(x):
#     tripled_value = 3 * x
#     print(f"Tripled value is: {tripled_value}")
#     return tripled_value

# result = triple_and_display(5)
# print(f"Stored result: {result}")

# score = int(input("Your test score: "))
# def check_pass(score):
#     if score >= 75:
#         print("You passed!")
#         return "Pass"
#     else:
#          print("You failed!")
#          return "Fail"
    

# result = check_pass(score)
# print(f"Result: {result}")

# score = int(input("Enter your score: "))
# def get_grade(score):
#     if score < 0 or score > 100:
#         print("Invalid. Grade should not be above 100")
#         return "Invalid"
#     elif score >= 90:
#         print("Grade: A")
#         return "A"
#     elif score >= 80:
#         print("Grade: B")
#         return "B"
#     elif score >= 70:
#         print("Grade: C")
#         return "C"
#     elif score >= 60:
#         print("Grade: D")
#         return "D"
#     else:
#         print("Grade: F")
#         return "F"

        
# result = get_grade(score)
# print(f"Returned grade: {result}")


def grade_summary_and_average(score_to_enter):
    scores = []
    for score in range(score_to_enter):
            enter_score = int(input(f"Enter score#{score + 1} "))
            scores.append(enter_score)
    print(f"Your scores are: {scores}")
    return scores

def calculate_average(scores):
        total_grade = sum(scores) / len(scores)
        print (f"Average score is : {total_grade:.2f}")
        return total_grade
        
def get_grade(total_grade):
    if total_grade < 0 or total_grade > 100:
        print("Invalid. Grade should not be above 100")
        return "Invalid"
    elif total_grade >= 90:
        print("Grade: A")
        return "A"
    elif total_grade >= 80:
        print("Grade: B")
        return "B"
    elif total_grade >= 70:
        print("Grade: C")
        return "C"
    elif total_grade >= 60:
        print("Grade: D")
        return "D"
    else:
        print("Grade: F")
        return "F"

score_to_enter = int(input("How many scores you want to enter?: "))    
scores = grade_summary_and_average(score_to_enter)
average = calculate_average(scores)
result = get_grade(average)
print(f"Returned grade: {result}")