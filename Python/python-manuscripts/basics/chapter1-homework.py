

def user_register():

    user_data = []

    while True:

        # Input name
        name = input("Enter name (type exit to quit): ")
        if name == "exit":
            break

        # Input age
        age = input("Enter age (type exit to quit): ")
        if age == "exit":
            break

        # Input phone number
        phone = input("Enter phone number (type exit to quit): ")
        if phone == "exit":
            break
        # Validate phone number
        if not (phone.isdigit() and len(phone) == 11):
            print("Invalid phone number. Please enter an 11-digit number.")
            continue

        # Register user data to the list
        user_data.append({
            "name": name,
            "age": age,
            "phone": phone
        })

    return user_data


def find_user_by_phone(phone, user_data):

    for user in user_data:
        if user["phone"] == phone:
            return user

    return None


def print_user_list(user_data):

    print("Registered Users:")

    for user in user_data:
        print(f"Name: {user['name']}, Age: {user['age']}, Phone: {user['phone']}\n")

# register users from input
user_data = user_register()

# find user by phone number
while True:
    phone_to_find = input("Enter phone number to find user (enter exit to quit): ")

    if phone_to_find == "exit":
        break

    if not (phone_to_find.isdigit() and len(phone_to_find) == 11):
        print("Invalid phone number. Please enter an 11-digit number.")
        continue

    found_user = find_user_by_phone(phone_to_find, user_data)

    if found_user:
        print("User found:")
        print(f"Name: {found_user['name']}, Age: {found_user['age']}, Phone: {found_user['phone']}")
    else:
        print("User not found.")

# print all registered users
print_user_list(user_data)


