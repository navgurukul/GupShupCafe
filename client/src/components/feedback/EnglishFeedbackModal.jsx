import React, { useEffect, useState } from 'react'
import { X, Award, BookOpen, MessageCircle, TrendingUp } from 'lucide-react'

/**
 * EnglishFeedbackModal Component
 * Displays English language feedback for the speaker including CEFR level, 
 * grammar issues, and scores. Auto-dismisses after 10 seconds.
 */
function EnglishFeedbackModal({ feedback, isOpen, onClose }) {
  const [autoCloseTimer, setAutoCloseTimer] = useState(10)

  // Auto-dismiss after 10 seconds
  useEffect(() => {
    if (!isOpen || !feedback) return

    const timer = setInterval(() => {
      setAutoCloseTimer((prev) => {
        if (prev <= 1) {
          onClose()
          return 10
        }
        return prev - 1
      })
    }, 1000)

    return () => {
      clearInterval(timer)
      setAutoCloseTimer(10)
    }
  }, [isOpen, feedback, onClose])

  if (!isOpen || !feedback) return null

  /**
   * Display CEFR level badge with color coding
   */
  const displayCEFRLevel = () => {
    const cefrColors = {
      'A1': 'bg-red-100 text-red-700 border-red-300',
      'A2': 'bg-orange-100 text-orange-700 border-orange-300',
      'B1': 'bg-yellow-100 text-yellow-700 border-yellow-300',
      'B2': 'bg-green-100 text-green-700 border-green-300',
      'C1': 'bg-blue-100 text-blue-700 border-blue-300',
      'C2': 'bg-purple-100 text-purple-700 border-purple-300',
    }

    const level = feedback.cefrLevel || 'B1'
    const colorClass = cefrColors[level] || cefrColors['B1']

    return (
      <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full border-2 ${colorClass}`}>
        <Award className="w-5 h-5" />
        <span className="font-bold text-lg">CEFR Level: {level}</span>
      </div>
    )
  }

  /**
   * Display grammar feedback with corrections
   */
  const displayGrammarFeedback = () => {
    if (!feedback.grammarIssues || feedback.grammarIssues.length === 0) {
      return (
        <p className="text-sm text-green-600">✓ No grammar issues detected!</p>
      )
    }

    return (
      <div className="space-y-2">
        {feedback.grammarIssues.map((issue, index) => (
          <div key={index} className="bg-red-50 border border-red-200 rounded-md p-3">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-gray-700">
                  <span className="line-through text-red-600">{issue.original}</span>
                  {' → '}
                  <span className="text-green-600 font-medium">{issue.corrected}</span>
                </p>
                <p className="text-xs text-gray-500 mt-1">{issue.reason}</p>
              </div>
              {issue.severity && (
                <span className={`text-xs px-2 py-1 rounded ${
                  issue.severity === 'high' ? 'bg-red-200 text-red-800' :
                  issue.severity === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                  'bg-blue-200 text-blue-800'
                }`}>
                  {issue.severity}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  /**
   * Display vocabulary score with visual indicator
   */
  const displayVocabularyScore = () => {
    const score = feedback.vocabularyScore || 0
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Vocabulary</span>
          <span className="text-lg font-bold text-blue-600">{score}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${score}%` }}
          />
        </div>
      </div>
    )
  }

  /**
   * Display fluency score with visual indicator
   */
  const displayFluencyScore = () => {
    const score = feedback.fluencyScore || 0
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Fluency</span>
          <span className="text-lg font-bold text-green-600">{score}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-green-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${score}%` }}
          />
        </div>
      </div>
    )
  }

  /**
   * Close modal handler
   */
  const close = () => {
    setAutoCloseTimer(10)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-slide-up">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <MessageCircle className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">English Feedback</h2>
            <span className="text-sm text-gray-500">(Private - only you can see this)</span>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-500">Auto-closing in {autoCloseTimer}s</span>
            <button
              onClick={close}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close feedback modal"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* CEFR Level Badge */}
          <div className="text-center">
            {displayCEFRLevel()}
            {feedback.displayMessage && (
              <p className="text-sm text-gray-600 mt-2">{feedback.displayMessage}</p>
            )}
          </div>

          {/* Scores Section */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Grammar Score */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <BookOpen className="w-5 h-5 text-purple-600" />
                <span className="font-semibold text-gray-900">Grammar</span>
              </div>
              <div className="text-2xl font-bold text-purple-600">
                {feedback.grammarScore || 0}%
              </div>
            </div>

            {/* Vocabulary Score */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Award className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-gray-900">Vocabulary</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {feedback.vocabularyScore || 0}%
              </div>
            </div>

            {/* Fluency Score */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <span className="font-semibold text-gray-900">Fluency</span>
              </div>
              <div className="text-2xl font-bold text-green-600">
                {feedback.fluencyScore || 0}%
              </div>
            </div>
          </div>

          {/* Grammar Issues */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center space-x-2">
              <BookOpen className="w-5 h-5 text-purple-600" />
              <span>Grammar Feedback</span>
            </h3>
            {displayGrammarFeedback()}
          </div>

          {/* Suggestions */}
          {feedback.suggestions && feedback.suggestions.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">💡 Suggestions</h3>
              <ul className="space-y-1">
                {feedback.suggestions.map((suggestion, index) => (
                  <li key={index} className="text-sm text-blue-800">
                    • {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end">
          <button
            onClick={close}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                     transition-colors font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default EnglishFeedbackModal
