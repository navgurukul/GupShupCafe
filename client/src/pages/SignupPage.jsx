import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  MessageSquare,
  Tag,
} from "lucide-react";

import { createUserData } from "../utils/helpers";

const categories = [
  {
    id: "currentAffairs",
    label: "Current Affairs",
    color: "bg-red-100 text-red-800",
  },
  {
    id: "scienceAndTechnology",
    label: "Science & Technology",
    color: "bg-blue-100 text-blue-800",
  },
  {
    id: "literature",
    label: "Literature",
    color: "bg-purple-100 text-purple-800",
  },
  { id: "education", label: "Education", color: "bg-green-100 text-green-800" },
  { id: "politics", label: "Politics", color: "bg-yellow-100 text-yellow-800" },
  {
    id: "environment",
    label: "Environment",
    color: "bg-emerald-100 text-emerald-800",
  },
  { id: "healthcare", label: "Healthcare", color: "bg-pink-100 text-pink-800" },
  { id: "business", label: "Business", color: "bg-orange-100 text-orange-800" },
  { id: "sports", label: "Sports", color: "bg-indigo-100 text-indigo-800" },
  {
    id: "entertainment",
    label: "Entertainment",
    color: "bg-violet-100 text-violet-800",
  },
  { id: "philosophy", label: "Philosophy", color: "bg-gray-100 text-gray-800" },
  { id: "history", label: "History", color: "bg-amber-100 text-amber-800" },
];

/**
 * SignupPage Component
 * Handles user registration with name, email, password, and interest categories
 */
function SignupPage() {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [selectedCategories, setSelectedCategories] = useState([]);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate("/lobby");
    }
  }, [isAuthenticated, navigate]);

  /**
   * Handle form input changes
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  /**
   * Toggle interest category selection
   */
  const toggleCategory = (categoryId) => {
    setSelectedCategories((prev) =>
      prev.includes(categoryId)
        ? prev.filter((id) => id !== categoryId)
        : [...prev, categoryId]
    );

    // Clear category error when user selects one
    if (errors.categories) {
      setErrors((prev) => ({
        ...prev,
        categories: "",
      }));
    }
  };

  /**
   * Validate form data
   */
  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    } else if (formData.name.length < 2) {
      newErrors.name = "Name must be at least 2 characters";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.password.trim()) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    if (selectedCategories.length === 0) {
      newErrors.categories = "Please select at least one interest category";
    }

    return newErrors;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const newErrors = validateForm();

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setIsSubmitting(false);
      return;
    }

    try {
      // Call backend API for user registration
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:3003";
      const response = await fetch(`${apiUrl}/users/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          current_cefr_level: "A0", // Initial CEFR level
          topic_categories: selectedCategories,
        }),
      });

      const result = await response.json();

      if (result.status === "success") {
        // result.data now contains the full UserModel object
        const userData = result.data;

        if (userData && userData.user_id) {
          // Create user data with the full user object from backend
          const { userData: processedUserData, error } = createUserData(
            userData,
            formData.email
          );

          if (error) {
            setErrors({ submit: error });
            return;
          }

          // Login with the new user data
          login(processedUserData);

          // Save userData to localStorage
          localStorage.setItem("userData", JSON.stringify(processedUserData));

          // Navigate to lobby
          navigate("/lobby");
        } else {
          setErrors({ submit: "Invalid user data received from server." });
        }
      } else {
        setErrors({
          submit: result.message || "Registration failed. Please try again.",
        });
      }
    } catch (error) {
      console.error("Signup error:", error);
      setErrors({
        submit:
          "Registration failed. Please check your connection and try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-lg w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-600 rounded-full">
              <MessageSquare className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">Create Account</h2>
          <p className="mt-2 text-gray-600">Join the discussion community</p>
        </div>

        {/* Signup Form */}
        <form
          onSubmit={handleSubmit}
          className="space-y-6 bg-white p-8 rounded-lg shadow-lg"
        >
          {/* Name */}
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700"
            >
              Full Name
            </label>
            <div className="mt-1 relative">
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleChange}
                className="block w-full px-3 py-2 pl-10 border border-gray-300 rounded-md shadow-sm 
                           focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your full name"
              />
              <User className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
            </div>
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name}</p>
            )}
          </div>

          {/* Email */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email Address
            </label>
            <div className="mt-1 relative">
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="block w-full px-3 py-2 pl-10 border border-gray-300 rounded-md shadow-sm 
                           focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your email"
              />
              <Mail className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
            </div>
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email}</p>
            )}
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <div className="mt-1 relative">
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                required
                value={formData.password}
                onChange={handleChange}
                className="block w-full px-3 py-2 pl-10 pr-10 border border-gray-300 rounded-md shadow-sm 
                           focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your password"
              />
              <Lock className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password}</p>
            )}
          </div>

          {/* Interest Categories */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <Tag className="w-4 h-4 inline mr-1" />
              Interest Categories (Select multiple)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {categories.map((category) => (
                <button
                  key={category.id}
                  type="button"
                  onClick={() => toggleCategory(category.id)}
                  className={`p-3 text-sm rounded-lg border-2 transition-all duration-200 ${
                    selectedCategories.includes(category.id)
                      ? `${category.color} border-current shadow-md transform scale-105`
                      : "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100"
                  }`}
                >
                  {category.label}
                </button>
              ))}
            </div>
            {errors.categories && (
              <p className="mt-2 text-sm text-red-600">{errors.categories}</p>
            )}
            {selectedCategories.length > 0 && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {selectedCategories.length} categories
              </p>
            )}
          </div>

          {/* Submit Error */}
          {errors.submit && (
            <div className="text-sm text-red-600 text-center">
              {errors.submit}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md 
                       shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 
                       focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? "Creating Account..." : "Create Account"}
          </button>

          {/* Login Link */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{" "}
              <Link
                to="/"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SignupPage;
