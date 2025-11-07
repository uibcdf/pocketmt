feature_types_by_shape_type = {
    "point": ["feature0d", "point", "pit", "apex", "summit", "bifurcation", "saddle_point", "ridge_tip"],
    "boundary": ["feature1d", "mouth", "base_rim", "neck", "ridge", "furrow", "lip", "seam", "isthmus", "edge_loop",
                 "branch_line", "hinge_line"],
    "concavity": ["void", "pocket", "channel", "branched_channel", "groove", "funnel", "vestibule", "ampulla",
                  "alcove"],
    "convexity": ["protrusion", "dome", "ridge", "spine", "bulge", "ridge_cap", "knob", "buttress", "pinnacle"],
    "mixed": ["feature2d", "interface", "patch", "joint", "saddle", "trench"],
}

shape_type_by_feature_type = {
}
for shape_type, feature_types in feature_types_by_shape_type.items():
    for feature_type in feature_types:
        shape_type_by_feature_type[feature_type] = shape_type

dimensionality_by_feature_type = {
}
for shape_type, feature_types in feature_types_by_shape_type.items():
    for feature_type in feature_types:
        if shape_type in ["point"]:
            dimensionality_by_feature_type[feature_type] = 0
        elif shape_type in ["boundary"]:
            dimensionality_by_feature_type[feature_type] = 1
        elif shape_type in ["concavity", "convexity", "mixed"]:
            dimensionality_by_feature_type[feature_type] = 2
