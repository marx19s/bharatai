import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security secrets and JWT configs
SECRET_KEY = "bharat_ai_sovereign_secret_key_1947"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15 # 15 minutes session expiry

security_scheme = HTTPBearer()

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_access_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid session token.")

    @staticmethod
    def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security_scheme)) -> int:
        payload = AuthService.verify_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Could not validate credentials.")
        return int(user_id)

auth_service = AuthService()
