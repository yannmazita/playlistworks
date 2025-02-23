from pathlib import Path

SRC_PATH = Path(__file__).parent.parent.parent


def get_component_paths() -> list[Path]:
    """
    Gets base directories containing component modules
    return: A list of Path objects
    """
    src_path = Path(__file__).parent.parent.parent
    component_paths: list[Path] = []
    features_dir = src_path / "features"

    common_paths = src_path / "common" / "components"
    if common_paths.is_dir():
        component_paths.append(common_paths)

    for feature in features_dir.iterdir():
        component_path = feature / "components"
        if component_path.is_dir():
            component_paths.append(component_path)

    return component_paths
