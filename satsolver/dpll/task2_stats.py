from argparse import ArgumentParser


def read_stats(input_file, sat):
    cdecs, cunits, ctime = 0, 0, 0
    total = 0
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if "task2_controller" in line:
                if line[-2:] != "OK" and sat:
                    raise RuntimeError(f"Not valid!: {line}")
                elif "UNSAT" not in line and not sat:
                    raise RuntimeError(f"Not valid!: {line}")
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
    parser.add_argument("--sat", action='store_true')
    args = parser.parse_args()
    stats = read_stats(args.input_file, args.sat)
    for stat, value in stats.items():
        print(f"{stat}: {value}")

if __name__ == "__main__":
    main()