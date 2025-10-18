import uuid
import sys
import os

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.user_pydantic_models import LoginModel, SignUpModel, LoginSignUpResponseModel
from src.database.db_connection import conn, cursor

class User_services:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor
        
    def login_user(self, login_model: LoginModel) -> LoginSignUpResponseModel:
        """Service to handle user login"""
        try:
            self.cursor.execute("SELECT user_id, password FROM users WHERE email=?", (login_model.email,))
            user = self.cursor.fetchone()
            
            if user and user[1] == login_model.password:  # user[1] is password
                return LoginSignUpResponseModel(
                    status="success",
                    data=user[0],  # user[0] is id
                    message="Login successful"
                )
            return LoginSignUpResponseModel(
                status="failure",
                data="",
                message="Invalid email or password"
            )
        except Exception as e:
            print(f"Error during login: {e}")
            return LoginSignUpResponseModel(
                status="failure",
                data="",
                message="Login failed"
            )
            
    def signup_user(self, signup_model: SignUpModel) -> LoginSignUpResponseModel:
        """Service to handle user signup"""
        try:
            # Check if user already exists
            self.cursor.execute("SELECT user_id FROM users WHERE email=?", (signup_model.email,))
            if self.cursor.fetchone():
                return LoginSignUpResponseModel(
                    status="failure",
                    data="",
                    message="User with this email already exists"
                )
            if len(signup_model.password) < 6:
                return LoginSignUpResponseModel(
                    status="failure",
                    data="",
                    message="Password must be at least 6 characters long"
                )
            
            user_id = uuid.uuid4().hex
            category_str = ','.join(signup_model.category)  # Convert list to comma-separated string
            if signup_model.name and signup_model.email and signup_model.password and signup_model.category:
                self.cursor.execute(
                    "INSERT INTO users (user_id, name, email, password, category, cefr_level) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, signup_model.name, signup_model.email, signup_model.password, category_str, "A0")
                )
            else:
                self.cursor.execute(
                    "INSERT INTO users (user_id, name, email, password, category, cefr_level) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, signup_model.name, signup_model.email, signup_model.password, signup_model.category, 0)
                )
            self.conn.commit()
            
            return LoginSignUpResponseModel(
                status="success",
                data=user_id,
                message="Signup successful"
            )
        except Exception as e:
            print(f"Error during signup: {e}")
            self.conn.rollback()  # Rollback on error
            return LoginSignUpResponseModel(
                status="failure",
                data="",
                message="Signup failed"
            )
    
    def get_user(self, user_id: str) -> dict:
        """Service to get user details"""
        try:
            self.cursor.execute(
                "SELECT user_id, name, email, category, cefr_level FROM users WHERE user_id=?",
                (user_id,)
            )
            user = self.cursor.fetchone()
            
            if user:
                # Normalize topic categories list
                categories_raw = user[3] if user[3] else ""
                topic_categories = [c.strip() for c in categories_raw.split(",") if c and c.strip()]

                # Normalize CEFR level to string A0..C2 if integer stored
                cefr_value = user[4]
                if isinstance(cefr_value, int):
                    cefr_map = {
                        0: "A0", 1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"
                    }
                    current_cefr_level = cefr_map.get(cefr_value, "A0")
                else:
                    current_cefr_level = str(cefr_value)
                return {
                    "status": "success",
                    "data": {
                        "user_id": user[0],
                        "name": user[1],
                        "email": user[2],
                        # Backward-compatible fields
                        "category": user[3],
                        "cefr_level": user[4],
                        # New normalized fields aligned with MVP models
                        "topic_categories": topic_categories,
                        "current_cefr_level": current_cefr_level,
                    },
                    "message": "User found"
                }
            else:
                return {
                    "status": "failure",
                    "data": None,
                    "message": "User not found"
                }
        except Exception as e:
            print(f"Error getting user: {e}")
            return {
                "status": "failure",
                "data": None,
                "message": "Failed to retrieve user"
            }

if __name__ == "__main__":
    # Initialize the service
    user_service = User_services()
    
    try:
        # Test Case 1: Sign up a new user
        print("\n=== Test Case 1: Sign up a new user ===")
        signup_data = SignUpModel(
            name="Test User",
            email="test@example.com",
            password="test123",
            category=["student", "beginner"],  # category is a list of strings
            anonymous_name="Anonymous Tester"  # optional field
        )
        signup_result = user_service.signup_user(signup_data)
        print(f"Signup Result: {signup_result.status} - {signup_result.message}")
        
        # Test Case 2: Try to sign up with same email (should fail)
        print("\n=== Test Case 2: Sign up with existing email ===")
        duplicate_signup = user_service.signup_user(signup_data)
        print(f"Duplicate Signup Result: {duplicate_signup.status} - {duplicate_signup.message}")
        
        # Test Case 3: Login with correct credentials
        print("\n=== Test Case 3: Login with correct credentials ===")
        login_data = LoginModel(
            email="test@example.com",
            password="test123"
        )
        login_result = user_service.login_user(login_data)
        print(f"Login Result: {login_result.status} - {login_result.message}")
        
        # Test Case 4: Login with wrong password
        print("\n=== Test Case 4: Login with wrong password ===")
        wrong_login = LoginModel(
            email="test@example.com",
            password="wrongpass"
        )
        wrong_login_result = user_service.login_user(wrong_login)
        print(f"Wrong Password Login Result: {wrong_login_result.status} - {wrong_login_result.message}")
        
        # Test Case 5: Login with non-existent email
        print("\n=== Test Case 5: Login with non-existent email ===")
        nonexistent_login = LoginModel(
            email="nonexistent@example.com",
            password="test123"
        )
        nonexistent_result = user_service.login_user(nonexistent_login)
        print(f"Non-existent User Login Result: {nonexistent_result.status} - {nonexistent_result.message}")
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
    finally:
        # Clean up test data
        try:
            user_service.cursor.execute("DELETE FROM users WHERE email=?", ("test@example.com",))
            user_service.conn.commit()
            print("\nTest data cleaned up successfully")
        except Exception as e:
            print(f"\nError cleaning up test data: {str(e)}")
        
    print("\n=== All test cases completed ===")