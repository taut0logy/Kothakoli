import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request) {
  let response = null;
  try {
    const pathname = new URL(request.url).pathname;
    const routeSegments = pathname
      .split('/')
      .filter(segment => segment && segment !== 'api' && segment !== 'auth');
    
    const route = routeSegments.join('/');
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    const url = `${BACKEND_URL}/api/auth/${route}${queryString ? `?${queryString}` : ''}`;

    response = await fetch(url, {
      headers: {
        ...Object.fromEntries(request.headers),
        'host': new URL(BACKEND_URL).host,
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch from backend' },
      { status: 500 }
    );
  } finally {
    // Ensure response is properly closed
    if (response && !response.bodyUsed) {
      await response.body?.cancel();
    }
  }
}

export async function POST(request) {
  let response = null;
  try {
    const pathname = new URL(request.url).pathname;
    const routeSegments = pathname
      .split('/')
      .filter(segment => segment && segment !== 'api' && segment !== 'auth');
    
    const routePath = routeSegments.join('/');
    const firstRoute = routeSegments[0];

    if (firstRoute === 'verify-email') {
      const { token } = await request.json();
      
      response = await fetch(`${BACKEND_URL}/api/auth/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error('Verification failed');
      }

      return NextResponse.json(data);
    }

    const url = `${BACKEND_URL}/api/auth/${routePath}`;
    
    const contentType = request.headers.get('content-type');
    let body;
    let headers = {
      ...Object.fromEntries(request.headers),
      'host': new URL(BACKEND_URL).host,
    };

    if (contentType?.includes('application/json')) {
      body = await request.json();
      headers['content-type'] = 'application/json';
    } else if (contentType?.includes('application/x-www-form-urlencoded')) {
      const formData = await request.formData();
      body = new URLSearchParams(formData);
      headers['content-type'] = 'application/x-www-form-urlencoded';
    } else {
      body = await request.text();
    }

    response = await fetch(url, {
      method: 'POST',
      headers,
      body: typeof body === 'string' ? body : JSON.stringify(body),
    });

    const data = await response.json();
    
    // Create the response with the data
    const nextResponse = NextResponse.json(data, { status: response.status });
    
    // If login was successful, set the cookie
    if (routePath === 'login' && response.ok && data.access_token) {
      nextResponse.cookies.set('token', data.access_token, {
        path: '/',
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax'
      });
    }
    
    return nextResponse;
  } catch (error) {
    console.error('Route handler error:', error);
    return NextResponse.json(
      { error: 'Backend fetch error: ' + error.message },
      { status: 500 }
    );
  } finally {
    // Ensure response is properly closed
    if (response && !response.bodyUsed) {
      await response.body?.cancel();
    }
  }
}

export async function PUT(request, { params }) {
  const route = params.route.join('/');
  const url = `${BACKEND_URL}/api/auth/${route}`;

  try {
    const body = await request.json();
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...Object.fromEntries(request.headers),
        'host': new URL(BACKEND_URL).host,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: 'Failed to fetch from backend' },
      { status: 500 }
    );
  }
}

export async function DELETE(request, { params }) {
  const route = params.route.join('/');
  const url = `${BACKEND_URL}/api/auth/${route}`;

  try {
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        ...Object.fromEntries(request.headers),
        'host': new URL(BACKEND_URL).host,
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: 'Failed to fetch from backend' },
      { status: 500 }
    );
  }
} 