/**
 * @typedef {Object} Issue
 * @property {string} original - Original text with error
 * @property {string} corrected - Corrected text
 * @property {string} reason - Explanation of the correction
 * @property {string} severity - Error severity ('high', 'medium', 'low')
 */

/**
 * @typedef {Object} Feedback
 * @property {string} feedbackType - Type of feedback ('grammar', 'vocabulary', 'fluency', 'comprehensive')
 * @property {number} grammarScore - Grammar score (0-100)
 * @property {number} vocabularyScore - Vocabulary richness score (0-100)
 * @property {number} fluencyScore - Fluency score (0-100)
 * @property {string} cefrLevel - Assessed CEFR level (A1, A2, B1, B2, C1, C2)
 * @property {Issue[]} grammarIssues - List of grammar issues found
 * @property {string[]} suggestions - List of improvement suggestions
 * @property {string} displayMessage - Summary message to display
 */

/**
 * Feedback type definitions for English language assessment
 */
export const FeedbackType = {}
export const IssueType = {}
