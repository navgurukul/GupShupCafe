/**
 * API Service
 * Handles all HTTP requests to the backend API
 */

// Get base URL from environment variables
const getBaseUrl = () => {
  const isProd = import.meta.env.MODE === "production";
  return (
    import.meta.env.VITE_API_URL || (isProd ? "" : "http://localhost:3003")
  );
};

const BASE_URL = getBaseUrl();

/**
 * Generic GET request handler
 * @param {string} endpoint - API endpoint path
 * @param {Object} options - Fetch options
 * @returns {Promise} Response data
 */
export async function get(endpoint, options = {}) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("[API] GET error:", endpoint, error);
    throw error;
  }
}

/**
 * Generic POST request handler
 * @param {string} endpoint - API endpoint path
 * @param {Object} data - Request body data
 * @param {Object} options - Fetch options
 * @returns {Promise} Response data
 */
export async function post(endpoint, data = {}, options = {}) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      body: JSON.stringify(data),
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("[API] POST error:", endpoint, error);
    throw error;
  }
}

/**
 * Fetch available discussion topics
 * @returns {Promise<Array>} List of topics
 */
export async function fetchTopics() {
  try {
    const response = await get("/api/topics");
    return response.topics || [];
  } catch (error) {
    console.error("[API] Error fetching topics:", error);
    // Return fallback topics
    return [
      { id: 1, text: "Technology and Innovation", category: "Technology" },
      { id: 2, text: "Education System", category: "Education" },
      { id: 3, text: "Environmental Issues", category: "Environment" },
      { id: 4, text: "Social Media Impact", category: "Society" },
      { id: 5, text: "Future of Work", category: "Career" },
    ];
  }
}

/**
 * Fetch analytics data for a user
 * @param {string} userId - User identifier
 * @returns {Promise<Object>} Analytics data
 */
export async function fetchAnalytics(userId) {
  try {
    const response = await get(`/api/analytics/${userId}`);
    return response.data || {};
  } catch (error) {
    console.error("[API] Error fetching analytics:", error);
    throw error;
  }
}

/**
 * Create a new room
 * @param {Object} roomConfig - Room configuration
 * @returns {Promise<Object>} Created room data
 */
export async function createRoom(roomConfig) {
  try {
    const response = await post("/api/rooms", roomConfig);
    return response.data || {};
  } catch (error) {
    console.error("[API] Error creating room:", error);
    throw error;
  }
}

/**
 * Fetch active rooms
 * @returns {Promise<Array>} List of active rooms
 */
export async function fetchActiveRooms() {
  try {
    const response = await get("/api/rooms/active");
    return response.rooms || [];
  } catch (error) {
    console.error("[API] Error fetching active rooms:", error);
    return [];
  }
}

/**
 * Fetch waiting rooms (rooms with status 'waiting')
 * @returns {Promise<Array>} List of waiting rooms
 */
export async function fetchWaitingRooms() {
  try {
    const response = await get("/rooms/waiting");
    if (response.status === "success") {
      return response.data || [];
    }
    return [];
  } catch (error) {
    console.error("[API] Error fetching waiting rooms:", error);
    return [];
  }
}

export default {
  get,
  post,
  fetchTopics,
  fetchAnalytics,
  createRoom,
  fetchActiveRooms,
  fetchWaitingRooms,
};
