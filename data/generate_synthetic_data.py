import json
import argparse
from faker import Faker

def generate(num_samples: int):
    fake = Faker()
    texts = []

    for _ in range(num_samples):
        name = fake.name()
        address = fake.street_address()
        city = fake.city()
        date = fake.date_this_decade().isoformat()
        texts.append(f"{name} lives at {address}, {city}. Last checkup was on {date}")
    return texts

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=int, default=50)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    samples = generate(args.num)
    with open(args.output, 'w') as f:
        json.dump(samples, f, indent= 2)
        print(f"Generated {args.num} samples => {args.output}")