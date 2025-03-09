import itertools
import os

def generate_variations(password):
    # Map each character to its leetspeak substitutions.
    replacements = {
        'a': ['a', 'A', '@'], 'b': ['b', 'B', '8'], 'c': ['c', 'C', '('],
        'd': ['d', 'D'], 'e': ['e', 'E', '3'], 'f': ['f', 'F'], 
        'g': ['g', 'G', '6', '9'], 'h': ['h', 'H', '#'], 'i': ['i', 'I', '1', '!'],
        'j': ['j', 'J'], 'k': ['k', 'K'], 'l': ['l', 'L', '1'], 'm': ['m', 'M'],
        'n': ['n', 'N'], 'o': ['o', 'O', '0'], 'p': ['p', 'P'], 'q': ['q', 'Q'],
        'r': ['r', 'R'], 's': ['s', 'S', '$', '5'], 't': ['t', 'T', '7'],
        'u': ['u', 'U', 'µ'], 'v': ['v', 'V'], 'w': ['w', 'W'], 'x': ['x', 'X'],
        'y': ['y', 'Y'], 'z': ['z', 'Z', '2'], '@' : ['a', 'A', '@'], '&' : ['&', '8'],
        '1': ['1', 'l', 'L', 'i', 'I'], '2': ['2', 'z', 'Z'], '3': ['3', 'e', 'E'],
        '4': ['4'], '5': ['5', 's', 'S'], '6': ['6', 'g', 'G'], '7': ['7', 't', 'T'],
        '8': ['8', 'b', 'B', '&'], '9': ['9', 'g', 'G'], '0': ['0', 'o', 'O'],
        '!': ['!', 'i', 'I', 'l', 'L'], '@': ['@', 'a', 'A']
    }

    # Ensure uppercase characters are fully covered.
    for letter in list(replacements.keys()):
        if letter.islower():
            upper_letter = letter.upper()
            replacements[upper_letter] = list(set([upper_letter] + replacements[letter]))

    # Generate all possible variations by creating a list of character options.
    char_options = [replacements.get(char, [char]) for char in password]
    all_variations = (''.join(variant) for variant in itertools.product(*char_options))
    return all_variations

def process_passwords(input_file):
    input_file = os.path.abspath(input_file)
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return

    # Write back to the same file.
    output_file = input_file
    total_variations = 0

    with open(input_file, "r") as file:
        password_list = [line.strip() for line in file.readlines()]

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
    process_passwords("usernames.txt")
    process_passwords("generatedpass.txt")
