import uuid
import sys
import os
from datetime import datetime

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.user_pydantic_models import (
    LoginModel, SignUpModel, LoginSignUpResponseModel,
    UserModel, UpdateUserCEFRModel, UpdateUserLastActiveModel, UpdateUserPasswordModel
)
from src.database.db_connection import conn, cursor

class User_services:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor

    def hash_password(self, password: str) -> str:
        """Hash the password (placeholder function)"""
        # In production, use a secure hashing algorithm like bcrypt
        return "hashed_" + password
    
    def unhash_password(self, hashed_password: str) -> str:
        """Unhash the password (placeholder function)"""
        # In production, use a secure hashing algorithm like bcrypt
        if hashed_password.startswith("hashed_"):
            return hashed_password[len("hashed_"):]
        return ""

    def verify_password(self, old_password_from_user: str, hashed_old_password_from_db: str) -> bool:
        """Verify a plain password against the hashed password"""
        return self.unhash_password(hashed_old_password_from_db) == old_password_from_user

    def get_user_password_hash(self, user_id: str) -> str:
        """Retrieve the hashed password for a user from the database"""
        self.cursor.execute("SELECT hashed_password FROM users WHERE user_id=?", (user_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return ""

    def login_user(self, login_model: LoginModel) -> LoginSignUpResponseModel:
        """Service to handle user login"""
        try:
            self.cursor.execute("SELECT user_id, hashed_password FROM users WHERE email=?", (login_model.email,))
            user = self.cursor.fetchone()

            if user and self.unhash_password(user[1]) == login_model.password:  # user[1] is hashed_password
                # Get the full user data to return as UserModel
                user_data = self.get_user(user[0])
                return LoginSignUpResponseModel(
                    status="success",
                    data=user_data,
                    message="Login successful"
                )
            return LoginSignUpResponseModel(
                status="failure",
                data=None,
                message="Invalid email or password"
            )
        except Exception as e:
            print(f"Error during login: {e}")
            return LoginSignUpResponseModel(
                status="failure",
                data=None,
                message=f"Login failed: {str(e)}"
            )
            
    def signup_user(self, signup_model: SignUpModel) -> LoginSignUpResponseModel:
        """Service to handle user signup"""
        try:
            # Check if user already exists
            self.cursor.execute("SELECT user_id FROM users WHERE email=?", (signup_model.email,))
            if self.cursor.fetchone():
                return LoginSignUpResponseModel(
                    status="failure",
                    data=None,
                    message="User with this email already exists"
                )
            if len(signup_model.password) < 6:
                return LoginSignUpResponseModel(
                    status="failure",
                    data=None,
                    message="Password must be at least 6 characters long"
                )
            
            user_id = uuid.uuid4().hex
            category_str = ','.join(signup_model.topic_categories) if signup_model.topic_categories else ''
            created_at = datetime.now()
            last_active = datetime.now()
            if signup_model.name and signup_model.email and signup_model.password:
                # Hash password before storing (omitted for brevity)
                hashed_password = self.hash_password(signup_model.password)

                self.cursor.execute(
                    "INSERT INTO users (user_id, name, email, hashed_password, topic_categories, current_cefr_level, created_at, last_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, signup_model.name, signup_model.email, hashed_password, category_str, signup_model.current_cefr_level, created_at, last_active)
                )
            self.conn.commit()
            
            # Get the created user to return as UserModel
            user_data = self.get_user(user_id)
            return LoginSignUpResponseModel(
                status="success",
                data=user_data,
                message="Signup successful"
            )
        except Exception as e:
            print(f"Error during signup: {e}")
            self.conn.rollback()  # Rollback on error
            return LoginSignUpResponseModel(
                status="failure",
                data=None,
                message=f"Signup failed: {str(e)}"
            )
    
    def get_user(self, user_id: str) -> UserModel:
        """Service to get user details"""
        try:
            self.cursor.execute(
                "SELECT user_id, name, email, hashed_password, topic_categories, current_cefr_level, created_at, last_active FROM users WHERE user_id=?",
                (user_id,)
            )
            user = self.cursor.fetchone()
            
            if user:
                # Normalize topic categories list
                categories_raw = user[4] if user[4] else ""
                topic_categories = [c.strip() for c in categories_raw.split(",") if c and c.strip()]

                # Normalize CEFR level to string A0..C2 if integer stored
                cefr_value = user[5]
                current_cefr_level = str(cefr_value)
                
                return UserModel(
                    user_id=user[0],
                    name=user[1],
                    email=user[2],
                    hashed_password=user[3],
                    topic_categories=topic_categories,
                    current_cefr_level=current_cefr_level,
                    created_at=user[6],
                    last_active=user[7],
                )
            else:
                raise ValueError("User not found")
        except Exception as e:
            print(f"Error getting user: {e}")
            raise e

    def list_users(self) -> dict:
        """List all users
        
        # FLAG: NOT CONVERTIBLE - This function returns dict instead of pydantic model
        # TODO: Convert to use ListUsersResponseModel
        """
        try:
            self.cursor.execute("SELECT user_id, name, email, topic_categories, current_cefr_level, created_at, last_active FROM users ORDER BY created_at DESC")
            rows = self.cursor.fetchall()
            cols = [d[0] for d in self.cursor.description]
            return {"status": "success", "data": [dict(zip(cols, r)) for r in rows], "message": "Users listed"}
        except Exception as e:
            print(f"Error listing users: {e}")
            return {"status": "failure", "data": [], "message": f"Failed to list users: {e}"}

    
    def delete_user(self, user_id: str) -> dict:
        """Delete user
        
        # FLAG: NOT CONVERTIBLE - This function returns dict instead of pydantic model
        # TODO: Convert to use DeleteUserResponseModel
        """
        try:
            self.cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            self.conn.commit()
            return {"status": "success", "data": {"deleted": self.cursor.rowcount}, "message": "User deleted"}
        except Exception as e:
            print(f"Error deleting user: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": f"Failed to delete user: {e}"}

    def update_user_cefr_level(self, update: UpdateUserCEFRModel) -> dict:
        """Update user's CEFR level
        
        # FLAG: NOT CONVERTIBLE - This function returns dict instead of pydantic model
        # TODO: Convert to use UpdateUserResponseModel
        """
        try:
            self.cursor.execute(
                "UPDATE users SET current_cefr_level=? WHERE user_id=?",
                (update.current_cefr_level.value, update.user_id)
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "CEFR level updated"}
            return {"status": "failure", "data": None, "message": "User not found"}
        except Exception as e:
            print(f"Error updating CEFR level: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": f"Failed to update CEFR level: {e}"}

    def update_user_last_active(self, update: UpdateUserLastActiveModel) -> dict:
        """Update user's last active timestamp
        
        # FLAG: NOT CONVERTIBLE - This function returns dict instead of pydantic model
        # TODO: Convert to use UpdateUserResponseModel
        """
        try:
            self.cursor.execute(
                "UPDATE users SET last_active=? WHERE user_id=?",
                (update.last_active, update.user_id)
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Last active updated"}
            return {"status": "failure", "data": None, "message": "User not found"}
        except Exception as e:
            print(f"Error updating last active: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": f"Failed to update last active: {e}"}

    def update_user_password(self, update: UpdateUserPasswordModel) -> dict:
        """Update user's password
        
        # FLAG: NOT CONVERTIBLE - This function returns dict instead of pydantic model
        # TODO: Convert to use UpdateUserResponseModel
        """
        try:
            if update.old_password == update.new_password:
                return {"status": "failure", "data": None, "message": "New password must be different from old password"}
            if not self.verify_password(update.old_password, self.get_user_password_hash(update.user_id)):
                return {"status": "failure", "data": None, "message": "Old password is incorrect"}
            self.cursor.execute(
                "UPDATE users SET hashed_password=? WHERE user_id=?",
                (self.hash_password(update.new_password), update.user_id)
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Password updated"}
            return {"status": "failure", "data": None, "message": "User not found"}
        except Exception as e:
            print(f"Error updating password: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": f"Failed to update password: {e}"}

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