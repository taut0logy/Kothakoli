const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
  // Chat endpoints
  async sendMessage(message, modelName = null) {
    const response = await fetch(`${API_BASE_URL}/api/chat/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ 
        message,
        model_name: modelName 
      }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to send message')
    }
    const data = await response.json()
    return data // Return the actual response data
  },

  async sendVoice(audioBlob, modelName = null) {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'audio.webm')
    if (modelName) {
      formData.append('model_name', modelName)
    }

    const response = await fetch(`${API_BASE_URL}/api/chat/voice`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to process voice')
    }
    const data = await response.json()
    return data.data
  },

  async textToSpeech(text) {
    const response = await fetch(`${API_BASE_URL}/api/chat/text-to-speech`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to convert text to speech');
    }

    // Get the audio data as an ArrayBuffer
    const arrayBuffer = await response.arrayBuffer();
    // Convert ArrayBuffer to Blob with correct MIME type
    return new Blob([arrayBuffer], { type: 'audio/mpeg' });
  },

  // File endpoints
  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/api/files/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to upload file')
    }
    return response.json()
  },

  async processFile(file, modelName = null) {
    const formData = new FormData()
    formData.append('file', file)
    if (modelName) {
      formData.append('model_name', modelName)
    }

    const response = await fetch(`${API_BASE_URL}/api/files/process-file`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to process image')
    }
    return response.json()
  },

  // PDF endpoints
  async generateStory(prompt, modelName = null, isPublic = true) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-story`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        prompt,
        model_name: modelName,
        is_public: isPublic
      })
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to generate story')
    }
    return response.json()
  },

  async downloadPdf(fileId) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/download/${fileId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to download PDF')
    }
    return response.blob()
  },

  async listPdfs() {
    const response = await fetch(`${API_BASE_URL}/api/pdf/files`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to list PDFs')
    }
    return response.json()
  },

  async generateCustomPDF({ content, title, caption, isPublic = true, fontName = "Kalpurush" }) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-custom`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        content,
        title,
        caption,
        is_public: isPublic,
        font_name: fontName
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate PDF');
    }
    
    const result = await response.json();
    return {
      success: result.success,
      data: result.data
    };
  },

  async verifyEmail(token) {
    try {
      const response = await fetch('/api/auth/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });
      
      if (!response.ok) {
        throw new Error('Verification failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error verifying email:', error);
      throw error;
    }
  },

  async deleteContent(contentId) {
    const response = await fetch(`${API_BASE_URL}/api/content/${contentId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete content');
    }
    
    return true;
  },

  async getContents({ contentType = null, page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = {}) {
    const params = new URLSearchParams();
    if (contentType) params.append('content_type', contentType);
    if (page) params.append('page', page.toString());
    if (limit) params.append('limit', limit.toString());
    if (sortBy) params.append('sort_by', sortBy);
    if (sortOrder) params.append('sort_order', sortOrder);

    const queryString = params.toString();
    const response = await fetch(
      `${API_BASE_URL}/api/content${queryString ? `?${queryString}` : ''}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch contents');
    }
    
    const data = await response.json();
    return Array.isArray(data) ? data : [];
  },

  async getUserContents({userId, contentType = null, page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc'}) {
    const params = new URLSearchParams();
    if (contentType) params.append('content_type', contentType);
    if (page) params.append('page', page.toString());
    if (limit) params.append('limit', limit.toString());
    if (sortBy) params.append('sort_by', sortBy);
    if (sortOrder) params.append('sort_order', sortOrder);

    const queryString = params.toString();
    const response = await fetch(
      `${API_BASE_URL}/api/content/${userId}${queryString ? `?${queryString}` : ''}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch contents');
    }
    
    const data = await response.json();
    return Array.isArray(data) ? data : [];
  },

  async getUserPdfs({userId, page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc'}) {
    const params = new URLSearchParams();
    if (page) params.append('page', page.toString());
    if (limit) params.append('limit', limit.toString());
    if (sortBy) params.append('sort_by', sortBy);
    if (sortOrder) params.append('sort_order', sortOrder);

    const queryString = params.toString();
    const response = await fetch(
      `${API_BASE_URL}/api/content/${userId}/pdfs${queryString ? `?${queryString}` : ''}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch contents');
    }
    
    const data = await response.json();
    return Array.isArray(data) ? data : [];
  },

  // Search endpoints
  async searchUsers(query, page = 1, limit = 10) {
    const response = await fetch(
      `${API_BASE_URL}/api/search/users?query=${encodeURIComponent(query)}&page=${page}&limit=${limit}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to search users');
    }
    return response.json();
  },

  async searchPdfs(query, page = 1, limit = 10) {
    const response = await fetch(
      `${API_BASE_URL}/api/search/pdfs?query=${encodeURIComponent(query)}&page=${page}&limit=${limit}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to search PDFs');
    }
    return response.json();
  },

  

  async getAllUsers(page = 1, limit = 10) {
    const response = await fetch(
      `${API_BASE_URL}/api/admin/users?page=${page}&limit=${limit}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get users');
    }
    return response.json();
  },

  async convertToBengali(text) {
    const response = await fetch(`${API_BASE_URL}/api/convert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ text }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to convert text');
    }
    
    return response.json();
  },

  async generateTitleCaption(text) {
    const response = await fetch(`${API_BASE_URL}/api/convert/generate-title-caption`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ text }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate title and caption');
    }
    
    return response.json();
  }
} 