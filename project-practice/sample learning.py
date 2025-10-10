# numbers = [1, 1, 1, 1, 5]
# for x_count in numbers:
#     output = ""
#     for count in range (x_count):
#         output += "x"
#     print(output)

# for num in numbers:
#     print("x" * num)

# numbers = [3, 6, 2, 8, 4, 10]
# max = numbers[0]
# for number in numbers:
#     if number > max:
#         max = number
# print(max)

# numbers = [3, 3, 6, 2, 2 ,6, 3, 10]
# unique_list = []

# for number in numbers:
#     if number not in unique_list:
#         unique_list.append(number)

# print(unique_list) 

# phone = input("Phone: ")
# num = {
#       "1" : "One",
#       "2" : "Two",
#       "3" : "Three",
#       "4" : "Four"
# }
# output = ""
# for i in phone:
#     output += num.get(i, "!") + " "
# print(output)


# def emoji_converter(message):
#     words = message.split(' ')
#     emojis = {
#         ":)" : "😊",
#         ":(" : "😔"
#     }
#     output = ""
#     for word in words:
#         output += emojis.get(word, word) + " "
#     return output


# message = input(">:")
# print(emoji_converter(message))


# from utils import find_max

# numbers = [3, 6, 2, 8, 4, 10]
# print(find_max(numbers))

# import random

# play_again = True

# while play_again:

#     number_of_dice = int(input("Choose how many dice to roll: "))
#     dice = []
#     total = 0

#     class Dice():

#         def roll(number_of_dice):
#             for die in range(number_of_dice):
#                 dice.append(random.randint(1, 6))
#             return dice

#         print(roll(number_of_dice))

#     Dice()


#     while True:
#         playing = input("Do you want to play again? (y/n): ").lower()

#         if playing == "y":
#             break
#         elif playing == "n" :
#             print("Thanks for playing!")
#             exit()
#         else:
#             print("Invalid option, type only y or n")
            
import random

def roll_dice(num_dice):
    return [random.randint(1, 6) for _ in range(num_dice)]

def play_game():
    while True:
        try:
            num = int(input("Choose how many dice to roll: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    results = roll_dice(num)
    print("You rolled:", results)

def ask_to_play_again():
    while True:
        answer = input("Do you want to play again? (y/n): ").lower()
        if answer == "y":
            return True
        elif answer == "n":
            print("Thanks for playing!")
            return False
        else:
            print("Invalid option, type only y or n.")

# Main loop
while True:
    play_game()
    if not ask_to_play_again():
        break