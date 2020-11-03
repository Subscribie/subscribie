from subscribie import current_app


def getLoadedModules():
    """Get module names and links
    Of the loaded modules, return a list indexed
    by the module (bluepint) name (useful for `url_for`),
    and all the links that module publishes.

    :return: dict of modules

    Structure:
    modules['module-name']['links'] = [module-index-route]
    modules['module-name']['friendly-name'] = "Module name"
    """

    def isBlacklistedSystemModule(rule):
        """Filter out system modules"""
        # Filter out system blueprints
        if "_uploads" in rule or "auth" in rule or "views" in rule or "admin" in rule:
            return True
        return False

    # Get all activeBlueprintNames, excluding system ones
    activeBlueprintNames = []
    for key in current_app.blueprints.keys():
        if isBlacklistedSystemModule(key) is False:
            activeBlueprintNames.append(current_app.blueprints[key].name)

    # For each activeBlueprint, find its index route and add to 'links' property
    # We *only* store module links which are called "[/blueprintname/index]"
    # This is because we don't know ahead of time which arguments a url_for
    # Route needs. We only generally need the blueprint's index route anyway,
    # which is used in the application layer to show links to a modules settings
    # page for example.
    # Also generate a readable friendly name for the blueprint
    modules = {}
    for blueprintName in activeBlueprintNames:
        modules[blueprintName] = {"links": []}
        friendly_name = blueprintName.replace("_", " ").capitalize()
        modules[blueprintName]["friendly-name"] = friendly_name
        # Add matching Rules (routes) which map to loaded Blueprint
        rules = current_app.url_map.iter_rules()  # All Rules
        for rule in rules:
            if (
                blueprintName in rule.endpoint
                and rule.rule == "/" + blueprintName + "/index"
            ):  # Only add the index route
                modules[blueprintName]["links"].append(rule.endpoint)
    return modules
