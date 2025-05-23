# test_imports.py
try:
    import pandas as pd
    print(pd.__version__)
    print("✅ Pandas imported successfully")
    
    import pyarrow as pa
    print("✅ PyArrow imported successfully")
    
    import cloudpickle
    print("✅ Cloudpickle imported successfully")
    
    import feast
    print("✅ Feast imported successfully")
    
    from langchain_core import runnables
    print("✅ LangChain imported successfully")
    
    import langgraph.graph
    print("✅ LangGraph imported successfully")
except Exception as e:
    print(f"❌ Error: {e}")