import uuid
from ..models.user_pydantic_models import LoginModel, SignUpModel, CreateRoomModel, JoinRoomModel, LoginResponseModel
from ..database.db_connection import conn, cursor

class User_services:
    def __init__(self):
        self.conn=conn
        self.cursor=cursor
        
    def login_user(self, login_model: LoginModel) -> LoginResponseModel:
        """Service to handle user login"""
        try:
            self.cursor.execute("SELECT id, password FROM users WHERE email=?", (login_model.email,))
            user = self.cursor.fetchone()
            
            if user and user[1] == login_model.password:  # user[1] is password
                return LoginResponseModel(
                    status="success",
                    data=user[0],  # user[0] is id
                    message="Login successful"
                )
            return LoginResponseModel(
                status="failure",
                data="",
                message="Invalid email or password"
            )
        except Exception as e:
            print(f"Error during login: {e}")
            return LoginResponseModel(
                status="failure",
                data="",
                message="Login failed"
            )
            
    def signup_user(self, signup_model: SignUpModel) -> LoginResponseModel:
        """Service to handle user signup"""
        try:
            # Check if user already exists
            self.cursor.execute("SELECT id FROM users WHERE email=?", (signup_model.email,))
            if self.cursor.fetchone():
                return LoginResponseModel(
                    status="failure",
                    data="",
                    message="User with this email already exists"
                )

            user_id = uuid.uuid4().hex
            self.cursor.execute(
                "INSERT INTO users (id, name, email, password, category) VALUES (?, ?, ?, ?, ?)",
                (user_id, signup_model.name, signup_model.email, signup_model.password, signup_model.category)
            )
            self.conn.commit()
            
            return LoginResponseModel(
                status="success",
                data=user_id,
                message="Signup successful"
            )
        except Exception as e:
            print(f"Error during signup: {e}")
            self.conn.rollback()  # Rollback on error
            return LoginResponseModel(
                status="failure",
                data="",
                message="Signup failed"
            )