from backend.pipeliner import run_pipeline

if __name__ == "__main__":
    test_url = input("Enter product URL: ")
    result = run_pipeline(test_url)
    print(result["final_decision"]["label"])
    print(result["final_decision"]["reason"])
