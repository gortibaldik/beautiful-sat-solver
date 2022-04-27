from argparse import ArgumentParser


def read_stats(input_file):
    cdecs, cunits, ctime = 0, 0, 0
    total = 0
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if "task2_controller" in line:
                continue
            total += 1
            _, decs, units, time = line.split(';')
            cdecs += int(decs.split()[1])
            cunits += int(units.split()[1])
            ctime += float(time.split()[1])
    
    return {
        "average time": ctime / total,
        "average unit derived variables": cunits / total,
        "average decision derived variables": cdecs / total
    }


def main():
    parser = ArgumentParser()
    parser.add_argument("input_file")
    args = parser.parse_args()
    stats = read_stats(args.input_file)
    for stat, value in stats.items():
        print(f"{stat}: {value}")

if __name__ == "__main__":
    main()