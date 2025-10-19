import React, { useState } from 'react'

import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Mail, Lock, MessageSquare, Eye, EyeOff, Users, Brain } from 'lucide-react'

/**
 * Login Page Component
 * Handles user authentication with email and password
 */
function LoginPage() {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuth()
  
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/lobby')
    }
  }, [isAuthenticated, navigate])

  /**
   * Handle form input changes
   */
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  /**
   * Validate form data
   */
  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }
    
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }
    
    return newErrors
  }

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    const newErrors = validateForm()
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      setIsSubmitting(false)
      return
    }
    
    try {
      // Call backend API for user login
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:3003'
      const response = await fetch(`${apiUrl}/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      })
      
      const result = await response.json()
      
      if (result.status === 'success') {
        // Fetch user details to get name and interests
        const userResponse = await fetch(`${apiUrl}/users/${result.data}`)
        let userName = formData.email.split('@')[0] // Default to email prefix
        let userInterests = []
        
        if (userResponse.ok) {
          const userResult = await userResponse.json()
          if (userResult.status === 'success' && userResult.data) {
            userName = userResult.data.name || userName
            userInterests = userResult.data.category ? 
              (Array.isArray(userResult.data.category) ? userResult.data.category : userResult.data.category.split(',')) 
              : []
          }
        }
        
        // Create user data with the ID returned from backend
        const userData = {
          id: result.data,
          email: formData.email,
          name: userName,
          interests: userInterests
        }
        
        // Generate a random anonymous name
        const adjectives = ['Happy', 'Clever', 'Brave', 'Wise', 'Kind', 'Swift', 'Bright', 'Noble']
        const animals = ['Tiger', 'Eagle', 'Dolphin', 'Fox', 'Owl', 'Lion', 'Hawk', 'Wolf']
        const anonymousName = `${adjectives[Math.floor(Math.random() * adjectives.length)]} ${animals[Math.floor(Math.random() * animals.length)]}`
        
        // Login with the user data and anonymous name
        login(userData, anonymousName)
        
        // Navigate to lobby
        navigate('/lobby')
      } else {
        setErrors({ submit: result.message || 'Login failed. Please check your credentials.' })
      }
    } catch (error) {
      console.error('Login error:', error)
      setErrors({ submit: 'Login failed. Please check your connection and try again.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-600 rounded-full">
              <MessageSquare className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">Welcome Back</h2>
          <p className="mt-2 text-gray-600">
            Sign in to join discussions
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-lg shadow-lg">
          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
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
            {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div className="mt-1 relative">
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
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
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
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
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md 
                       shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 
                       focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Signing in...' : 'Sign In'}
          </button>

          {/* Sign Up Link */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link
                to="/signup"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Sign up here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginPage
