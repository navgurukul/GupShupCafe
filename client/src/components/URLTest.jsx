import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const URLTest = () => {
  const location = useLocation();

  useEffect(() => {
    console.log('=== URL TEST COMPONENT ===');
    console.log('window.location.href:', window.location.href);
    console.log('window.location.search:', window.location.search);
    console.log('React Router location.search:', location.search);
    console.log('location.pathname:', location.pathname);
    
    // Test direct URL parsing
    try {
      const url = new URL(window.location.href);
      console.log('Direct URL params:', Object.fromEntries(url.searchParams.entries()));
    } catch (e) {
      console.log('URL parsing error:', e.message);
    }
    
    // Test URLSearchParams with different sources
    const windowParams = new URLSearchParams(window.location.search);
    const routerParams = new URLSearchParams(location.search);
    
    console.log('Window URLSearchParams:', Object.fromEntries(windowParams.entries()));
    console.log('Router URLSearchParams:', Object.fromEntries(routerParams.entries()));
    console.log('=== END URL TEST ===');
  }, [location]);

  return (
    <div style={{ padding: '20px', background: '#f0f0f0', margin: '20px' }}>
      <h3>URL Test Component</h3>
      <p>Current URL: {window.location.href}</p>
      <p>Search params: {window.location.search}</p>
      <p>Pathname: {location.pathname}</p>
    </div>
  );
};

export default URLTest;