import os
import sys

# Add the src directory to PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

#from ITSMAnalysis.exception.exception import ITSMAnalysisException  # or whatever you want to run

print("It works!")


def main():
    print("Hello from itsm-multi-agent-support-analysis!")


if __name__ == "__main__":
    main()
