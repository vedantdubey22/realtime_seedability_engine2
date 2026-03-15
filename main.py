
from loader import load_all
from seedability_engine import run_seedability_engine
from visualize.plot_seedability import plot_all


def main():
    # Step 1 — Load all tiles
    data = load_all()

    # Step 2 — Run seedability engine
    products = run_seedability_engine(data)

    # Step 3 — Plot everything
    plot_all(data, products)


if __name__ == "__main__":
    main()