def pick_current_model_key(available_models, previous_model_key=None):
    if previous_model_key in available_models:
        return previous_model_key

    if not available_models:
        return None

    return next(iter(available_models))
