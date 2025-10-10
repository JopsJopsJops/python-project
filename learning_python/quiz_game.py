print ("Welcome to my computer quiz!")

playing = input("Do you want to play? ")

if playing.lower() != "yes":
    print("Bye")
    quit()

print("Okay! Let's play :)")
score = 0
total_question = 0

answer = input("What does CPU stands for? ").lower()
total_question += 1
if answer == "central processing unit":
    print("Correct!")
    score += 1
else:
    print("Incorrect!")

answer = input("What does GPU stands for? ").lower()
total_question += 1
if answer == "graphics processing unit":
    print("Correct!")
    score += 1
else:
    print("Incorrect!")

answer = input("What does RAM stands for? ").lower()
total_question += 1
if answer == "random access memory":
    print("Correct!")
    score += 1
else:
    print("Incorrect!")

answer = input("What does PSU stands for? ").lower()
total_question += 1
if answer == "power supply unit":
    print("Correct!")
    score += 1
else:
    print("Incorrect!")

print(f"You got {score} out of {total_question }questions correct!")
print(f"You got {(score / total_question) * 100:.2f}%")




