from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_required_structure():
    for name in ["README.md","requirements.txt","data_pipeline","analytics","support_assistant"]: assert (ROOT/name).exists()
    for rel in ["data_pipeline/src/pipeline.py","analytics/01_eda.ipynb","analytics/02_modeling.ipynb","support_assistant/main.py","support_assistant/Dockerfile"]: assert (ROOT/rel).exists()

def test_exact_support_document_count(): assert len(list((ROOT/"support_assistant/docs").glob("doc_*.txt")))==8
