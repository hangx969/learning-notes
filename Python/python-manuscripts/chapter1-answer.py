
# 用户信息列表
users = []


def user_register():
    name = input("Please input name:")
    age = input("Please input age:")
    phone = input("Please input phone number:")

    if len(phone) != 11 or not phone.isdigit():
        print("Phone number should be 11 digits.")
        return

    user = {
        'name': name,
        'age': age,
        'phone': phone
    }
    users.append(user)
    print(f"User {name} registered successfully.")


def user_search():
    phone = input("Please enter phone number to search:")
    for user in users:
        if user['phone'] == phone:
            print(f"Found user {user['name']} whose phone number is {user['phone']}.")
            return
    print("User not found.")


def user_lists():
    if not users:
        print("No users registered.")
    for user in users:
        print(f"User name: {user['name']}, age: {user['age']}, phone number: {user['phone']}")


def main():
    while True:
        print("\n=====User management system=====")
        print("1. Register user")
        print("2. Search user")
        print("3. List all users")
        print("4. Exit system")

        choice = input("Please enter number to select function:")

        if choice == '1':
            user_register()
        elif choice == '2':
            user_search()
        elif choice == '3':
            user_lists()
        elif choice == '4':
            print("Existing...Thanks for using.")
            break
        else:
            print("Invalid input, please re-select.")

main()