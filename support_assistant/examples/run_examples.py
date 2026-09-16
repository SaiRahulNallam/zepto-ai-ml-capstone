import json
from support_assistant.graph import build_graph

g=build_graph()
for q in ["What is the delivery fee for an order below INR 149?","What is the capital of France?"]:
    out=g.invoke({"query":q})
    print(json.dumps(out["response"],indent=2))
