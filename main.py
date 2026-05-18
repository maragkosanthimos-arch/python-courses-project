import time
from api_collectors import fetch_udemy, fetch_youtube, fetch_coursera

def collect_all_courses():
    print("\n=== CLOSED API COURSE AGGREGATOR ===")

    all_courses = []

    all_courses += fetch_udemy()
    time.sleep(1)

    all_courses += fetch_youtube()
    time.sleep(1)

    all_courses += fetch_coursera()

    print(f"\n=== DONE | TOTAL COURSES: {len(all_courses)} ===")
    return all_courses


if __name__ == "__main__":
    courses = collect_all_courses()

    for c in courses:
        print(c)