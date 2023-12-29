class ResourceInUseError(Exception):
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        super().__init__(f"Resource {resource_name} is being used and cannot be deleted")
