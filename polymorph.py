import itertools
import os

def generate_variations(password): #This will map each character to its leetspeak substitution
    replacements = {
        'a': ['a', 'A', '@'], 'b': ['b', 'B', '8'], 'c': ['c', 'C', '('],
        'd': ['d', 'D'], 'e': ['e', 'E', '3'], 'f': ['f', 'F'], 
        'g': ['g', 'G', '6', '9'], 'h': ['h', 'H', '#'], 'i': ['i', 'I', '1', '!'],
        'j': ['j', 'J'], 'k': ['k', 'K'], 'l': ['l', 'L', '1'], 'm': ['m', 'M'],
        'n': ['n', 'N'], 'o': ['o', 'O', '0'], 'p': ['p', 'P'], 'q': ['q', 'Q'],
        'r': ['r', 'R'], 's': ['s', 'S', '$', '5'], 't': ['t', 'T', '7'],
        'u': ['u', 'U', 'µ'], 'v': ['v', 'V'], 'w': ['w', 'W'], 'x': ['x', 'X'],
        'y': ['y', 'Y'], 'z': ['z', 'Z', '2']
    }

    # This will help to ensure all uppercase character is included
    for letter in list(replacements.keys()):
        if letter.islower():
            upper_letter = letter.upper()
            replacements[upper_letter] = list(set([upper_letter] + replacements[letter]))

    # This will be used to generate all possible variations
    char_options = [replacements.get(char, [char]) for char in password]
    all_variations = (''.join(variant) for variant in itertools.product(*char_options))

    return all_variations

# This is used to read the possible passwords from the file
def process_passwords(input_file):
    input_file = os.path.abspath(input_file)  # Convert to absolute path

    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return

    # This is used to generate output file in the same directory as input
    output_file = os.path.join(os.path.dirname(input_file), "generatedpass.txt")

    total_variations = 0 # This is for the counter for variations.

    # This is used to read passwords from the input file
    with open(input_file, "r") as file:
        password_list = [line.strip() for line in file.readlines()]

    # This is used to process each password with the variations
    with open(output_file, "w") as file:
        for password in password_list:
            print(f"\n🔹 Processing password: {password}")
            variations = generate_variations(password)
            for variation in variations:
                file.write(variation + "\n")
                total_variations += 1

    print(f"\nTotal variations generated: {total_variations}")
    print(f"File is saved to: {output_file}")

if __name__ == "__main__":
    input_filename = input("Enter the full path to your passwords.txt file: (ex. C:\\Users\\username\\Downloads\\passwords.txt) ").strip()

    process_passwords(input_filename)
