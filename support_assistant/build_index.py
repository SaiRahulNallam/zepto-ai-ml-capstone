from pathlib import Path
from .config import ROOT
from .retrieval import build_collection
if __name__ == "__main__":
    c=build_collection(ROOT/"docs")
    print({"collection":c.name,"count":c.count()})
