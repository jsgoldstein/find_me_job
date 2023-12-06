import csv
from typing import List, Self, Set, Tuple


INPUT_FILE = '/Users/jakegoldstein/downloads/cgww_newsletter.csv'
OUTPUT_FILE = '/Users/jakegoldstein/downloads/cgww_newsletter_v2.csv'

class Person:
    def __init__(self, email: str, first_name: str, last_name: str) -> None:
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def __eq__(self, other: Self) -> bool:
        return self.email == other.email

    def __hash__(self) -> int:
        return hash(self.email)


def get_full_name(row: List[str]) -> List[str]:
    print(row)
    email = row[0]
    first_name = row[1]
    last_name = row[2]
    if not first_name and last_name and len(last_name.split()) == 2:
        first_name = last_name.split()[0]
        last_name = last_name.split()[1]
    elif not last_name and first_name and len(first_name.split()) == 2:
        last_name = first_name.split()[1]
        first_name = first_name.split()[0]

    return [email, first_name, last_name]


def read_csv() -> Tuple[Set[Person], List[Person]]:
    unique_people = set()
    duplicates = list()

    with open(INPUT_FILE, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            assert len(row) == 3, f"There were more items in this row {row}"

            row = get_full_name(row)
            person = Person(email=row[0], first_name=row[1], last_name=row[2])

            if person in unique_people:
                duplicates.append(person)
            else:
                unique_people.add(person)
    return unique_people, duplicates


def write_csv(people: Set[Person]) -> None:
    with open(OUTPUT_FILE, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['Email', 'First Name', 'Last Name'])
        for person in people:
            csv_writer.writerow([person.email, person.first_name, person.last_name])


def main() -> None:
    unique_people, duplicates = read_csv()
    print(len(duplicates))  # 112
    print(len(unique_people))  # 14038
    write_csv(unique_people)


if __name__ == "__main__":
    main()
