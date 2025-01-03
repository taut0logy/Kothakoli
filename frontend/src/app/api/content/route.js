import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    const url = `${BACKEND_URL}/api/content${queryString ? `?${queryString}` : ''}`;

    const response = await fetch(url, {
      headers: {
        ...Object.fromEntries(request.headers),
        'host': new URL(BACKEND_URL).host,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch contents');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching contents:', error);
    return NextResponse.json(
      { error: 'Failed to fetch contents' },
      { status: 500 }
    );
  }
}

export async function DELETE(request) {
  const url = `${BACKEND_URL}/api/content`;

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