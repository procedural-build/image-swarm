import docker


def is_leader() -> bool:
    """Check if Docker node is leader"""

    client = docker.from_env()
    info = client.info()
    node_id = info.get("Swarm", {}).get("NodeID")

    is_manager = info.get("Swarm", {}).get("ControlAvailable", False)
    if not is_manager:
        return False

    node = client.nodes.get(node_id)
    return node.attrs.get("ManagerStatus", {}).get("Leader", False)
