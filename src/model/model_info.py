import ollama

def get_ollama_models():
    try:
        models = ollama.list()
        model_names = [model['model'] for model in models['models']]
        return model_names 
    except Exception as e:
        print(f"Error : {e}")
        raise

def get_context_length(model: str):
    try:
        info = ollama.show(model)
        details = info.get("modelinfo", {})
        family = info.get("details", {}).get("family", "")
        
        # try exact key first
        context_search_key = f"{family}.context_length"
        context_length = details.get(context_search_key)
        
        # fallback: first key ending with 'context_length'
        if context_length is None:
            for k, v in details.items():
                if k.endswith("context_length"):
                    context_length = v
                    break
        
        if context_length is None:
            raise ValueError(f"No context_length found for model '{model}'")
        
        return context_length
    
    except Exception as e:
        print(f"Error retrieving context_length for '{model}': {e}")
        raise

