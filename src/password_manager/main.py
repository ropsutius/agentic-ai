import json, os, base64
from crypto import derive_key, encrypt, decrypt, generate_secure_password
from utils import log_update
from database import read_passwords, write_passwords
from auth import hash_password, verify_password


def main():
    if os.path.exists("master_login.json"):
        with open("master_login.json", 'r') as file:
            master_login = json.load(file)

    while True:
        # Create a more visually appealing header
        print("="*40)
        print(f"{'Welcome to the Password Manager'.center(40)}")
        print("="*40)

        # User login
        uid = input("Enter your UID: ")
        if uid not in master_login:
            print("\n[!] User not found.\n")
            continue

        pss = input("Enter your password: ")
        if not verify_password(pss, master_login[uid]):
            print("\n[!] Password mismatch.\n")
            continue

        key = derive_key(pss, b"salt")

        # updating the log for an user login
        log_update(f"User {uid} has logged-in")

        # Success message with stylized heading
        print("*"*40)
        print(f"{f'Login successful - Welcome {uid}'.center(40)}")
        print("*"*40)

        # Menu for actions
        while True:
            print("\nSelect an option:")
            print("+"*40)
            print("1. Add Password")
            print("2. Retrieve Password")
            print("3. Update Password")
            print("4. Delete Password")
            print("9. Exit")
            print("+"*40)

            choice = input("Choose an option: ")

            if choice == "1":
                add_password(uid, key)
            elif choice == "2":
                retrieve_password(uid, key)
            elif choice == "3":
                update_password(uid, key)
            elif choice == "4":
                delete_password(uid)
            elif choice == "9":
                print(f"\n[!] Exiting the Password Manager. Stay safe! - {uid}")
                break
            else:
                print("\n[!] Invalid option. Please try again.\n")

        # End message
        print("="*40)
        print(f"{'Thank you for using the Password Manager!'.center(40)}")
        print("="*40)
        break  # Break the while loop to exit after finishing tasks.

def add_password(uid, key):
    # Read the stored passwords from the file
    app_password = read_passwords()

    # Prompt user to enter domain and password
    print("="*40)
    print(f"{'Add Password'.center(40)}")
    print("="*40)

    domain = input("Enter the domain name: ")
    print(f"<======  If you wish to generate a random password, leave the password field as blank. ======>")
    password = input("Enter the password for the domain: ")

    # Generating a random password if the user has not provided the password
    if password == "":
      length = int(input("Enter the length of the password you would like to use: "))
      password = generate_secure_password(length)

    # Check if the user exists in app_password; if not, initialize an empty list for them
    if uid not in app_password:
        app_password[uid] = []

    encrypted_password = base64.b64encode(encrypt(key, password)).decode("utf-8")

    # Create a new password entry
    new_entry = { "domain": domain, "pwd": encrypted_password }

    # Append the new entry to the user's password list
    app_password[uid].append(new_entry)

    # Write the updated password list back to the file
    write_passwords(app_password)

    # Log the action for tracking purposes
    log_update(f"Added password for {domain} under user {uid}")

    # Print success message with a decorative format
    print("*"*40)
    print(f"Password for {domain} has been added successfully.")
    print("*"*40)

def retrieve_password(uid, key):
    # Read the stored passwords from the file
    app_password = read_passwords()

    # Check if the user exists and has stored passwords
    if uid in app_password and app_password[uid]:
        print("="*40)
        print(f"{'Stored Passwords'.center(40)}")  # Title centered
        print("="*40)

        # Enumerate through the list of stored passwords and display the domains
        for index, entry in enumerate(app_password[uid], 1):
            print(f"{index}. {entry['domain']}")  # List the domain name (website)

        # Allow the user to select an option to view a specific password
        try:
            choice = int(input("\nEnter the option number to display the password: "))

            # Validate the user's choice
            if 0 < choice <= len(app_password[uid]):
                selected_entry = app_password[uid][choice - 1]
                decrypted_password = decrypt(key, base64.b64decode(selected_entry['pwd'].encode("utf-8")))

                # Display the selected password details with decorative formatting
                print("*"*40)
                print(f"Password for {selected_entry['domain']} ==> {decrypted_password}")
                print("*"*40)
                # Log the password retrival
                log_update(f"Retrieved password for {selected_entry['domain']} under user {uid}")

            else:
                # Invalid option if the choice is out of range
                print("\n[!] Invalid option selected. Please choose a valid number.\n")

        except ValueError:
            # Error message if the user does not input a valid integer
            print("\n[!] Please enter a valid number.\n")

    else:
        # If no passwords are stored or user is not found
        print("\n[!] No passwords stored or user not found.\n")

