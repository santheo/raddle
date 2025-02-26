import yaml
from pathlib import Path

def create_yaml_structure(words):
    # Create the basic structure
    puzzle = {
        'meta': {
            'title': f'From {words[0]} to {words[-1]}',
            'author': 'Sandy Weisz',
            'difficulty': 'medium',
        },
        'ladder': []
    }
    
    # Create ladder entries
    for i, word in enumerate(words):
        rung = {
            'word': word,
            'clue': "", 
            'transform': "", 
        }
        puzzle['ladder'].append(rung)
    
    return puzzle

def main():
    # Read input file
    input_path = Path('../static/data/new.txt')
    words = [line.strip() for line in input_path.read_text().splitlines() if line.strip()]
    
    # Create YAML structure
    puzzle = create_yaml_structure(words)
    
    # Generate output filename based on first and last words
    # output_filename = f"{words[0].lower()}-{words[-1].lower()}.yaml"
    output_filename = "new.yaml"
    output_path = input_path.parent / output_filename
    
    # Write YAML file
    with open(output_path, 'w') as f:
        yaml.dump(puzzle, f, default_flow_style=False, sort_keys=False)
    
    print(f"Created {output_path}")

if __name__ == '__main__':
    main()