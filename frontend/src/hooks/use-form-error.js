import { useState } from 'react';

export function useFormError() {
  const [serverError, setServerError] = useState('');

  const handleError = (error, form) => {
    try {
      // Try to parse the error message as JSON
      const errorData = JSON.parse(error.message);
      
      // Handle validation errors from the server
      if (typeof errorData === 'object') {
        // If it's a validation error object, set field errors
        Object.keys(errorData).forEach(field => {
          form?.setError(field, {
            type: 'server',
            message: errorData[field]
          });
        });
      } else {
        // If it's a simple error message
        setServerError(error.message);
      }
    } catch (e) {
      // If error message is not JSON, just set it as server error
      setServerError(error.message || 'An unexpected error occurred');
    }
  };

  return {
    serverError,
    setServerError,
    handleError
  };
} 