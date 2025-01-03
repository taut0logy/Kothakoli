import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function DELETE(request, { params }) {
  const { contentId } = params;
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/content/${contentId}`, {
      method: 'DELETE',
      headers: {
        ...Object.fromEntries(request.headers),
        'host': new URL(BACKEND_URL).host,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to delete content');
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting content:', error);
    return NextResponse.json(
      { error: 'Failed to delete content' },
      { status: 500 }
    );
  }
} 