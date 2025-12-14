import os
from typing import Dict
from jose import jwt
from jose.exceptions import JWTError
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
import httpx

# In-memory cache for JWKS
JWKS_CACHE = None

async def get_jwks(domain: str) -> Dict:
    """Fetches JWKS from Auth0 and caches it."""
    global JWKS_CACHE
    if JWKS_CACHE:
        return JWKS_CACHE

    jwks_url = f"https://{domain}/.well-known/jwks.json"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            JWKS_CACHE = response.json()
            return JWKS_CACHE
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Failed to fetch JWKS from {jwks_url}: {e}")
    except httpx.RequestError as e:
        raise RuntimeError(f"Network error while fetching JWKS from {jwks_url}: {e}")

async def validate_token(token: str) -> Dict:
    """Validates an Auth0 JWT and returns its claims."""
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
    AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
    AUTH0_ISSUER = os.getenv("AUTH0_ISSUER")

    if not all([AUTH0_DOMAIN, AUTH0_AUDIENCE, AUTH0_ISSUER]):
        raise ValueError("Missing Auth0 configuration environment variables.")

    jwks = await get_jwks(AUTH0_DOMAIN)

    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise ValueError("Invalid token header.")

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            break
    if not rsa_key:
        raise ValueError("RSA key not found in JWKS.")

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except jwt.JWTClaimsError:
        raise ValueError("Incorrect claims, please check the audience and issuer.")
    except JWTError as e:
        raise ValueError(f"Could not validate token: {e}")

    return payload