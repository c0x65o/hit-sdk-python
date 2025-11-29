"""Configuration and service discovery for Hit SDK.

Discovers service URLs in priority order:
1. Environment variables (HIT_<SERVICE>_URL)
2. hit.yaml file (hit_services section)
3. Default ports from service manifests
"""

import os
from pathlib import Path
from typing import Optional

import yaml


# Default ports for services (from hit-module.yaml manifests)
DEFAULT_PORTS = {
    "ping-pong": 8099,
    "auth": 8001,
    "email": 8002,
}


def get_service_url(service_name: str) -> str:
    """Get service URL with auto-discovery.
    
    Priority:
    1. Environment variable: HIT_<SERVICE>_URL
    2. hit.yaml configuration
    3. Default localhost with default port
    
    Args:
        service_name: Service name (e.g., "ping-pong", "auth")
    
    Returns:
        Service URL (e.g., "http://localhost:8099")
    """
    # Normalize service name for env var (ping-pong -> PINGPONG)
    env_key = f"HIT_{service_name.upper().replace('-', '_')}_URL"
    
    # 1. Check environment variable
    env_url = os.getenv(env_key)
    if env_url:
        return env_url
    
    # 2. Check hit.yaml
    yaml_url = _get_url_from_yaml(service_name)
    if yaml_url:
        return yaml_url
    
    # 3. Default localhost with default port
    default_port = DEFAULT_PORTS.get(service_name, 8000)
    return f"http://localhost:{default_port}"


def _get_url_from_yaml(service_name: str) -> Optional[str]:
    """Get service URL from hit.yaml configuration.
    
    Args:
        service_name: Service name
    
    Returns:
        Service URL or None if not found
    """
    # Look for hit.yaml in current directory or parent directories
    current_dir = Path.cwd()
    for _ in range(5):  # Check up to 5 levels up
        hit_yaml = current_dir / "hit.yaml"
        if hit_yaml.exists():
            try:
                with open(hit_yaml) as f:
                    config = yaml.safe_load(f)
                
                # Check modules section for service port
                for module in config.get("modules", []):
                    if module.get("name") == service_name:
                        port = module.get("port")
                        if port:
                            return f"http://localhost:{port}"
            except Exception:
                pass  # Ignore yaml parsing errors
            break
        
        # Move up one directory
        parent = current_dir.parent
        if parent == current_dir:
            break  # Reached filesystem root
        current_dir = parent
    
    return None


def get_namespace() -> str:
    """Get namespace for multi-tenancy.
    
    Returns:
        Namespace from HIT_NAMESPACE env var or "default"
    """
    return os.getenv("HIT_NAMESPACE", "default")


def get_api_key(service_name: str) -> Optional[str]:
    """Get API key for service authentication.
    
    Args:
        service_name: Service name
    
    Returns:
        API key or None if not set
    """
    env_key = f"HIT_{service_name.upper().replace('-', '_')}_API_KEY"
    return os.getenv(env_key)