def update_password(uid, key):
    # Read the stored passwords from the file
    app_password = read_passwords()

    # Check if the user exists and has stored passwords
    if uid in app_password and app_password[uid]:
        print("="*40)
        print(f"{'Stored Passwords'.center(40)}")  # Title centered
        print("="*40)

        # Enumerate through the list of stored passwords and display the domains
        for index, entry in enumerate(app_password[uid], 1):
            print(f"{index}. {entry['domain']}")  # Display domain name

        # Allow the user to select an option to update a specific password
        try:
            choice = int(input("\nEnter the option number to update the password: "))

            # Validate if the choice is within the valid range
            if 0 < choice <= len(app_password[uid]):
                selected_entry = app_password[uid][choice - 1]

                # Prompt the user for the new password
                print(f"<======  If you wish to generate a random password, leave the password field as blank. ======>")
                new_password = input(f"Enter the new password for {selected_entry['domain']}: ")

                # Generating a random password if the user has not provided the password and updating it
                if new_password == "":
                    length = int(input("Enter the length of the password you would like to use"))
                    new_password = generate_secure_password(length)

                encrypted_password = base64.b64encode(encrypt(key, new_password)).decode("utf-8")
               
                selected_entry['pwd'] = encrypted_password

                # Write the updated passwords back to the file
                write_passwords(app_password)

                # Log the password update
                log_update(f"Updated password for {selected_entry['domain']} under user {uid}")

                # Provide success feedback to the user
                print("*"*40)
                print(f"Password for {selected_entry['domain']} updated successfully.")
                print("*"*40)

            else:
                # Handle invalid selection
                print("\n[!] Invalid option selected. Please choose a valid number.\n")

        except ValueError:
            # Handle non-integer input
            print("\n[!] Please enter a valid number.\n")

    else:
        # If no passwords are stored or user is not found
        print("\n[!] No passwords stored or user not found.\n")

def delete_password(uid):
    # Read the stored passwords from the file
    app_password = read_passwords()

    # Check if the user exists and has stored passwords
    if uid in app_password and app_password[uid]:
        print("=" * 40)
        print(f"{'Stored Passwords'.center(40)}")
        print("=" * 40)

        # Enumerate through the list of stored passwords and display the domains
        for index, entry in enumerate(app_password[uid], 1):
            print(f"{index}. {entry['domain']}")

        try:
            choice = int(input("\nEnter the option number to delete the password: "))
            if 0 < choice <= len(app_password[uid]):
                deleted_entry = app_password[uid].pop(choice - 1)  # Delete the entry

                write_passwords(app_password)  # Update the password file

                log_update(f"Deleted password for {deleted_entry['domain']} under user {uid}")
                log_update(f"Deleted credentials - user: {uid}, domain: {deleted_entry['domain']}, password: {deleted_entry['pwd']} ")

                print("*" * 40)
                print(f"Password for {deleted_entry['domain']} deleted successfully.")
                print("*" * 40)

            else:
                print("\n[!] Invalid option selected. Please choose a valid number.\n")

        except ValueError:
            print("\n[!] Please enter a valid number.\n")
    else:
        print("\n[!] No passwords stored or user not found.\n")

if __name__ == "__main__":
    main()
